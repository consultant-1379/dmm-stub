import tarfile 
from zipfile import ZipFile 

class unpack:

    def __init__(self, file_name):
        self.file_name = file_name
    def untar_file(self):
        file = tarfile.open('./resources/'+self.file_name) 
        print(f"Untar the tgz file of - ${self.file_name}")
        file.extractall('/resources') 
        file.close() 

