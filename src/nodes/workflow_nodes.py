
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.llms.factory import get_llm
from src.nodes.common import timer, read_file, extract_content_after_pattern
from src.state.state import GraphState, APPROVED_PHRASES, MAX_ITERATIONS
from langgraph.graph import StateGraph, START, END
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_user_requirements_node(state: GraphState) -> GraphState:
    """Node that retrieves user requirements from file"""

    logger.info("Getting user requirements...")

    with timer("Reading requirements file"):
        user_requirements = read_file("req_build.md", "No requirements found")

    return {"user_requirement": user_requirements}


def generate_user_stories_node(state: GraphState) -> GraphState:
    """Node that generates user stories based on requirements"""

    current_state = state
    user_requirements = current_state['user_requirement']
    po_review_comment = current_state.get('po_review_comment', '')
    stories_correction_iteration = current_state.get(
        'stories_correction_iteration', 0)

    logger.info(
        f"Generating user stories (iteration {stories_correction_iteration + 1})...")

    messages = [
        SystemMessage(content="You are an expert Product Manager. Your job is to create well-structured user stories for the given requirement for the developers to implement and return the response as Python list. If feedback is provided, modify the stories based on the feedback."),
        HumanMessage(
            content=f"Generate list of user stories for requirement {user_requirements} or if feedbacks are provided on user stories in {po_review_comment}, modify them based on the feedbacks. Each user story should have a title, description, acceptance criteria, priority and status")
    ]

    with timer("User stories generation"):
        llm = get_llm("groq", "deepseek-r1-distill-llama-70b")
        response = llm.invoke(messages)
        user_stories = response.content.strip()
        user_stories = extract_content_after_pattern(user_stories)

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Product Manager. Here are the Generated User Stories: {user_stories}")
    ]

    return {
        "user_requirement": state["user_requirement"],
        "generated_user_stories": user_stories,
        "stories_correction_iteration": stories_correction_iteration + 1,
        "po_review_comment": current_state.get("po_review_comment", ""),
        "design_doc_review_iteration": current_state.get("design_doc_review_iteration", 0),
        "design_doc": current_state.get("design_doc", ""),
        "design_doc_review_comments": current_state.get("design_doc_review_comments", ""),
        "messages": new_messages
    }


def po_review_stories_node(state: GraphState) -> GraphState:
    """Node for product owner to review user stories"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]

    logger.info("PO is reviewing user stories...")

    messages = [
        SystemMessage(content="You are a Product Owner. Your job is to provide feedback on User Stories against the given requirement and either approve it or provide feedback. The goal is to build MVP first i.e build product fast and then iterate on it."),
        HumanMessage(content=f"Review the List of User Stories {user_stories} against requirement {user_requirements}. If you approve of all the user stories then mention 'Here is my approval for all user stories' in your review comments else provide feedback on the user stories with the changes required and start your comments with 'Here are the changes required' and don't mention word 'approved' anywhere in your comments.")
    ]

    with timer("PO review"):
        llm = get_llm("groq", "deepseek-r1-distill-qwen-32b")
        response = llm.invoke(messages)
        po_review_comment = response.content.strip()
        po_review_comment = extract_content_after_pattern(po_review_comment)

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Product owner.Here is the Generated Product owner Review comment for user stories: {po_review_comment}")
    ]

    return {
        **state,
        "po_review_comment": po_review_comment,
        "messages": new_messages
    }


def create_design_doc_node(state: GraphState) -> GraphState:
    """Node to create functional and technical design documents"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]
    design_doc_review_iteration = state.get("design_doc_review_iteration", 0)
    design_doc_review_comments = state.get("design_doc_review_comments", "")

    logger.info(
        f"Generating design documents (iteration {design_doc_review_iteration + 1})...")

    messages = [
        SystemMessage(content="You are a Software Architect with strong business analysis skills. Your job is to create comprehensive Functional and Technical design documents of great quality against given requirement and user stories."),
        HumanMessage(
            content=f"Create Functional and Technical design documents based on {user_stories} against requirement {user_requirements}. If feedback is present in {design_doc_review_comments} modify the document accordingly. The goal is to build MVP first i.e build product fast and then iterate on it. Return document in markdown format.")
    ]

    with timer("Design document creation"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        design_doc = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Software Architect and creating Functional and Technical design doc.Here is the generated functional and technical design doc: {design_doc}")
    ]

    return {
        **state,
        "design_doc": design_doc,
        "design_doc_review_iteration": design_doc_review_iteration + 1,
        "messages": new_messages
    }


