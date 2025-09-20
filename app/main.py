from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router.crud import router_crud
from app.api.router.upload import router_upload

from app.api.router.download import router_download

app = FastAPI(
    title="API Nucleo Juridico - S3",
    version="1.0.0",
    description="API para manipular arquivos no S3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, troque "*" por ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router_crud)
app.include_router(router_upload)
app.include_router(router_download)