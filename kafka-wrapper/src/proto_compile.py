import subprocess
import glob

class compile_protofile:

    def __init__(self, proto_path,python_out,proto_files_pattern):
        self.proto_path = proto_path
        self.python_out = python_out
        self.proto_files_pattern = proto_files_pattern
    def execute_protoc(self):
        # Use glob to manually expand the wildcard
        proto_files = glob.glob(self.proto_files_pattern)
        
        # Check if any files match the pattern
        if not proto_files:
            print(f"No .proto files found matching the pattern: {self.proto_files_pattern}")
            return
        
        command = [
            "protoc",
            f"--proto_path={self.proto_path}",
            f"--python_out={self.python_out}",
        ] + proto_files
        
        try:
            subprocess.run(command, check=True)
            print("Proto files generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error generating proto files: {e}")

