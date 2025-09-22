from pydantic import BaseModel

class UserData(BaseModel) :
    user_name : str 

class ClientData(UserData) : 
    client_name : str

class SessionData(ClientData) : 
    session_name : str 

class FileData(SessionData) : 
    file_name : str

class DownloadSession(BaseModel) : 
    client_name : str 
    session_name : str 
    unic_name : str 
    unic_client : str 
    unic_session : str 