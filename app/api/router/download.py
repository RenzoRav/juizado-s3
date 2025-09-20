from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.service.amazon_s3.push_docs import S3PushDocs
from app.service.amazon_s3.connection import s3
from app.utils.data import S3PathSession
import tempfile
import os

router_download = APIRouter(tags=['Download'])


@router_download.get("/download/file")
async def download_file(
    user_name: str,
    client_name: str,
    session_name: str,
    file_name: str
):
    """Baixa um arquivo específico"""
    try:
        s3_push = S3PushDocs(s3)
        prefix = S3PathSession(user_name, client_name, session_name).get_path_session()
        key = f"{prefix}/{file_name}"

        temp_dir = tempfile.mkdtemp()
        download_path = os.path.join(temp_dir, file_name)

        s3_push.download_file(key, download_path)

        return FileResponse(download_path, filename=file_name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_download.get("/download/session")
async def download_session(
    user_name: str,
    client_name: str,
    session_name: str
):
    """
    Baixa toda a sessão em uma pasta temporária
    nomeada como {client_name}_{session_name}_{datetime}
    """
    try:
        s3_push = S3PushDocs(s3)
        prefix = S3PathSession(user_name, client_name, session_name).get_path_session()

        folder_path = s3_push.download_folder(prefix, client_name, session_name)

        if not folder_path:
            raise HTTPException(status_code=404, detail="Nenhum arquivo encontrado na sessão")

        # Retorna a pasta temporária (no browser você precisaria compactar para download)
        return FileResponse(folder_path, filename=os.path.basename(folder_path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
