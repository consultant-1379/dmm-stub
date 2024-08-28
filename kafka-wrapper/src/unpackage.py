import tarfile 
from zipfile import ZipFile 
from proto_compile import compile_protofile

class unpack:

    def __init__(self, file_names):
        self.file_names = file_names
    def untar_file(self,file_name):
        file = tarfile.open('./resources/'+file_name) 
        print(f"Untar the tgz file of - ${file_name}")
        file.extractall('/resources') 
        file.close() 
    def unzip_file(self,file_name):
        with ZipFile('./resources/'+file_name, 'r') as zip: 
            zip.printdir() 
            print(f"unzip the file of - {file_name}") 
            zip.extractall('.') 
            print('Done!') 
        
        # Compile proto file
        print("compile proto file")
        protoCompile = compile_protofile("./","./","./pm_event/*.proto")
        protoCompile.execute_protoc()
    def execute(self):
        for file_name in self.file_names:
            if file_name.endswith('.tgz') or file_name.endswith('.tar.gz'):
                self.untar_file(file_name)
            elif file_name.endswith('.zip'):
                self.unzip_file(file_name)
            else:
                print(f"Unsupported file format for {file_name}")
def main():       
    file_names= ["pm_event_standardized_242_23_Q4.zip","4G_PM_Events_242_23_Q4.tgz"]
    untar = unpack(file_names)
    untar.execute()
    
if __name__ == "__main__":
    main()
