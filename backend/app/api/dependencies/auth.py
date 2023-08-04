from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from app.core.config import SECRET_KEY, API_PREFIX
from app.models.user import UserInDB
from app.api.dependencies.database import get_repository
from app.db.repositories.users import UserRepository
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{API_PREFIX}/users/login/token/",
    scopes={
        "resources": "Modify Category/Question resources.",
        "me": "Read information about the current user."
    },
)


async def get_user_from_token(
        *,
        security_scopes: SecurityScopes,
        token: str = Depends(oauth2_scheme),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> Optional[UserInDB]:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    try:
        jwt_credentials = auth_service.get_username_from_token(
            token=token,
            secret_key=str(SECRET_KEY),
            authenticate_value=authenticate_value
        )
    except Exception as e:
        raise e
    
    if not check_user_has_required_scopes(
            required_scopes=security_scopes.scopes, user_scopes=jwt_credentials.scopes
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    
    user = await user_repo.get_user_by_username(username=jwt_credentials.username)
    
    return user


def get_current_active_user(
        current_user: UserInDB = Depends(get_user_from_token)
) -> Optional[UserInDB]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authenticated user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is disabled.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


def check_user_has_required_scopes(
        required_scopes: List[str],
        user_scopes: List[str]
) -> bool:
    for scope in required_scopes:
        if scope not in user_scopes:
            return False
    return True
