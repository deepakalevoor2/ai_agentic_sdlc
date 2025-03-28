
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.graph.workflow import build_workflow_graph
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_workflow(live_callback=None) -> Dict:
    initial_state = {
        "user_requirement": "",
        "generated_user_stories": "",
        "po_review_comment": "",
        "stories_correction_iteration": 0,
        "design_doc_review_iteration": 0,
        "design_doc": "",
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
        "messages": [HumanMessage(content="Getting requirements from file")]
    }

    graph = build_workflow_graph(live_callback=live_callback)

    def recursive_hook(state):
        if live_callback:
            live_callback(state.get("messages", []))

    result = graph.invoke(initial_state, {
        "recursion_limit": 100,
        "recursion_hook": recursive_hook
    })
    return result


if __name__ == "__main__":
    final_output = run_workflow()
    for key, value in final_output.items():
        print(f"\n=== {key.upper()} ===\n{value}\n")
