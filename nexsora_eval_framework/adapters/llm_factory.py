"""
Got deepeval model error and Otel connection error on first run

Deepeval error:
DeepEval does not natively accept a plain LangChain ChatGoogleGenerativeAI instance. 
Instead, it expects custom LLMs to inherit from its own wrapper class: DeepEvalBaseLLM

Ragas error:
"Ragas Engine Error: 'GeminiDeepEvalWrapper' object has no attribute 'invoke'"

Deepeval error & Ragas error:
"DeepEval Execution Error: 'list' object has no attribute 'find'"
"Ragas Engine Error: 'list' object has no attribute 'replace'"
"""
import os
from typing import Union, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from deepeval.models.base_model import DeepEvalBaseLLM

def _extract_text_content(content: Any) -> str:
    """Safely extracts string content from standard strings, lists of dicts, or AIMessages."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Extract text blocks if content is a list of dicts/blocks e.g. [{'type': 'text', 'text': '...'}]
        texts = []
        for item in content:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
            elif hasattr(item, "text"):
                texts.append(item.text)
        return "\n".join(texts)
    elif hasattr(content, "content"):
        return _extract_text_content(content.content)
    return str(content)


class GeminiDeepEvalWrapper(DeepEvalBaseLLM):
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.0, api_key_env_var: str = "GEMINI_API_KEY"):
        api_key = os.getenv(api_key_env_var) or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(f"Environment variable '{api_key_env_var}' or 'GOOGLE_API_KEY' is not set in environment or .env file!")
        
        self.model_name = model_name
        self.langchain_model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            max_retries=6,
            timeout=60.0
        )

    def load_model(self):
        return self.langchain_model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        response = chat_model.invoke(prompt)
        return _extract_text_content(response)

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        response = await chat_model.ainvoke(prompt)
        return _extract_text_content(response)

    def invoke(self, input, config=None, **kwargs):
        response = self.langchain_model.invoke(input, config=config, **kwargs)
        # Ensure that if calling .content on the returned AIMessage, it returns a string if requested
        return response

    async def ainvoke(self, input, config=None, **kwargs):
        return await self.langchain_model.ainvoke(input, config=config, **kwargs)

    def get_model_name(self):
        return self.model_name


class LLMFactory:
    @staticmethod
    def create_llm(
        provider: str,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.0,
        api_key_env_var: str = "GEMINI_API_KEY"
    ):
        if provider.lower() in ["google", "gemini"]:
            return GeminiDeepEvalWrapper(
                model_name=model_name,
                temperature=temperature,
                api_key_env_var=api_key_env_var
            )
        else:
            raise NotImplementedError(f"Provider '{provider}' is not supported in LLMFactory.")