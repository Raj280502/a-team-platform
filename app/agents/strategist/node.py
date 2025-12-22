"""
node.py
-------
Defines the Strategist agent as a LangChain Runnable.

This file connects:
- Prompt
- LLM
- Output parser

into ONE reusable pipeline.
"""

from langchain_core.runnables import RunnableSequence, RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser

from app.core.llm import get_llm
from app.agents.strategist.prompt import strategist_prompt
from app.agents.strategist.schema import StrategistOutput


def build_strategist_node() -> RunnableSequence:
    """
    Builds and returns the Strategist agent runnable.

    Returns:
        RunnableSequence: A pipeline that takes user input
                          and returns structured project scope.
    """

    # 1. Load shared LLM (singleton)
    llm = get_llm()

    # 2. Create output parser
    output_parser = PydanticOutputParser(
        pydantic_object=StrategistOutput
    )

    # 3. Inject formatting instructions into prompt
    prompt_with_formatting = strategist_prompt.partial(
        format_instructions=output_parser.get_format_instructions()
    )
    
    def debug_llm_output(x):
        print("\n--- RAW LLM OUTPUT ---")
        print(x)
        return x
    # 4. Build runnable pipeline
    strategist_chain = (
        prompt_with_formatting
        | llm
        | debug_llm_output
        | output_parser
    )
    print("Strategist node module loaded. Use build_strategist_node() to get the agent.")
    return strategist_chain

