import cloudinary

cloudinary.config(
    cloud_name="dsjusqa4p",
    api_key="599877185773136",
    api_secret="VFeBRMltUi1d8Jz_aCwOGLF4b8k"
)


from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

settings = Settings()