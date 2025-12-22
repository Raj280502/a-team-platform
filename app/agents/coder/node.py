"""
node.py
-------
Defines the Coder agent as a Runnable.

This agent:
- Calls the LLM
- Parses structured file output
- Returns file artifacts (does NOT write to disk)
"""

from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.agents.coder.prompt import generate_prompt, repair_prompt
from app.agents.coder.schema import CoderOutput


def build_generate_node() -> RunnableSequence:
    """
    Builds and returns the Coder agent runnable.

    Returns:
        RunnableSequence: Generates structured file artifacts
                          from project scope and architecture.
    """

    llm = get_llm()

    parser = PydanticOutputParser(
        pydantic_object=CoderOutput
    )

    prompt_with_formatting = generate_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    return (
        prompt_with_formatting
        | llm
        | parser
    )
def build_repair_node() -> RunnableSequence:
    """
    Builds the coder node responsible for LOCALIZED REPAIR.

    Used ONLY when tests fail.
    """

    llm = get_llm()

    parser = PydanticOutputParser(
        pydantic_object=CoderOutput
    )

    prompt_with_formatting = repair_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    return (
        prompt_with_formatting
        | llm
        | parser
    )