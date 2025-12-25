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


from app.utils.file_ops import normalize_code


def coder_node(state):
    llm = get_llm()

    generated_files = {}

    for file_path in state["planned_files"]:
        file_chain = single_file_prompt | llm
        content = file_chain.invoke({
            "file_path": file_path,
            "project_scope": state["project_scope"],
            "architecture": state["architecture"],
        })

        generated_files[file_path] = normalize_code(content.content)

    return CoderOutput(new_files=generated_files)