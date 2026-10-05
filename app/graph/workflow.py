import logging
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from langgraph.types import Send
from langgraph.graph import END, START, StateGraph

from app.graph.state import (
    InterviewState,
    ResearchGraphState,
    GenerateAnalystsState,
    Analyst,
)
from app.agents.planner import create_analysts
from app.agents.interviewer import (
    generate_question,
    search_web,
    search_wikipedia,
    generate_answer,
    save_interview,
    route_messages,
)
from app.agents.writer import (
    write_section,
    write_report,
    write_introduction,
    write_conclusion,
    finalize_report,
)

logger = logging.getLogger(__name__)


def build_interview_graph():
    """Build and compile the sub-graph for conducting an analyst interview."""
    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node("ask_question", generate_question)
    interview_builder.add_node("search_web", search_web)
    interview_builder.add_node("search_wikipedia", search_wikipedia)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    interview_builder.add_edge(START, "ask_question")
    interview_builder.add_edge("ask_question", "search_web")
    interview_builder.add_edge("ask_question", "search_wikipedia")
    interview_builder.add_edge("search_web", "answer_question")
    interview_builder.add_edge("search_wikipedia", "answer_question")
    interview_builder.add_conditional_edges(
        "answer_question", route_messages, ["ask_question", "save_interview"]
    )
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)

    return interview_builder.compile()


def initiate_all_interviews(state: ResearchGraphState):
    """
    Conditional edge router:
    If human feedback is not 'approve', loop back to create_analysts.
    Otherwise kick off parallel interviews for each analyst persona via Send() API.
    """
    human_analyst_feedback = state.get("human_analyst_feedback", "approve")
    if human_analyst_feedback and human_analyst_feedback.lower() != "approve":
        return "create_analysts"

    topic = state["topic"]
    return [
        Send(
            "conduct_interview",
            {
                "analyst": analyst,
                "messages": [
                    HumanMessage(
                        content=f"So you said you were writing an article on {topic}?"
                    )
                ],
                "max_num_turns": state.get("max_num_turns", 2),
            },
        )
        for analyst in state.get("analysts", [])
    ]


def human_feedback_node(state: ResearchGraphState):
    """Pass-through node representing editorial feedback."""
    return {}


def build_research_graph(with_interrupt: bool = False):
    """Build and compile the main multi-analyst research graph."""
    compiled_interview = build_interview_graph()

    builder = StateGraph(ResearchGraphState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback_node)
    builder.add_node("conduct_interview", compiled_interview)
    builder.add_node("write_report", write_report)
    builder.add_node("write_introduction", write_introduction)
    builder.add_node("write_conclusion", write_conclusion)
    builder.add_node("finalize_report", finalize_report)

    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")
    builder.add_conditional_edges(
        "human_feedback",
        initiate_all_interviews,
        ["create_analysts", "conduct_interview"],
    )
    builder.add_edge("conduct_interview", "write_report")
    builder.add_edge("conduct_interview", "write_introduction")
    builder.add_edge("conduct_interview", "write_conclusion")
    builder.add_edge(
        ["write_conclusion", "write_report", "write_introduction"], "finalize_report"
    )
    builder.add_edge("finalize_report", END)

    interrupt_nodes = ["human_feedback"] if with_interrupt else []
    return builder.compile(interrupt_before=interrupt_nodes)
