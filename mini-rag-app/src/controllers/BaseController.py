from helpers.config import get_settings, Settings
import os
import random
import string

class BaseController:
    
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir, "Assets/files")
        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)


        self.database_dir = os.path.join(self.base_dir,
                                         "Assets/database")

    def generate_random_id(self, length=12):

        characters = string.ascii_letters + string.digits
        random_id = ''.join(random.choices(characters, k=length))
        return random_id

    def get_database_path(self, db_name:str):
        database_path = os.path.join(self.database_dir, 
                                     db_name)
        
        if not os.path.exists(database_path):
            os.mkdir(database_path)
        
        return database_path