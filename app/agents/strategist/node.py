"""
node.py - Strategist agent runnable.
Connects prompt → LLM → output parser.
"""

from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.agents.strategist.prompt import strategist_prompt
from app.agents.strategist.schema import StrategistOutput


def build_strategist_node() -> RunnableSequence:
    """Builds the Strategist agent chain."""
    llm = get_llm(role="strategist")

    output_parser = PydanticOutputParser(pydantic_object=StrategistOutput)

    prompt_with_formatting = strategist_prompt.partial(
        format_instructions=output_parser.get_format_instructions()
    )

    return prompt_with_formatting | llm | output_parser
