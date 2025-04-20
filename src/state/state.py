
from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

MAX_ITERATIONS = 10

APPROVED_PHRASES = {
    "user_stories": "here is my approval for all user stories",
    "design_doc": "go ahead",
    "code_review": "no additional review comments",
    "security_review": "no additional security review comments",
    "test_case_review": "no additional test case review comments",
    "qa_testing": "qa testing passed"
}

class GraphState(TypedDict):
    user_requirement: str
    generated_user_stories: str
    po_review_comment: str
    stories_correction_iteration: int=1
    design_doc: str
    design_doc_review_iteration: int=1
    design_doc_review_comments: str
    generated_code: str
    code_review_comments: str
    code_review_iteration: int=1
    security_review_comments: str
    security_review_iteration: int=1
    generated_test_cases: str
    test_case_review_comments: str
    test_case_review_iteration: int=1
    qa_testing_result: str
    qa_testing_iteration: int=1
    deployment_plan: str
    monitoring_plan: str
    maintenance_plan: str
    messages: List[Union[HumanMessage, SystemMessage, AIMessage]]
