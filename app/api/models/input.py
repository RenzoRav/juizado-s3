from pydantic import BaseModel

class ClientData(BaseModel) : 
    client_id : int

class SessionData(ClientData) : 
    session_id : int

class FileData(SessionData) : 
    file_name : str

class DownloadSession(BaseModel) : 
    client_name : str 
    session_name : str 
    client_id : int 
    session_id : int