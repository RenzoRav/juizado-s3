import boto3

from app.utils.data import S3Config
from app.core.logger import logger

class S3Connection:
    def __init__(self, config: S3Config):
        self.config = config
        try : 
            logger.info("Conectando ao S3...")
            self.client = boto3.client(
                's3',
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region_name
            )
            logger.info("Conexão estabelecida com sucesso!")
        except Exception as e :
            logger.error(f"Erro ao conectar com o bucket S3 : {e}")


config = S3Config()
s3 = S3Connection(config)


