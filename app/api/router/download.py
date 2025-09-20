from datetime import datetime
import tempfile
import os

from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse

from app.api.models.output import DownloadFileRequest 
from app.api.models.input import SessionData

from app.service.amazon_s3.push_docs import S3PushDocs
from app.service.amazon_s3.connection import s3

from app.utils.data import S3PathSession


router_download = APIRouter(tags=['Download'])


@router_download.post("/download/file")
async def download_file(request: DownloadFileRequest):
    try:
        s3_push = S3PushDocs(s3)
        prefix = S3PathSession(request.user_name, request.client_name, request.session_name).get_path_session()
        key = f"{prefix}/{request.file_name}"

        temp_dir = tempfile.mkdtemp()
        download_path = os.path.join(temp_dir, request.file_name)

        s3_push.download_file(key, download_path)

        return FileResponse(
            download_path,
            filename=request.file_name,
            media_type="application/octet-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_download.get("/download/session")
async def download_session(
    request_input = SessionData
):
    try:   
        user_name = request_input.user_name.lower()
        client_name = request_input.client_name.lower()
        session_name = request_input.session_name.lower()
        s3_push = S3PushDocs(s3)
        prefix = S3PathSession(user_name, client_name, session_name).get_path_session()

        # Baixa a pasta da sessão
        folder_path = s3_push.download_folder(prefix, client_name, session_name)

        if not folder_path:
            raise HTTPException(status_code=404, detail="Nenhum arquivo encontrado na sessão")

        zip_name = f"{client_name}_{session_name}_{datetime.now()}.zip"
        zip_path = os.path.join(tempfile.gettempdir(), zip_name)

        # Compacta a pasta
        s3_push.make_zip_from_folder(folder_path, zip_path)

        return FileResponse(zip_path, filename=zip_name, media_type="application/zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))