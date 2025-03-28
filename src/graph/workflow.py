
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from src.state.state import GraphState, APPROVED_PHRASES, MAX_ITERATIONS
from src.nodes.common import with_live_callback
from src.nodes.workflow_nodes import (
    get_user_requirements_node,
    generate_user_stories_node,
    po_review_stories_node,
    create_design_doc_node,
    design_doc_review_node,
    coder_node,
    code_reviewer_node,
    security_review_node,
    write_test_cases_node,
    test_case_review_node,
    qa_testing_node,
    deployment_node,
    monitoring_feedback_node,
    maintenance_updates_node
)
import logging

logger = logging.getLogger(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def build_workflow_graph(live_callback=None):
    """Build and return the workflow graph"""

    builder = StateGraph(GraphState)

    # Add nodes
    # builder.add_node("get_user_requirements", get_user_requirements_node)
    builder.add_node("get_user_requirements", with_live_callback(
        get_user_requirements_node, live_callback))
    # builder.add_node("generate_user_stories", generate_user_stories_node)
    builder.add_node("generate_user_stories", with_live_callback(
        generate_user_stories_node, live_callback))
    # builder.add_node("po_review_stories", po_review_stories_node)
    builder.add_node("po_review_stories", with_live_callback(
        po_review_stories_node, live_callback))
    # builder.add_node("create_design_doc", create_design_doc_node)
    builder.add_node("create_design_doc", with_live_callback(
        create_design_doc_node, live_callback))
    # builder.add_node("design_doc_review", design_doc_review_node)
    builder.add_node("design_doc_review", with_live_callback(
        design_doc_review_node, live_callback))
    # builder.add_node("coder", coder_node)
    builder.add_node("coder", with_live_callback(
        coder_node, live_callback))
    # builder.add_node("code_reviewer", code_reviewer_node)
    builder.add_node("code_reviewer", with_live_callback(
        code_reviewer_node, live_callback))
    # builder.add_node("security_review", security_review_node)
    builder.add_node("security_review", with_live_callback(
        security_review_node, live_callback))
    # builder.add_node("write_test_cases", write_test_cases_node)
    builder.add_node("write_test_cases", with_live_callback(
        write_test_cases_node, live_callback))
    # builder.add_node("test_case_review", test_case_review_node)
    builder.add_node("test_case_review", with_live_callback(
        test_case_review_node, live_callback))
    # builder.add_node("qa_testing", qa_testing_node)
    builder.add_node("qa_testing", with_live_callback(
        qa_testing_node, live_callback))
    # builder.add_node("fix_code_after_qa", fix_code_after_qa_node)
    # builder.add_node("deployment", deployment_node)
    builder.add_node("deployment", with_live_callback(
        deployment_node, live_callback))
    # builder.add_node("monitoring_feedback", monitoring_feedback_node)
    builder.add_node("monitoring_feedback", with_live_callback(
        monitoring_feedback_node, live_callback))
    # builder.add_node("maintenance_updates", maintenance_updates_node)
    builder.add_node("maintenance_updates", with_live_callback(
        maintenance_updates_node, live_callback))

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
            print("QA Testing Passed")
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
