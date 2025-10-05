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

    def generate_random_id(self, length=12):

        characters = string.ascii_letters + string.digits
        random_id = ''.join(random.choices(characters, k=length))
        return random_id
