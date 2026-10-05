from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, get_buffer_string
from app.graph.state import InterviewState, SearchQuery
from app.services.llm import get_llm
from app.tools.search import search_tavily, search_wikipedia_docs

question_instructions = """You are an analyst tasked with interviewing an expert to learn about a specific topic. 

Your goal is boil down to interesting and specific insights related to your topic.

1. Interesting: Insights that people will find surprising or non-obvious.
        
2. Specific: Insights that avoid generalities and include specific examples from the expert.

Here is your topic of focus and set of goals: {goals}
        
Begin by introducing yourself using a name that fits your persona, and then ask your question.

Continue to ask questions to drill down and refine your understanding of the topic.
        
When you are satisfied with your understanding, complete the interview with: "Thank you so much for your help!"

Remember to stay in character throughout your response, reflecting the persona and goals provided to you."""

search_instructions = SystemMessage(
    content="""You will be given a conversation between an analyst and an expert. 

Your goal is to generate a well-structured query for use in retrieval and / or web-search related to the conversation.
        
First, analyze the full conversation.

Pay particular attention to the final question posed by the analyst.

Convert this final question into a well-structured web search query"""
)

answer_instructions = """You are an expert being interviewed by an analyst.

Here is analyst area of focus: {goals}. 
        
You goal is to answer a question posed by the interviewer.

To answer question, use this context:
        
{context}

When answering questions, follow these guidelines:
        
1. Use only the information provided in the context. 
        
2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.

3. The context contain sources at the topic of each individual document.

4. Include these sources your answer next to any relevant statements. For example, for source # 1 use [1]. 

5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc
        
6. If the source is: <Document source="assistant/docs/llama3_1.pdf" page="7"/>' then just list: 
        
[1] assistant/docs/llama3_1.pdf, page 7 
        
And skip the addition of the brackets as well as the Document source preamble in your citation."""


def generate_question(state: InterviewState):
    """Generate interview question staying in character as the assigned analyst."""
    analyst = state["analyst"]
    messages = state["messages"]

    llm = get_llm()
    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)] + messages)

    return {"messages": [question]}


def search_web(state: InterviewState):
    """Generate search query and retrieve docs from web search (Tavily)."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions] + state["messages"])

    formatted_docs = search_tavily(search_query.search_query, max_results=3)
    return {"context": [formatted_docs] if formatted_docs else []}


def search_wikipedia(state: InterviewState):
    """Generate search query and retrieve docs from Wikipedia."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions] + state["messages"])

    formatted_docs = search_wikipedia_docs(search_query.search_query, max_docs=2)
    return {"context": [formatted_docs] if formatted_docs else []}


def generate_answer(state: InterviewState):
    """Generate expert answer based strictly on retrieved context documents."""
    analyst = state["analyst"]
    messages = state["messages"]
    context = state.get("context", [])

    llm = get_llm()
    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=system_message)] + messages)
    answer.name = "expert"

    return {"messages": [answer]}


def save_interview(state: InterviewState):
    """Serialize the completed interview messages."""
    messages = state["messages"]
    interview = get_buffer_string(messages)
    return {"interview": interview}


def route_messages(state: InterviewState, name: str = "expert"):
    """Route between continuing the interview or saving the transcript."""
    messages = state["messages"]
    max_num_turns = state.get("max_num_turns", 2)

    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and getattr(m, "name", None) == name]
    )

    if num_responses >= max_num_turns:
        return "save_interview"

    if len(messages) >= 2:
        last_question = messages[-2]
        if "Thank you so much for your help" in str(last_question.content):
            return "save_interview"

    return "ask_question"
