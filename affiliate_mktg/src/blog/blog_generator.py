import ollama
from ollama import AsyncClient

from affiliate_mktg.src.core.enums import Models
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

class BlogGenerator:
    def __init__(self):
        logger.info("Hello from BlogGenerator!")

    async def generate_blog_by_model(
        self,
        system_prompt: str,
        user_prompt: str,
        model_name: str,
        model_options: object,
    ) -> str:
        if model_name in Models.LLAMA.value:
            return await self._generate_blog_llama(
                system_prompt, user_prompt, model_options
            )
        else:
            logger.error(
                "Error: MODELNAME is not defined. Please set the MODELNAME variable."
            )
            raise ValueError("Error: MODELNAME is not defined in Models.LLAMA.")

    async def _generate_blog_llama(
        self,
        system_prompt: str,
        user_prompt: str,
        model_options: object,
    ) -> str:
        try:
            response = ollama.chat(
                model="llama3.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options=model_options,
            )
            return response["message"]["content"]

        except ollama.ResponseError as e:
            logger.error(
                f"Error connecting to Ollama and generating stream response: {e.error}",
                exc_info=True,
            )
            if e.status_code == 404:
                logger.error(
                    "Model not found. Ensure the model name is correct and the model is available.",
                    exc_info=True,
                )
            return ""
        except Exception as e:
            logger.error(
                f"Error connecting to Ollama and generating response: {e}",
                exc_info=True,
            )
            return ""

    async def generate_blog_by_model_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        model_name: str,
        model_options: object,
    ) -> str:
        if model_name in Models.LLAMA.value:
            return await self._generate_blog_llama_stream(
                system_prompt, user_prompt, model_options
            )
        else:
            logger.error(
                "Error: MODELNAME is not defined. Please set the MODELNAME variable."
            )
            raise ValueError("Error: MODELNAME is not defined in Models.LLAMA.")

    async def _generate_blog_llama_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        model_options: object,
    ) -> str:
        try:
            all_chunks = []
            async for chunk in await AsyncClient().chat(
                model="llama3.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options=model_options,
                stream=True,
            ):
                content = chunk["message"]["content"]
                if content:
                    all_chunks.append(content)
            return "".join(all_chunks)

        except ollama.ResponseError as e:
            logger.error(
                f"Error connecting to Ollama and generating stream response: {e.error}",
                exc_info=True,
            )
            if e.status_code == 404:
                logger.error(
                    "Model not found. Ensure the model name is correct and the model is available.",
                    exc_info=True,
                )
            return ""
        except Exception as e:
            logger.error(
                f"Error connecting to Ollama and generating response: {e}",
                exc_info=True,
            )
            return ""
