import subprocess
import uuid
import os
import tarfile
import io
from typing import List, Tuple, Optional

from deepagents.backends.sandbox import BaseSandbox
from deepagents.backends.protocol import ExecuteResponse, FileUploadResponse, FileDownloadResponse, FileOperationError

class DockerBackend(BaseSandbox):
    def __init__(self, image: str = "python:3.11-slim", container_name: Optional[str] = None):
        self.image = image
        self._id = container_name or f"deepagents-{uuid.uuid4().hex[:8]}"
        self._ensure_container()

    def _ensure_container(self):
        # Check if container exists and is running
        result = subprocess.run(["docker", "ps", "-a", "--filter", f"name={self._id}", "--format", "{{.Status}}"], capture_output=True, text=True)
        if not result.stdout:
            # Create and start container
            subprocess.run([
                "docker", "run", "-d", "--name", self._id, 
                "--rm", # Automatically remove when stopped
                "-it", self.image, "bash"
            ], check=True)
        elif "Up" not in result.stdout:
            subprocess.run(["docker", "start", self._id], check=True)

    @property
    def id(self) -> str:
        return self._id

    def execute(self, command: str, *, timeout: Optional[int] = None) -> ExecuteResponse:
        try:
            # We use 'bash -c' to support pipes and redirects in the command
            exec_cmd = ["docker", "exec", self._id, "bash", "-c", command]
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=timeout)
            
            output = result.stdout
            if result.stderr:
                output += result.stderr
            
            return ExecuteResponse(
                output=output,
                exit_code=result.returncode,
                truncated=False # We could implement truncation if needed
            )
        except subprocess.TimeoutExpired:
            return ExecuteResponse(
                output=f"Error: Command timed out after {timeout} seconds",
                exit_code=124,
                truncated=False
            )
        except Exception as e:
            return ExecuteResponse(
                output=f"Error executing command: {str(e)}",
                exit_code=1,
                truncated=False
            )

    def upload_files(self, files: List[Tuple[str, bytes]]) -> List[FileUploadResponse]:
        responses = []
        for path, content in files:
            try:
                # Use docker cp via tar to upload files
                tar_stream = io.BytesIO()
                with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                    tarinfo = tarfile.TarInfo(name=os.path.basename(path))
                    tarinfo.size = len(content)
                    tar.addfile(tarinfo, io.BytesIO(content))
                
                tar_stream.seek(0)
                
                # Create directory if it doesn't exist
                dir_path = os.path.dirname(path)
                if dir_path and dir_path != "/":
                    self.execute(f"mkdir -p {dir_path}")

                # Copy to container
                dest_dir = dir_path or "/"
                subprocess.run(
                    ["docker", "cp", "-", f"{self._id}:{dest_dir}"],
                    input=tar_stream.read(),
                    check=True
                )
                responses.append(FileUploadResponse(path=path))
            except Exception as e:
                responses.append(FileUploadResponse(path=path, error="invalid_path"))
        return responses

    def download_files(self, paths: List[str]) -> List[FileDownloadResponse]:
        responses = []
        for path in paths:
            try:
                # Check if file exists
                check = self.execute(f"test -f {path}")
                if check.exit_code != 0:
                    responses.append(FileDownloadResponse(path=path, error="file_not_found"))
                    continue

                # Use docker cp to get file content
                # Note: docker cp sends it as a tar stream
                result = subprocess.run(
                    ["docker", "cp", f"{self._id}:{path}", "-"],
                    capture_output=True,
                    check=True
                )
                
                # Extract from tar
                tar_stream = io.BytesIO(result.stdout)
                with tarfile.open(fileobj=tar_stream, mode='r') as tar:
                    member = tar.getmembers()[0]
                    extract = tar.extractfile(member)
                    if extract:
                        content = extract.read()
                        responses.append(FileDownloadResponse(path=path, content=content))
                    else:
                        responses.append(FileDownloadResponse(path=path, error="file_not_found"))
                    
                
            except Exception as e:
                responses.append(FileDownloadResponse(path=path, error="permission_denied"))
        return responses

    def cleanup(self):
        subprocess.run(["docker", "stop", self._id], capture_output=True)
