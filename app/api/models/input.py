from pydantic import BaseModel

class UserData(BaseModel) :
    user_id : int 

class ClientData(UserData) : 
    client_id : int

class SessionData(ClientData) : 
    session_id : int

class FileData(SessionData) : 
    file_name : str

class DownloadSession(BaseModel) : 
    client_name : str 
    session_name : str 
    user_id : int
    client_id : int 
    session_id : int