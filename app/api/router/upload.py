import os
import shutil
import tempfile
import zipfile
from typing import List

from fastapi import (
    APIRouter,
    UploadFile,
    HTTPException,
    File,
    Form
)

from app.service.amazon_s3.scan import S3ManagerUpload
from app.service.amazon_s3.delete import S3DeleteFile
from app.api.models.input import FileData
from app.api.models.output import UploadOutput, DirectoryOutput
from app.service.amazon_s3.connection import s3
from app.core.logger import logger

router_upload = APIRouter(tags=["Upload"])


def _is_safe_path(base_path: str, target_path: str) -> bool:
    """Verifica se o caminho extraído de um ZIP é seguro (sem path traversal)."""
    return os.path.realpath(target_path).startswith(os.path.realpath(base_path))


@router_upload.post("/upload/files", response_model=UploadOutput)
async def upload_files(
    client_id: int = Form(...),
    session_id: int = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Envia múltiplos arquivos (ou ZIPs) para o bucket S3.
    Caso algum arquivo seja ZIP, ele será descompactado e cada item será enviado individualmente.
    """
    temp_dir = tempfile.mkdtemp()
    uploaded_files = []

    try:
        manager = S3ManagerUpload(
            s3_connection=s3,
            client_name=str(client_id),
            session_name=str(session_id)
        )
        base_path = manager.path

        for file in files:
            local_path = os.path.join(temp_dir, file.filename)

            # Grava o arquivo temporariamente
            with open(local_path, "wb") as temp_file:
                shutil.copyfileobj(file.file, temp_file)

            if file.filename.lower().endswith(".zip"):
                try:
                    with zipfile.ZipFile(local_path, "r") as zip_ref:
                        for member in zip_ref.namelist():
                            if member.endswith("/"):
                                continue

                            extracted_path = os.path.join(temp_dir, member)
                            zip_ref.extract(member, path=temp_dir)

                            # Segurança: evita path traversal
                            if not _is_safe_path(temp_dir, extracted_path):
                                logger.warning(f"Tentativa de extração insegura detectada: {member}")
                                continue

                            uploaded = manager._upload_file(extracted_path, upload_prefix=base_path)
                            uploaded_files.append(uploaded)

                except zipfile.BadZipFile:
                    logger.error(f"Arquivo ZIP inválido: {file.filename}")
                    raise HTTPException(status_code=400, detail=f"O arquivo {file.filename} não é um ZIP válido.")
            else:
                uploaded = manager._upload_file(local_path, upload_prefix=base_path)
                uploaded_files.append(uploaded)

        return {"uploaded_files": uploaded_files}

    except Exception as e:
        logger.exception(f"Erro ao enviar arquivos para o S3: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar arquivos: {e}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@router_upload.delete("/delete/file", response_model=DirectoryOutput)
async def delete_file(request: FileData):
    """
    Deleta um arquivo específico no bucket S3 com base em client_id e session_id.
    """
    try:
        client_name = str(request.client_id)
        session_name = str(request.session_id)
        file_name = request.file_name

        deleter = S3DeleteFile(
            s3,
            client_name=client_name,
            session_name=session_name,
            file_name=file_name
        )

        file_path = deleter.file_path
        result = deleter.delete_file()

        status_msg = "not_found" if "não encontrado" in result.lower() else "success"

        return {
            "status": status_msg,
            "message": result,
            "path": file_path
        }

    except Exception as e:
        file_path = f"{request.client_id}/{request.session_id}/{request.file_name}"
        logger.exception(f"Erro ao deletar arquivo {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar arquivo: {e}")
