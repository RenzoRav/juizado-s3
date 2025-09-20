from fastapi import (
    HTTPException , 
    APIRouter , 
    Query , 
)

from app.api.models.input import (
    SessionData , 
    ClientData , 
    UserData
)

from app.service.amazon_s3.create import (
    S3CreatePathClient , 
    S3CreatePathUser , 
    S3CreatePathSession
)

from app.service.amazon_s3.delete import (
    S3DeletePathClient , 
    S3DeletePathUser , 
    S3DeletePathSession , 
    S3DeleteFile
)

from app.api.models.output import DirectoryOutput

from app.service.amazon_s3.connection import s3

from app.core.logger import logger


router_crud = APIRouter(tags=["Objects"])

@router_crud.get("/s3/healthcheck")
async def s3_healthcheck():
    try:
        buckets = s3.client.list_buckets()
        bucket_names = [bucket["Name"] for bucket in buckets.get("Buckets", [])]

        return {
            "status": "success",
            "message": "Conexão com S3 estabelecida com sucesso.",
            "available_buckets": bucket_names
        }
    except Exception as e:
        logger.error(f"Erro ao verificar conexão com S3: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao conectar com o S3"
    )

@router_crud.post("/create/directory/user", response_model=DirectoryOutput)
async def directory_user(request_input: UserData):
    try:
        path_creator = S3CreatePathUser(
            s3,
            user_name=request_input.user_name.lower()
        )

        created_path = path_creator.create_path()

        if "já existia" in created_path:
            return {
                "status": "exists",
                "message": "Diretório do usuário já existe.",
                "path": created_path
            }

        return {
            "status": "success",
            "message": "Diretório do usuário criado com sucesso!",
            "path": created_path
        }

    except Exception as e:
        logger.error(f"Erro interno ao criar pasta do usuário: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar pasta do usuário: {e}"
        )


@router_crud.post("/create/directory/client", response_model=DirectoryOutput)
async def directory_client(request_input: ClientData):
    try:
        path_creator = S3CreatePathClient(
            s3,
            user_name=request_input.user_name.lower(),
            client_name=request_input.client_name.lower()
        )

        created_path = path_creator.create_path()

        if "já existia" in created_path:
            return {
                "status": "exists",
                "message": "Diretório do cliente já existe.",
                "path": created_path
            }

        return {
            "status": "success",
            "message": "Diretório do cliente criado com sucesso!",
            "path": created_path
        }

    except Exception as e:
        logger.error(f"Erro interno ao criar pasta do cliente: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar pasta do cliente: {e}"
        )


@router_crud.post("/create/directory/session", response_model=DirectoryOutput)
async def directory_session(request_input: SessionData):
    try:
        path_creator = S3CreatePathSession(
            s3,
            user_name=request_input.user_name.lower(),
            client_name=request_input.client_name.lower(),
            session_name=request_input.session_name.lower()
        )

        created_path = path_creator.create_path()

        if "já existia" in created_path:
            return {
                "status": "exists",
                "message": "Diretório da sessão já existe.",
                "path": created_path
            }

        return {
            "status": "success",
            "message": "Diretório da sessão criado com sucesso!",
            "path": created_path
        }

    except Exception as e:
        logger.error(f"Erro interno ao criar pasta da sessão: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar pasta da sessão: {e}"
        )

    
@router_crud.delete("/delete/directory/user", response_model=DirectoryOutput)
async def delete_user(request_input: UserData):
    try:
        deleter = S3DeletePathUser(
            s3,
            user_name=request_input.user_name.lower()
        )
        deleted_path = deleter.delete_path()

        # Verifica se foi realmente deletado ou não existia
        if "não encontrado" in deleted_path:
            status_msg = "not_found"
            message = f"Diretório do usuário {request_input.user_name} não encontrado."
        else:
            status_msg = "success"
            message = f"Diretório do usuário {request_input.user_name} deletado com sucesso."

        return {
            "status": status_msg,
            "message": message,
            "path": deleted_path
        }

    except Exception as e:
        logger.error(f"Erro ao deletar pasta do usuário: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar pasta do usuário: {e}"
        )



@router_crud.delete("/delete/directory/client", response_model=DirectoryOutput)
async def delete_client(request_input: ClientData):
    try:
        deleter = S3DeletePathClient(
            s3,
            user_name=request_input.user_name.lower(),
            client_name=request_input.client_name.lower()
        )
        deleted_path = deleter.delete_path()

        if "não encontrado" in deleted_path:
            status_msg = "not_found"
            message = f"Diretório do cliente {request_input.client_name} não encontrado."
        else:
            status_msg = "success"
            message = f"Diretório do cliente {request_input.client_name} deletado com sucesso."

        return {
            "status": status_msg,
            "message": message,
            "path": deleted_path
        }

    except Exception as e:
        logger.error(f"Erro ao deletar pasta do cliente: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar pasta do cliente: {e}"
        )


@router_crud.delete("/delete/directory/session", response_model=DirectoryOutput)
async def delete_session(request_input: SessionData):
    try:
        deleter = S3DeletePathSession(
            s3,
            user_name=request_input.user_name.lower(),
            client_name=request_input.client_name.lower(),
            session_name=request_input.session_name.lower()
        )
        deleted_path = deleter.delete_path()

        if "não encontrado" in deleted_path:
            status_msg = "not_found"
            message = f"Diretório da sessão {request_input.session_name} não encontrado."
        else:
            status_msg = "success"
            message = f"Diretório da sessão {request_input.session_name} deletado com sucesso."

        return {
            "status": status_msg,
            "message": message,
            "path": deleted_path
        }

    except Exception as e:
        logger.error(f"Erro ao deletar pasta da sessão: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar pasta da sessão: {e}"
        )


