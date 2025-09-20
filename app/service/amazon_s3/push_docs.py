from datetime import datetime
import tempfile
import zipfile
import os

from app.service.amazon_s3.connection import S3Connection
from app.core.logger import logger


class S3PushDocs:
    def __init__(self, connection: S3Connection):
        self.client = connection.client
        self.bucket = connection.config.bucket_name

    def download_file(self, key: str, download_path: str):
        try:
            self.client.download_file(self.bucket, key, download_path)
            logger.info(f"Arquivo {key} baixado em {download_path}")
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo {key}: {e}")
            raise

    def download_folder(self, prefix: str, client_name: str, session_name: str) -> str:
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
                relative_name = key[len(prefix):].lstrip("/")
                if not relative_name or relative_name.startswith("."):
                    continue

                download_path = os.path.join(folder_path, relative_name)
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                self.client.download_file(self.bucket, key, download_path)

            logger.info(f"Pasta de download criada em {folder_path}")
            return folder_path

        except Exception as e:
            logger.error(f"Erro ao baixar pasta {prefix}: {e}")
            raise

    def make_zip_from_folder(self, folder_path: str, zip_path: str):
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)

            logger.info(f"Pasta {folder_path} compactada em {zip_path}")
            return zip_path

        except Exception as e:
            logger.error(f"Erro ao compactar pasta {folder_path}: {e}")
            raise
