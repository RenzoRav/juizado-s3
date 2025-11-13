from app.service.amazon_s3.connection import S3Connection
from app.utils.data import ( 
    S3PathClient , 
    S3PathSession
)

from app.core.logger import logger

class S3CreatePath:
    def __init__(
            self, 
            connection: S3Connection, 
            path: str
    ):
        self.client = connection.client
        self.bucket = connection.config.bucket_name
        self.path = path

    def _exists(self) -> bool:
        response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=f"{self.path}/",
            MaxKeys=1
        )
        return "Contents" in response

    def create_path(self):
        """Cria um 'diretório' no bucket, se não existir"""
        try:
            if self._exists():
                logger.info(f"Diretório já existe: {self.bucket}/{self.path}/")
                return f"{self.bucket}/{self.path}/ (já existia)"

            logger.info("Criando diretório...")
            self.client.put_object(
                Bucket=self.bucket, 
                Key=f"{self.path}/"
            )
            logger.info("Diretório criado com sucesso!")
            return f"{self.bucket}/{self.path}/"
        except Exception as e: 
            logger.error(f"Erro ao criar diretório: {e}")
            raise
        

class S3CreatePathClient(S3CreatePath):
    def __init__(self, connection: S3Connection, client_name: str):
        super().__init__(
            connection, 
            S3PathClient(
                client_name=client_name
            ).get_path_client())

    def create_path(self) -> str:
        return super().create_path()


class S3CreatePathSession(S3CreatePath):
    def __init__(self, connection: S3Connection,client_name: str, session_name: str):
        super().__init__(
            connection, 
            S3PathSession(
                client_name=client_name , 
                session_name=session_name
            ).get_path_session())

    def create_path(self) -> str:
        return super().create_path()

