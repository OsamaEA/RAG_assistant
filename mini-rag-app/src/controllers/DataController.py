from .BaseController import BaseController

class DataController(BaseController):

    def __init__(self):
        super().__init__()

    def valdiate_uploaded_file(self, file):
        '''
        Validate the uploaded file based on type and size.'''
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, f"File type {file.content_type} is not allowed."

        if file.size > self.app_settings.MAX_FILE_SIZE * 1024 * 1024:
            return False, f"File size exceeds the maximum limit of {self.app_settings.MAX_FILE_SIZE} MB."

        return True, "File is valid."