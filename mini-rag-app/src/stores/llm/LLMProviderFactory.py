from LLMEnums import LLMEnum
from providers.OpenAIProvider import OpenAIProvider
from providers.CohereProvider import CohereProvider
##from helpers.config import Config

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnum.OPENAI.value:
            return OpenAIProvider(
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPEN_API_URL,
                default_input_max_characters = self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_token = self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature = self.config.default_generation_temperature)

        if provider == LLMEnum.COHERE.value:
            return CohereProvider(
                api_key = self.config.COHERE_API_KEY,
                default_input_max_characters = self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature = self.config.GENERATION_DEFAULT_TEMPERATURE)
                


        return None