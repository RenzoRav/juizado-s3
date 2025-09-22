from datetime import datetime
import tempfile
import os

from botocore.exceptions import ClientError

from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse

from app.api.models.output import DownloadFileRequest 
from app.api.models.input import DownloadSession

from app.service.amazon_s3.push_docs import S3PushDocs
from app.service.amazon_s3.connection import s3

from app.utils.data import S3PathSession

from app.core.logger import logger

router_download = APIRouter(tags=['Download'])


@router_download.post("/download/file")
async def download_file(request: DownloadFileRequest):
    s3_push = S3PushDocs(s3)
    prefix = S3PathSession(request.user_name, request.client_name, request.session_name).get_path_session()
    key = f"{prefix}/{request.file_name}"

    temp_dir = tempfile.mkdtemp()
    download_path = os.path.join(temp_dir, request.file_name)

    try:
        s3_push.download_file(key, download_path)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ["404", "NoSuchKey"]:
            logger.warning(f"Arquivo {key} não encontrado")
            raise HTTPException(status_code=404, detail=f"Arquivo {request.file_name} não encontrado")
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(
        download_path,
        filename=request.file_name,
        media_type="application/octet-stream"
    )


@router_download.post("/download/session")
async def download_session(request_input: DownloadSession):
    try:   
        client_name = request_input.client_name.lower()
        session_name = request_input.session_name.lower()
        unic_name = request_input.unic_name 
        unic_client = request_input.unic_client
        unic_session = request_input.unic_session

        s3_push = S3PushDocs(s3)
        prefix = S3PathSession(unic_name, unic_client, unic_session).get_path_session()

        try:
            folder_path = s3_push.download_folder(prefix, client_name, session_name)
        except HTTPException as e:
            if e.status_code == 404:
                raise
            raise HTTPException(status_code=500, detail=str(e))

        zip_name = f"{client_name}_{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(tempfile.gettempdir(), zip_name)

        s3_push.make_zip_from_folder(folder_path, zip_path)

        return FileResponse(zip_path, filename=zip_name, media_type="application/zip")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))