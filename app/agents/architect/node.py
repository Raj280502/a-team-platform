"""
node.py
-------
Defines the Architect agent as a Runnable.
"""

from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.agents.architect.prompt import architect_prompt
from app.agents.architect.schema import ArchitectOutput


def build_architect_node() -> RunnableSequence:
    """
    Builds and returns the Architect agent runnable.

    Returns:
        RunnableSequence: Converts project scope
                          into system architecture.
    """

    llm = get_llm()

    output_parser = PydanticOutputParser(
        pydantic_object=ArchitectOutput
    )

    prompt_with_formatting = architect_prompt.partial(
        format_instructions=output_parser.get_format_instructions()
    )

    architect_chain = (
        prompt_with_formatting
        | llm
        | output_parser
    )

    return architect_chain
