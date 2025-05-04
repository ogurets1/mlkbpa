from pydantic_settings import BaseSettings 

class Settings(BaseSettings):
    upload_dir: str = "./uploads"
    results_dir: str = "./results"
    model_path: str = "./models/best.pt"
    
    class Config:
        env_file = ".env"

settings = Settings()