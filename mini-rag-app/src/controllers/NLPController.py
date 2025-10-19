import json
from .BaseController import BaseController
from models.db_scehmes.project import Project
from models.db_scehmes.data_chunk import DataChunk
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnum

class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

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
        return json.loads(json.dumps(results, default = lambda x: x.__dict__))
