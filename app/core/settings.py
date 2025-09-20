import os 

from dotenv import load_dotenv

from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))
class Configs(BaseSettings):
    S3_ENDPOINT_URL :str = os.getenv("S3_ENDPOINT_URL")
    AWS_ACCESS_KEY_ID :str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY:str = os.getenv("AWS_SECRET_ACCESS_KEY")
    REGION_NAME : str=os.getenv("REGION_NAME")
    BUCKET_NAME : str=os.getenv("BUCKET")
    ROOT1 :str=os.getenv("ROOT1")
    ROOT2 :str=os.getenv("ROOT2")
    ROOT3 :str=os.getenv("ROOT3")
    model_config = SettingsConfigDict(env_file=".env")  # correto para Pydantic 2.x

configs = Configs()
