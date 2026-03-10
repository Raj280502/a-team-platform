"""
node.py - Coder agent runnables.
Build chains for code generation and repair.
"""

from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.agents.coder.prompt import generate_prompt, repair_prompt
from app.agents.coder.schema import CoderOutput


def build_generate_node() -> RunnableSequence:
    """Builds the code generation chain."""
    llm = get_llm(role="coder")

    parser = PydanticOutputParser(pydantic_object=CoderOutput)

    prompt_with_formatting = generate_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )

    return prompt_with_formatting | llm | parser


def build_repair_node() -> RunnableSequence:
    """
    Builds the repair chain.
    Returns raw LLM output (no Pydantic parser) since repaired code
    may contain unescaped quotes that break JSON parsing.
    """
    llm = get_llm(role="repair")

    # No Pydantic parser — repair_node handles parsing manually
    return repair_prompt | llm