def design_doc_review_node(state: GraphState) -> GraphState:
    """Node for reviewing design documents"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]
    design_doc = state["design_doc"]

    logger.info("Reviewing design documents...")

    messages = [
        SystemMessage(content="You are a Software Architect. Your job is to review Functional and Technical design documents against given requirement and user stories. Don't nitpick and be liberal while providing feedback."),
        HumanMessage(content=f"Review the Functional and Technical design documents {design_doc} based on {user_stories} and requirement {user_requirements}. If you are happy with the documents, mention 'Go ahead, Here is my approval for the design documents' or else provide feedback on the documents and start your comments with 'Here are the changes required' and don't mention word 'approved' anywhere in your comments.")
    ]

    with timer("Design document review"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        design_doc_review_comments = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Software Architect and reviewing Functional and Technical design doc.Here is the generated Functional and technical design doc review comments: {design_doc_review_comments}")
    ]

    return {
        **state,
        "design_doc_review_comments": design_doc_review_comments,
        "messages": new_messages
    }


def coder_node(state: GraphState) -> GraphState:
    """Node that generates code based on requirements and design"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]
    design_doc = state["design_doc"]
    code_review_comments = state.get("code_review_comments", "")
    security_review_comments = state.get("security_review_comments", "")
    code_review_iteration = state.get("code_review_iteration", 0)
    qa_testing_result = state.get("qa_testing_result", "")

    logger.info(f"Generating code (iteration {code_review_iteration + 1})...")

    messages = [
        SystemMessage(content="You are an expert python coder. Your job is to create python code for the given requirement, user stories and design document that will accurately implement the functionality. If peer review comments or security review feedbacks are provided, implement those changes to code accordingly."),
        HumanMessage(
            content=f"Generate the python code as per the requirement: {user_requirements}, user stories: {user_stories}, Functional and Technical Design: {design_doc}. If peer comments are provided in {code_review_comments} or security review aspect of code is present in {security_review_comments}, implement those changes too in the code.If QA testing is failed as per {qa_testing_result} fix the code.")
    ]

    with timer("Code generation"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        generated_code = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as python coder and generating code. Here is the Generated Code: {generated_code}")
    ]

    return {
        **state,
        "generated_code": generated_code,
        "code_review_iteration": code_review_iteration + 1,
        "messages": new_messages
    }


def code_reviewer_node(state: GraphState) -> GraphState:
    """Node for reviewing generated code"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]
    design_doc = state["design_doc"]
    generated_code = state["generated_code"]

    logger.info("Reviewing code...")

    messages = [
        SystemMessage(content="You are a code reviewer. Your job is to review the code against the given requirement, stories and design doc and check if it implements all the functionalities and covers all scenarios. Return 'no additional review comments' if you find the code is good enough."),
        HumanMessage(content=f"Peer review the code {generated_code} against the requirement: {user_requirements}, user stories: {user_stories}, Functional and Technical Design: {design_doc} and provide your review comments on the code. Don't nitpick while providing your review comments. Return 'no additional review comments' if you find the code is good enough.")
    ]

    with timer("Code review"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        code_review_comments = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as code reviewer.Here is the Generated code review comments: {code_review_comments}")
    ]

    return {
        **state,
        "code_review_comments": code_review_comments,
        "messages": new_messages
    }


def security_review_node(state: GraphState) -> GraphState:
    """Node for security review of code"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]
    design_doc = state["design_doc"]
    generated_code = state["generated_code"]
    security_review_iteration = state.get("security_review_iteration", 0)

    logger.info(
        f"Performing security review (iteration {security_review_iteration + 1})...")

    messages = [
        SystemMessage(content="You are a Software Security Engineer. Your job is to review the security aspects of code against the given requirement, stories and design doc and provide security review feedback. Return 'no additional security review comments' if you find the code is good enough regarding security."),
        HumanMessage(content=f"Do the security review of the code {generated_code} against the requirement: {user_requirements}, user stories: {user_stories}, Functional and Technical Design: {design_doc} and provide your feedback on the code regarding security. Don't nitpick while providing your feedback. Return 'no additional security review comments' if you find the code is good enough.")
    ]

    with timer("Security review"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        security_review_comments = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Security Engineer and performing security review.Here is the Generated security review comments: {security_review_comments}")
    ]

    return {
        **state,
        "security_review_comments": security_review_comments,
        "security_review_iteration": security_review_iteration + 1,
        "messages": new_messages
    }


