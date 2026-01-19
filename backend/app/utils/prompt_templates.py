from typing import List
from langchain_core.prompts import PromptTemplate


def get_system_prompt(input_variables: List = [], template: str = "You are a helpful assistant that provides accurate and concise information.") -> PromptTemplate:
    system_prompt = PromptTemplate(
        input_variables=input_variables,
        template=template,
    )
    return system_prompt
