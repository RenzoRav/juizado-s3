import tempfile
import zipfile
import shutil
import os

from typing import List

from fastapi import (
    APIRouter, 
    UploadFile,
    HTTPException , 
    File ,
    Form
)
from app.service.ocr.apply import S3ManagerUpload 
from app.service.amazon_s3.delete import S3DeleteFile
from app.api.models.input import FileData 
from app.api.models.output import UploadOutput , DirectoryOutput

from app.service.amazon_s3.connection import s3

from app.core.logger import logger

router_upload = APIRouter(tags=["Upload"])

@router_upload.post("/upload/files", response_model=UploadOutput)
async def upload_files(
    user_name: str = Form(...),
    client_name: str = Form(...),
    session_name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    temp_dir = tempfile.mkdtemp()
    uploaded_files = []

    try:
        manager = S3ManagerUpload(
            s3_connection=s3, 
            user_name=user_name, 
            client_name=client_name, 
            session_name=session_name
        )
        base_path = manager.path

        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            if file.filename.lower().endswith(".zip"):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    for f in zip_ref.namelist():
                        if not f.endswith("/"):
                            extracted_path = zip_ref.extract(f, path=temp_dir)
                            uploaded_files.append(manager._upload_file(extracted_path, upload_prefix=base_path))
            else:
                uploaded_files.append(manager._upload_file(file_path, upload_prefix=base_path))

        return {"uploaded_files": uploaded_files}

    except Exception as e:
        logger.error(f"Erro ao enviar arquivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@router_upload.delete("/delete/file", response_model=DirectoryOutput)
async def delete_file(request: FileData):
    try:
        user_name = request.user_name.lower()
        client_name = request.client_name.lower()
        session_name = request.session_name.lower()
        file_name = request.file_name.lower()

        deleter = S3DeleteFile(
            s3, 
            user_name=user_name,
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
        file_path = f"{request.user_name}/{request.client_name}/{request.session_name}/{request.file_name}"
        logger.error(f"Erro ao deletar arquivo {file_path}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar arquivo: {e}"
        )
