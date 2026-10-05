import operator
from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class Analyst(BaseModel):
    """Analyst persona representing a research perspective."""
    affiliation: str = Field(description="Primary affiliation of the analyst.")
    name: str = Field(description="Name of the analyst.")
    role: str = Field(description="Role of the analyst in the context of the topic.")
    description: str = Field(description="Description of the analyst focus, concerns, and motives.")

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"


class Perspectives(BaseModel):
    """Collection of analyst personas."""
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations."
    )


class SearchQuery(BaseModel):
    """Structured query for web or Wikipedia retrieval."""
    search_query: str = Field(None, description="Search query for retrieval.")


class GenerateAnalystsState(TypedDict):
    """State for generating analyst personas."""
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]


class InterviewState(MessagesState):
    """State for sub-graph conducting an interview."""
    max_num_turns: int
    context: Annotated[list, operator.add]
    analyst: Analyst
    interview: str
    sections: list


class ResearchGraphState(TypedDict):
    """Outer state for full multi-analyst research graph."""
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
    sections: Annotated[list, operator.add]
    introduction: str
    content: str
    conclusion: str
    final_report: str
