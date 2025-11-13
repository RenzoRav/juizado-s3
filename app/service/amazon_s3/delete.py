from app.core.logger import logger
from app.service.amazon_s3.connection import S3Connection
from app.utils.data import (
    S3PathSession, 
    S3PathClient, 
    S3PathFile
)

class S3DeletePath:
    def __init__(self, connection: S3Connection, path: str):
        self.client = connection.client
        self.bucket = connection.config.bucket_name
        self.path = path

    def delete_path(self):
        try:
            logger.info(f"Deletando diretório {self.path}/ ...")

            objects = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=f"{self.path}/"
            )

            if "Contents" not in objects:
                logger.warning(f"Nenhum objeto encontrado em {self.path}/")
                return f"{self.bucket}/{self.path}/ já estava vazio."
            
            to_delete = [{"Key": obj["Key"]} for obj in objects["Contents"]]

            self.client.delete_objects(
                Bucket=self.bucket,
                Delete={"Objects": to_delete}
            )

            logger.info(f"Diretório {self.path}/ deletado com sucesso!")
            return f"{self.bucket}/{self.path}/ removido."
        except Exception as e:
            logger.error(f"Erro ao deletar diretório {self.path}: {e}")
            raise


class S3DeletePathClient(S3DeletePath):
    def __init__(self, connection: S3Connection, client_name: str):
        super().__init__(
            connection,
            S3PathClient(client_name=client_name).get_path_client()
        )

    def delete_path(self) -> str:
        return super().delete_path()


class S3DeletePathSession(S3DeletePath):
    def __init__(self, connection: S3Connection, client_name: str, session_name: str):
        super().__init__(
            connection,
            S3PathSession(client_name=client_name, session_name=session_name).get_path_session()
        )

    def delete_path(self) -> str:
        return super().delete_path()


class S3DeleteFile:
    def __init__(self, connection: S3Connection, client_name: str, session_name: str, file_name: str):
        self.client = connection.client
        self.bucket = connection.config.bucket_name
        self.client_name = client_name
        self.session_name = session_name
        self.file_name = file_name
        self.file_path = self.create_path()

    def create_path(self):
        return S3PathFile(
            client_name=self.client_name,
            session_name=self.session_name,
            file_name=self.file_name
        ).get_path_file()

    def delete_file(self) -> str:
        try:
            # Confirma se existe
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=self.file_path, MaxKeys=1)
            if "Contents" not in response:
                logger.warning(f"Arquivo não encontrado: {self.file_path}")
                return f"{self.bucket}/{self.file_path} não encontrado."

            # Deleta
            self.client.delete_object(Bucket=self.bucket, Key=self.file_path)
            logger.info(f"Arquivo deletado: {self.file_path}")

            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=self.file_path, MaxKeys=1)
            if "Contents" in response:
                return f"{self.bucket}/{self.file_path} não pôde ser deletado."
            return f"{self.bucket}/{self.file_path} deletado com sucesso."

        except Exception as e:
            logger.error(f"Erro ao deletar arquivo {self.file_path}: {e}")
            raise
