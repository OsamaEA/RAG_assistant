import json
from .BaseController import BaseController
from models.db_scehmes.project import Project
from models.db_scehmes.data_chunk import DataChunk
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnum

class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str) -> str:
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        if self.vectordb_client.is_collection_existed(collection_name=collection_name):
            self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self, project: Project) -> dict:
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        if self.vectordb_client.is_collection_existed(collection_name=collection_name):
            return json.loads(json.dumps(collection_info, default = lambda x: x.__dict__))
        return {}
    

    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                             chunk_ids: List[int],
                             do_reset: bool = False):
        # step 1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        # step 2: manage items
        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [chunk.chunk_metadata for chunk in chunks]
        vectors = [self.embedding_client.embed_text(text=text,
                                                    document_type=DocumentTypeEnum.DOCUMENT.value)
                   for text in texts]
        # step 3: create collection
        self.vectordb_client.create_collection(collection_name=collection_name,
                                               embedding_size=self.embedding_client.embedding_size,
                                               do_reset=do_reset)
        # step 4: insert chunks in database
        self.vectordb_client.insert_many(collection_name=collection_name,
                                        texts=texts,
                                        vectors=vectors,
                                        metadata=metadata,
                                        record_ids = chunk_ids)
        return True
    

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        vector = self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.QUERY.value)
        if not vector or len(vector) == 0:
            return False
        results = self.vectordb_client.search_by_vector(collection_name=collection_name,
                                                        vector=vector,
                                                        limit=limit)
        if not results:
            return False
        return [result.dict() for result in results]



    def answer_rag_question(self, project: Project, query: str,
                            limit: int = 10,
                            chat_history: list = [],
                            max_output_token: int = None,
                            temperature: float = None) -> str:
        # step 1: retrieve relevant documents from vector database
        retrieved_docs = self.search_vector_db_collection(project=project,
                                                          text=query,
                                                          limit=limit)
        answer, full_prompt, chat_history = None, None, None

        if not retrieved_docs or len(retrieved_docs) == 0:
            self.logger.error("No relevant documents found in vector database.")
            return None

        # step 2: construct prompt with retrieved documents
        system_prompt = self.template_parser.get("rag", "system_prompt")
        document_prompts = [
            self.template_parser.get("rag", "document_prompt",
                                     {"doc_num": idx + 1,
                                      "chunk_text": doc["text"]})
            for idx, doc in enumerate(retrieved_docs)
        ]

        footer_prompt = self.template_parser.get("rag", "footer_prompt", 
                                                 {"user_question": query})

        chat_history = [
            self.generation_client.construct_prompt(prompt=system_prompt, role=self.generation_client.enums.SYSTEM.value)
        ]

        full_prompt = "\n\n".join(document_prompts) + "\n\n" + footer_prompt

        answer = self.generation_client.generate_text(prompt=full_prompt,
                                                      chat_history=chat_history,
                                                      max_output_token=max_output_token,
                                                      temperature=temperature)
        
        return answer, full_prompt, chat_history
