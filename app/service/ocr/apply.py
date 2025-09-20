import os
from PIL import Image, ImageOps, ImageEnhance
from typing import Optional
from app.service.amazon_s3.connection import S3Connection
from app.utils.data import S3PathSession
from app.core.logger import logger

class S3ManagerUpload:
    """
    Gerencia upload de arquivos individuais para MinIO.
    - Converte imagens em PDF.
    - Suporta documentos Office/PDF/TXT.
    """

    _SUPPORTED_IMAGE_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    _SUPPORTED_DOCS = (".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt")

    def __init__(self, s3_connection: S3Connection, user_name: str, client_name: str, session_name: str):
        self.client = s3_connection.client
        self.bucket = s3_connection.config.bucket_name
        self.path = S3PathSession(user_name, client_name, session_name).get_path_session()

    def _object_exists(self, object_name: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=object_name)
            return True
        except self.client.exceptions.ClientError as e:
            # Captura erro 404 que significa "não existe"
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return False
            logger.warning(f"Erro ao verificar objeto {object_name}: {e}")
            return False

    def _process_image(self, file_path: str) -> Optional[str]:
        try:
            img = Image.open(file_path)
            img = ImageOps.grayscale(img)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            a4_width, a4_height = (595, 842)
            img.thumbnail((a4_width, a4_height), Image.LANCZOS)
            img = img.convert("RGB")

            pdf_path = f"{os.path.splitext(file_path)[0]}.pdf"
            img.save(pdf_path, "PDF")
            logger.info(f"Imagem convertida para PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Erro ao processar imagem {file_path}: {e}")
            return None

    def _upload_file(self, file_path: str, upload_prefix: str) -> dict:
        filename = os.path.basename(file_path)
        object_name = f"{upload_prefix}/{filename}"

        if os.path.splitext(file_path)[1].lower() in self._SUPPORTED_IMAGE_FORMATS:
            file_path = self._process_image(file_path)
            if file_path:
                object_name = f"{upload_prefix}/{os.path.basename(file_path)}"

        if not file_path:
            return {"filename": filename, "path": None, "status": "error", "error": "Erro ao processar arquivo"}

        if self._object_exists(object_name):
            return {"filename": filename, "path": f"{self.bucket}/{object_name}", "status": "exists", "error": None}

        try:
            self.client.upload_file(file_path, self.bucket, object_name)
            return {"filename": filename, "path": f"{self.bucket}/{object_name}", "status": "uploaded", "error": None}
        except Exception as e:
            return {"filename": filename, "path": None, "status": "error", "error": str(e)}
