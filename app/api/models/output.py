from pydantic import BaseModel
from typing import List , Optional

class DirectoryOutput(BaseModel) :
    status : str
    message : str 
    path : str 

class FileStatus(BaseModel):
    filename: str               
    path: Optional[str] = None  
    status: str                
    error: Optional[str] = None 

class UploadOutput(BaseModel):
    uploaded_files: List[FileStatus] 

class DownloadSessionRequest(BaseModel):
    user_name: str
    client_name: str
    session_name: str

class DownloadFileRequest(DownloadSessionRequest):
    file_name: str