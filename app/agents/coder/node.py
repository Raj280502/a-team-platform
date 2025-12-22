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
from app.agents.coder.prompt import coder_prompt
from app.agents.coder.schema import CoderOutput


def build_coder_node() -> RunnableSequence:
    """
    Builds and returns the Coder agent runnable.

    Returns:
        RunnableSequence: Generates structured file artifacts
                          from project scope and architecture.
    """

    llm = get_llm()

    output_parser = PydanticOutputParser(
        pydantic_object=CoderOutput
    )

    prompt_with_formatting = coder_prompt.partial(
        format_instructions=output_parser.get_format_instructions()
    )

    coder_chain = (
        prompt_with_formatting
        | llm
        | output_parser
    )

    return coder_chain