def write_test_cases_node(state: GraphState) -> GraphState:
    """Node for writing test cases"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]
    design_doc = state["design_doc"]
    security_review_comments = state.get("security_review_comments", "")
    test_case_review_comments = state.get("test_case_review_comments", "")
    test_case_review_iteration = state.get("test_case_review_iteration", 0)

    logger.info(
        f"Generating test cases (iteration {test_case_review_iteration + 1})...")

    messages = [
        SystemMessage(content="You are a Software Development Engineer in Test (SDET). Your job is to write test cases against the given requirement, stories, design doc and security review comments."),
        HumanMessage(
            content=f"Write test cases against the requirement: {user_requirements}, user stories: {user_stories}, Functional and Technical Design: {design_doc}, Security Review comments: {security_review_comments}. If you find feedback in {test_case_review_comments}, modify test cases accordingly.")
    ]

    with timer("Test case generation"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        generated_test_cases = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Software Development Engineer in Test (SDET) and creating test cases. Here are the generated test cases: {generated_test_cases}")
    ]

    return {
        **state,
        "generated_test_cases": generated_test_cases,
        "test_case_review_iteration": test_case_review_iteration + 1,
        "messages": new_messages
    }


def test_case_review_node(state: GraphState) -> GraphState:
    """Node for reviewing test cases"""

    user_requirements = state["user_requirement"]
    user_stories = state["generated_user_stories"]
    design_doc = state["design_doc"]
    generated_test_cases = state["generated_test_cases"]
    security_review_comments = state.get("security_review_comments", "")

    logger.info("Reviewing test cases...")

    messages = [
        SystemMessage(content="You are a QA Lead/Manager. Your job is to review test cases against the given requirement, stories, design doc and security review comments and provide feedback. Return 'no additional test case review comments' if you find the test cases coverage are good enough."),
        HumanMessage(content=f"Review test cases: {generated_test_cases} against the requirement: {user_requirements}, user stories: {user_stories}, Functional and Technical Design: {design_doc}, Security Review comments: {security_review_comments} and provide feedback. Don't nitpick while providing your feedback. Return 'no additional test case review comments' if you find the test cases coverage are good enough.")
    ]

    with timer("Test case review"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        test_case_review_comments = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as QA Lead/Manager and reviewing test cases. Here are the test case review comments: {test_case_review_comments}")
    ]

    return {
        **state,
        "test_case_review_comments": test_case_review_comments,
        "messages": new_messages
    }


def qa_testing_node(state: GraphState) -> GraphState:
    """Node for QA testing based on test cases and code"""

    user_requirements = state["user_requirement"]
    generated_code = state["generated_code"]
    generated_test_cases = state["generated_test_cases"]
    qa_testing_iteration = state["qa_testing_iteration"]

    logger.info(
        f"Running QA testing (iteration {qa_testing_iteration + 1} )...")

    messages = [
        SystemMessage(content="You are a QA Engineer. Your job is to execute the test cases against the code and determine if it passes all tests. Evaluate thoroughly if the code successfully implements all the required functionality."),
        HumanMessage(content=f"Execute the test cases: {generated_test_cases} against the code: {generated_code} and requirement: {user_requirements}. If all tests pass or have only minor issues, respond with 'QA Testing Passed' at the beginning of your analysis. If there are significant issues that need fixing, respond with 'QA Testing Failed' at the beginning and list the specific issues that need to be addressed.")
    ]

    with timer("QA testing"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        qa_testing_result = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as QA Engineer and executing test cases. Here are the QA Testing Results: {qa_testing_result}")
    ]

    return {
        **state,
        "qa_testing_result": qa_testing_result,
        "messages": new_messages
    }


# def fix_code_after_qa_node(state: GraphState) -> GraphState:
#     """Node for fixing code based on QA testing feedback"""

#     user_requirements = state["user_requirement"]
#     generated_code = state["generated_code"]
#     qa_testing_result = state["qa_testing_result"]

#     logger.info("Fixing code after QA testing...")

#     messages = [
#         SystemMessage(
#             content="You are an expert python developer. Your job is to fix the code based on QA testing feedback."),
#         HumanMessage(
#             content=f"Fix the following code based on QA testing feedback:\n\nCode: {generated_code}\n\nQA Testing Result: {qa_testing_result}\n\nRequirement: {user_requirements}\n\nPlease provide the complete fixed code.")
#     ]

#     with timer("Code fixing"):
#         llm = get_llm("google", "gemini-2.0-flash")
#         response = llm.invoke(messages)
#         fixed_code = response.content.strip()

#     # Update state
#     new_messages = state.get("messages", []) + messages + [
#         AIMessage(content=f"Fixed Code After QA: {fixed_code}")
#     ]

#     return {
#         **state,
#         "generated_code": fixed_code,  # Update the code with fixed version
#         "messages": new_messages
#     }


def deployment_node(state: GraphState) -> GraphState:
    """Node for creating deployment plan"""

    user_requirements = state["user_requirement"]
    generated_code = state["generated_code"]

    logger.info("Preparing deployment plan...")

    messages = [
        SystemMessage(content="You are a DevOps Engineer. Your job is to create a deployment plan for the code including any necessary infrastructure configuration, environment setup, and monitoring configuration."),
        HumanMessage(
            content=f"Create a deployment plan for the following code:\n\nCode: {generated_code}\n\nRequirement: {user_requirements}\n\nInclude details on environment setup, configuration files, deployment steps, and any monitoring that should be set up.")
    ]

    with timer("Deployment planning"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        deployment_plan = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as DevOps Engineer and creating deployment plan. Here is the Deployment Plan: {deployment_plan}")
    ]

    return {
        **state,
        "deployment_plan": deployment_plan,
        "messages": new_messages
    }


def monitoring_feedback_node(state: GraphState) -> GraphState:
    """Node for setting up monitoring and feedback collection"""

    user_requirements = state["user_requirement"]
    generated_code = state["generated_code"]
    deployment_plan = state["deployment_plan"]

    logger.info("Setting up monitoring and feedback collection...")

    messages = [
        SystemMessage(content="You are a Site Reliability Engineer (SRE). Your job is to design monitoring systems and feedback collection mechanisms for the deployed application."),
        HumanMessage(
            content=f"Design monitoring systems and feedback collection for:\n\nCode: {generated_code}\n\nDeployment Plan: {deployment_plan}\n\nRequirement: {user_requirements}\n\nInclude details on metrics to track, alerting thresholds, logging strategies, and user feedback collection methods.")
    ]

    with timer("Monitoring setup"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        monitoring_plan = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Site Reliability Engineer (SRE) and creating Design monitoring systems. Here is the Monitoring and Feedback Plan: {monitoring_plan}")
    ]

    return {
        **state,
        "monitoring_plan": monitoring_plan,
        "messages": new_messages
    }


def maintenance_updates_node(state: GraphState) -> GraphState:
    """Node for creating maintenance and updates plan"""

    user_requirements = state["user_requirement"]
    generated_code = state["generated_code"]
    monitoring_plan = state.get("monitoring_plan", "")

    logger.info("Creating maintenance and updates plan...")

    messages = [
        SystemMessage(content="You are a Software Maintenance Engineer. Your job is to create a maintenance plan for the application including update strategies, technical debt management, and future enhancement roadmap."),
        HumanMessage(
            content=f"Create a maintenance and updates plan for:\n\nCode: {generated_code}\n\nRequirement: {user_requirements}\n\nMonitoring Plan: {monitoring_plan}\n\nInclude strategies for updates, dependency management, performance optimization, and potential future enhancements.")
    ]

    with timer("Maintenance planning"):
        llm = get_llm("google", "gemini-2.0-flash")
        response = llm.invoke(messages)
        maintenance_plan = response.content.strip()

    # Update state
    new_messages = state.get("messages", []) + messages + [
        AIMessage(
            content=f"AI is now acting as Software Maintenance Engineer and creating Maintenance and Updates Plan:,Her it is {maintenance_plan}")
    ]

    return {
        **state,
        "maintenance_plan": maintenance_plan,
        "messages": new_messages
    }


def build_workflow_graph():
    """Build and return the workflow graph"""

    builder = StateGraph(GraphState)

    # Add nodes
    builder.add_node("get_user_requirements", get_user_requirements_node)
    builder.add_node("generate_user_stories", generate_user_stories_node)
    builder.add_node("po_review_stories", po_review_stories_node)
    builder.add_node("create_design_doc", create_design_doc_node)
    builder.add_node("design_doc_review", design_doc_review_node)
    builder.add_node("coder", coder_node)
    builder.add_node("code_reviewer", code_reviewer_node)
    builder.add_node("security_review", security_review_node)
    builder.add_node("write_test_cases", write_test_cases_node)
    builder.add_node("test_case_review", test_case_review_node)
    builder.add_node("qa_testing", qa_testing_node)
    # builder.add_node("fix_code_after_qa", fix_code_after_qa_node)
    builder.add_node("deployment", deployment_node)
    builder.add_node("monitoring_feedback", monitoring_feedback_node)
    builder.add_node("maintenance_updates", maintenance_updates_node)

    # Define conditional edge functions
    def review_condition_stories(state):
        logger.info(
            f"Stories correction iteration: {state.get('stories_correction_iteration', 0)}")
        if APPROVED_PHRASES["user_stories"] in state.get('po_review_comment', '').lower():
            logger.info("User stories approved")
            return "create_design_doc"
        elif state.get('stories_correction_iteration', 0) < MAX_ITERATIONS:
            return "generate_user_stories"
        else:
            logger.warning("Max story iterations reached, proceeding anyway")
            return "create_design_doc"

    def review_condition_design_doc(state):
        logger.info(
            f"Design doc review count: {state.get('design_doc_review_iteration', 0)}")
        if APPROVED_PHRASES["design_doc"] in state.get("design_doc_review_comments", "").lower():
            logger.info("Design document approved")
            return "coder"
        elif state.get('design_doc_review_iteration', 0) < MAX_ITERATIONS:
            return "create_design_doc"
        else:
            logger.warning(
                "Max design doc iterations reached, proceeding anyway")
            return "coder"

    def review_condition_code_review(state):
        logger.info(
            f"Code review iteration: {state.get('code_review_iteration', 0)}")
        if APPROVED_PHRASES["code_review"] in state.get("code_review_comments", "").lower():
            logger.info("Code review passed")
            return "security_review"
        elif state.get('code_review_iteration', 0) < MAX_ITERATIONS:
            return "coder"
        else:
            logger.warning(
                "Max code review iterations reached, proceeding anyway")
            return "security_review"

    def review_condition_security_review(state):
        logger.info(
            f"Security review iteration: {state.get('security_review_iteration', 0)}")
        if APPROVED_PHRASES["security_review"] in state.get("security_review_comments", "").lower():
            logger.info("Security review passed")
            return "write_test_cases"
        elif state.get('security_review_iteration', 0) < MAX_ITERATIONS:
            return "coder"
        else:
            logger.warning(
                "Max security review iterations reached, proceeding anyway")
            return "write_test_cases"

    def review_condition_testcase_review(state):
        logger.info(
            f"Test case review iteration: {state.get('test_case_review_iteration', 0)}")
        if APPROVED_PHRASES["test_case_review"] in state.get("test_case_review_comments", "").lower():
            logger.info("Test cases review passed")
            return "qa_testing"
        elif state.get('test_case_review_iteration', 0) < MAX_ITERATIONS:
            return "write_test_cases"
        else:
            logger.warning(
                "Max test case review iterations reached, proceeding anyway")
            return "qa_testing"

    def qa_testing_condition(state):
        logger.info(
            f"QA Testing iteration: {state.get('qa_testing_iteration', 0)}")
        if APPROVED_PHRASES["qa_testing"] in state.get("qa_testing_result", "").lower():
            logger.info("QA Testing Passed")
            return "deployment"
        else:
            print("QA Testing Failed")
            return "coder"

    # Define the edges
    builder.add_edge(START, "get_user_requirements")
    # After getting requirements, generate user stories
    builder.add_edge("get_user_requirements", "generate_user_stories")
    # After Generating User Stories Product owner reviews user stories
    builder.add_edge("generate_user_stories", "po_review_stories")
    # Conditional edge for PO review.If Approved create design doc else revise stories
    builder.add_conditional_edges(
        "po_review_stories",
        review_condition_stories
    )
    # After design document creation, review of design doc
    builder.add_edge("create_design_doc", "design_doc_review")
    # Conditional edge for Design doc review.If Approved proceed to coding else revise design doc
    builder.add_conditional_edges(
        "design_doc_review",
        review_condition_design_doc
    )
    # After coding, peer review of code
    builder.add_edge("coder", "code_reviewer")
    # Conditional edge for Code review.If approved proceed to security review else revise code
    builder.add_conditional_edges(
        "code_reviewer",
        review_condition_code_review
    )
    # Conditional edge for security review.If approved proceed to test case creation else revise code
    builder.add_conditional_edges(
        "security_review",
        review_condition_security_review
    )
    # After test case creation, test case review
    builder.add_edge("write_test_cases", "test_case_review")
    # Conditional edge for test case review. If approved proceed to qa testing else revise test cases
    builder.add_conditional_edges(
        "test_case_review",
        review_condition_testcase_review
    )
    # Conditional edge for QA testing. If passed proceed to deployment else revise code
    builder.add_conditional_edges(
        "qa_testing",
        qa_testing_condition
    )
    # builder.add_edge("fix_code_after_qa", "qa_testing")
    builder.add_edge("deployment", "monitoring_feedback")
    builder.add_edge("monitoring_feedback", "maintenance_updates")
    builder.add_edge("maintenance_updates", END)

    # Build the graph
    react_graph = builder.compile()
    # Show
    # display(Image(react_graph.get_graph().draw_mermaid_png()))

    return react_graph


def run_workflow() -> Dict:
    """
    Run the workflow for given requirement.

    Args:
        Requirement: The functionality that needs to be implemented

    Returns:
        Dict containing the generated code, review comment and doc string
    """
    # Initialize state
    initial_state = {
        "user_requirement": "",
        "generated_user_stories": "",
        "po_review_comment": "",
        "stories_correction_iteration": 0,
        'design_doc_review_iteration': 0,
        'design_doc': "",
        "design_doc_review_comments": "",
        "generated_code": "",
        "code_review_comments": "",
        "code_review_iteration": 0,
        "security_review_comments": "",
        "security_review_iteration": 0,
        "generated_test_cases": "",
        "test_case_review_comments": "",
        "test_case_review_iteration": 0,
        "qa_testing_result": "",
        "qa_testing_iteration": 0,
        "deployment_plan": "",
        "monitoring_plan": "",
        "maintenance_plan": "",
        "messages": [HumanMessage(content=f"Getting requirements from file")]
    }

    # Run the graph
    graph = build_workflow_graph()
    result = graph.invoke(initial_state, {"recursion_limit": 100})

    return {
        "user_requirement": result["user_requirement"],
        "generated_user_stories": result["generated_user_stories"],
        "po_review_comment": result["po_review_comment"],
        "stories_correction_iteration": result["stories_correction_iteration"],
        "design_doc_review_iteration": result["design_doc_review_iteration"],
        'design_doc': result["design_doc"],
        "design_doc_review_comments": result["design_doc_review_comments"],
        "generated_code": result["generated_code"],
        "code_review_comments": result["code_review_comments"],
        "code_review_iteration": result["code_review_iteration"],
        "security_review_comments": result["security_review_comments"],
        "security_review_iteration": result["security_review_iteration"],
        "generated_test_cases": result["generated_test_cases"],
        "test_case_review_comments": result["test_case_review_comments"],
        "test_case_review_iteration": result["test_case_review_iteration"],
        "qa_testing_result": result["qa_testing_result"],
        "qa_testing_iteration": result["qa_testing_iteration"],
        "deployment_plan": result["deployment_plan"],
        "monitoring_plan": result["monitoring_plan"],
        "maintenance_plan": result["maintenance_plan"],
        "messages": result["messages"]
    }


if __name__ == "__main__":
    result = run_workflow()
    print(result)
