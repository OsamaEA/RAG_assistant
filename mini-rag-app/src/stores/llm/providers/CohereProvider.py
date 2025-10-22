from stores.llm.LLMInterface import LLMInterface
from stores.llm.LLMEnums import CohereEnums, DocumentTypeEnum
#import cohere
import logging

class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,
                default_input_max_characters: int = 1000,
                default_generation_max_output_token: int = 1000,
                default_generation_temperature: float = 0.1):

        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_token = default_generation_max_output_token
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None


        self.client = None#cohere.Client(api_key = self.api_key) #Because Cohere package has issues installing on some systems
        self.enums = CohereEnums

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id:str):
        self.generation_model_id = model_id
        self.logger.info(f"Set Cohere generation model to: {model_id}")

    def set_embedding_model(self, model_id:str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(f"Set Cohere embedding model to: {model_id} with embedding size: {embedding_size}")


    def generate_text(self, prompt: str, chat_history: list = [], max_output_token: int = None, temperature: float = None) -> str:
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        if not self.generation_model_id:
            self.logger.error("Cohere generation model is not set.")
            return None

        max_output_token = max_output_token if max_output_token else self.default_generation_max_output_token
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            max_tokens = max_output_token,
            temperature = temperature
        )


        if not response or not response.text:
            self.logger.error("No response received from Cohere.")
            return None

        result = response.text
        return result



    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        if not self.embedding_model_id:
            self.logger.error("Cohere embedding model is not set.")
            return None


        input_type = CohereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CohereEnums.QUERY

        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type
        )

        if not response or not response.embeddings or not response.embeddings.float_:
            self.logger.error("No embedding data received from Cohere.")
            return None

        return response.embeddings.float_[0]


    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "text": self.process_text(prompt)}




    #Helper Functions not in LLM interface
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    
    