import os

class Config:
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    # Add more config as needed

