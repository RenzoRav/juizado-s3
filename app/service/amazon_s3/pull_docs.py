from app.service.amazon_s3.connection import S3Connection
from app.core.logger import logger


class S3PullDocs:
    def __init__(
            self, 
            connection: S3Connection
    ):
        self.client = connection.client
        self.bucket = connection.config.bucket_name

    def upload_file(
            self, 
            file_path: str, 
            object_name: str = None
    ):
        if object_name is None:
            object_name = os.path.basename(file_path)
        try : 
            logger.info(f"Upload do arquivo : {object_name}")
            self.client.upload_file(
                file_path, 
                self.bucket, 
                object_name
            )
            logger.info("Upload feito com sucesso!")
            return f"{self.bucket}/{object_name}"
        except Exception as e :
            logger.error(f"Erro ao tentar fazer upload : {e}")