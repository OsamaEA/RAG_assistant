from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from models import ProcessingEnum, ResponseSignal
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from routers import ProcessRequest
import re


class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        return file_id.split('.')[-1].lower()

    def get_file_loader(self, file_id: str):
        file_extenstion = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(self.project_path, file_id)

        if not os.path.exists(file_path):
            return None
            
        if file_extenstion == ProcessingEnum.TXT.value:
            return TextLoader(file_path=file_path, encoding='utf-8')

        elif file_extenstion == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path=file_path)

        else:
            return None
        
    def sanitize_text(self, text: str) -> str:
        """Removes PostgreSQL-invalid control characters (especially null bytes)."""
        if not text:
            return ""
        return re.sub(r"[\x00-\x1F]+", "", text)
    

    def get_content_from_file(self, file_id: str):
        file_loader = self.get_file_loader(file_id=file_id)
        if file_loader is None:
            return None
        #return file_loader.load()
        # Sanitizing Text Content
        docs = file_loader.load()
        for doc in docs:
            if hasattr(doc, "page_content") and isinstance(doc.page_content, str):
                doc.page_content = self.sanitize_text(doc.page_content)
        return docs

    def process_file_content(self, file_id:str, file_content: list, chunk_size: int, overlap_size: int):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = overlap_size,
            length_function = len)
        
        file_content_texts = [rec.page_content for rec in file_content]
        file_content_metadata = [rec.metadata for rec in file_content]
        chunks = text_splitter.create_documents(file_content_texts, file_content_metadata)
        return chunks