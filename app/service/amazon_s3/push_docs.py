import os
import tempfile
from datetime import datetime
from app.service.amazon_s3.connection import S3Connection
from app.core.logger import logger

class S3PushDocs:
    def __init__(self, connection: S3Connection):
        self.client = connection.client
        self.bucket = connection.config.bucket_name

    def download_file(self, key: str, download_path: str):
        """Baixa um arquivo específico"""
        try:
            self.client.download_file(self.bucket, key, download_path)
            logger.info(f"Arquivo {key} baixado em {download_path}")
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo {key}: {e}")
            raise

    def download_folder(self, prefix: str, client_name: str,session_name : str) -> str:
        """
        Baixa todos os arquivos do prefixo em uma pasta temporária.
        A pasta terá o nome {client_name}_{datetime}.
        """
        try:
            objects = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            keys = [obj['Key'] for obj in objects.get('Contents', [])]
            if not keys:
                logger.warning(f"Nenhum arquivo encontrado no prefixo {prefix}")
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.mkdtemp()
            folder_name = f"{client_name}_{session_name}_{timestamp}"
            folder_path = os.path.join(temp_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            for key in keys:
                relative_name = os.path.relpath(key, prefix)
                download_path = os.path.join(folder_path, relative_name)
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                self.client.download_file(self.bucket, key, download_path)

            logger.info(f"Pasta de download criada em {folder_path}")
            return folder_path

        except Exception as e:
            logger.error(f"Erro ao baixar pasta {prefix}: {e}")
            raise
