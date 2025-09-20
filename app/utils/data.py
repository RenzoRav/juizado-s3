from dataclasses import dataclass

from app.core.settings import configs

@dataclass
class S3Config:
    endpoint_url: str = configs.S3_ENDPOINT_URL   
    access_key: str = configs.AWS_ACCESS_KEY_ID
    secret_key: str = configs.AWS_SECRET_ACCESS_KEY
    region_name: None|str = configs.REGION_NAME
    bucket_name: str = configs.BUCKET_NAME


from app.core.settings import configs

class S3PathUser:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.root_1 = configs.ROOT1

    def get_path_user(self) -> str:
        """Retorna o caminho do usuário em formato string"""
        return f"{self.root_1}/{self.user_name}"


class S3PathClient(S3PathUser):
    def __init__(self, user_name: str, client_name: str):
        super().__init__(user_name)
        self.client_name = client_name
        self.root_2 = configs.ROOT2

    def get_path_client(self) -> str:
        """Retorna o caminho do cliente em formato string"""
        return f"{self.root_1}/{self.user_name}/{self.root_2}/{self.client_name}"


class S3PathSession(S3PathClient):
    def __init__(self, user_name: str, client_name: str, session_name: str):
        super().__init__(user_name, client_name)
        self.session_name = session_name
        self.root_3 = configs.ROOT3

    def get_path_session(self) -> str:
        """Retorna o caminho da sessão em formato string"""
        return f"{self.root_1}/{self.user_name}/{self.root_2}/{self.client_name}/{self.root_3}/{self.session_name}"


class S3PathFile(S3PathSession):
    def __init__(self, user_name: str, client_name: str, session_name: str, file_name: str):
        super().__init__(user_name, client_name, session_name)
        self.file_name = file_name

    def get_path_file(self) -> str:
        """Retorna o caminho completo do arquivo"""
        return f"{self.root_1}/{self.user_name}/{self.root_2}/{self.client_name}/{self.root_3}/{self.session_name}/{self.file_name}"


