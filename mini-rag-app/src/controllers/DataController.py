from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ResponseSignal
import re
import os
class DataController(BaseController):

    def __init__(self):
        super().__init__()

    def valdiate_uploaded_file(self, file):
        '''
        Validate the uploaded file based on type and size.'''
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED.value

        if file.size > self.app_settings.MAX_FILE_SIZE * 1024 * 1024:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALID.value

    def generate_unique_filename(self, original_filename: str, project_id: str):
        project_path = ProjectController().get_project_path(project_id=project_id)
        clean_filename = self.clean_filename(original_filename)
        random_filename = self.generate_random_id()+"_"+clean_filename
        file_path = os.path.join(project_path, random_filename)
        
        while os.path.exists(file_path):
            random_filename = self.generate_random_id()+"_"+clean_filename
            file_path = os.path.join(project_path, random_filename)

        return(file_path, random_filename)


    def clean_filename(self, original_filename: str):
        # Remove any unwanted characters from the filename
        cleaned_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_filename)
        return cleaned_filename