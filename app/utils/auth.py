import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config import Config

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify basic auth credentials.
    Returns True if credentials are valid, raises HTTPException otherwise.
    """
    try:
        correct_username = secrets.compare_digest(credentials.username, Config.BASIC_AUTH_USERNAME)
        correct_password = secrets.compare_digest(credentials.password, Config.BASIC_AUTH_PASSWORD)

        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        return True
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

