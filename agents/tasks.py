# Re-exports for backward compatibility. Tasks live in their respective agent files.
from agents.ceo_agent import make_decompose_task, make_review_task, make_final_summary_task
from agents.product_agent import make_product_task
from agents.engineer_agent import make_html_task, make_pr_meta_task
from agents.marketing_agent import make_marketing_task
from agents.qa_agent import make_qa_task

__all__ = [
    "make_decompose_task",
    "make_review_task",
    "make_final_summary_task",
    "make_product_task",
    "make_html_task",
    "make_pr_meta_task",
    "make_marketing_task",
    "make_qa_task",
]
