from langchain_core.messages import HumanMessage, SystemMessage
from app.graph.state import GenerateAnalystsState, Perspectives
from app.services.llm import get_llm

analyst_instructions = """You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{topic}
        
2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts: 
        
{human_analyst_feedback}
    
3. Determine the most interesting themes based upon documents and / or feedback above.
                    
4. Pick the top {max_analysts} themes.

5. Assign one analyst to each theme."""


def create_analysts(state: GenerateAnalystsState):
    """Create diverse analyst personas tailored to the research topic."""
    topic = state["topic"]
    max_analysts = state.get("max_analysts", 3)
    human_analyst_feedback = state.get("human_analyst_feedback", "")

    llm = get_llm()
    structured_llm = llm.with_structured_output(Perspectives)

    system_message = analyst_instructions.format(
        topic=topic,
        human_analyst_feedback=human_analyst_feedback,
        max_analysts=max_analysts,
    )

    analysts = structured_llm.invoke(
        [SystemMessage(content=system_message)]
        + [HumanMessage(content="Generate the set of analysts.")]
    )

    return {"analysts": analysts.analysts}
