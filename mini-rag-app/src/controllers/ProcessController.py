from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from models import ProcessingEnum, ResponseSignal
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from routers import ProcessRequest

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
        if file_extenstion == ProcessingEnum.TXT.value:
            return TextLoader(file_path=file_path, encoding='utf-8')

        elif file_extenstion == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path=file_path)

        else:
            return None

    def get_content_from_file(self, file_id: str):
        file_loader = self.get_file_loader(file_id=file_id)
        if file_loader is None:
            return None
        return file_loader.load()

    def process_file_content(self, file_id:str, file_content: list, chunk_size: int, overlap_size: int):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = overlap_size,
            length_function = len)
        
        file_content_texts = [rec.page_content for rec in file_content]
        file_content_metadata = [rec.metadata for rec in file_content]
        chunks = text_splitter.create_documents(file_content_texts, file_content_metadata)
        return chunks