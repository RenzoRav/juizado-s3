from fastapi import FastAPI
from app.api.router.crud import router_crud
from app.api.router.upload import router_upload
from app.api.router.download import router_download

app = FastAPI(
    title="API Nucleo Juridico - S3",
    version="1.0.0",
    description="API para manipular arquivos no S3"
)
app.include_router(router_crud)
app.include_router(router_upload)
app.include_router(router_download)