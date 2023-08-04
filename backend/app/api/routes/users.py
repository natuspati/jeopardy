from fastapi import Depends, APIRouter, HTTPException, Body, Security
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.models.user import UserCreate, UserUpdate, UserInDB, UserPublic

from app.db.repositories.users import UserRepository

from app.models.token import AccessToken
from app.services import auth_service

router = APIRouter()


@router.post("/", response_model=UserPublic, name="user:register", status_code=HTTP_201_CREATED)
async def register_new_user(
        new_user: UserCreate = Body(),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserPublic:
    created_user = await user_repo.register_new_user(new_user=new_user)
    
    access_token = AccessToken(
        access_token=auth_service.create_access_token_for_user(user=created_user),
        token_type="bearer"
    )
    
    return UserPublic.model_construct(**created_user.model_dump(), access_token=access_token)


@router.post("/login/token/", response_model=AccessToken, name="user:login-email-and-password")
async def user_login_with_email_and_password(
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
) -> AccessToken:
    user = await user_repo.authenticate_user(email=form_data.username, password=form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Authentication was unsuccessful.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AccessToken(access_token=auth_service.create_access_token_for_user(user=user), token_type="bearer")
    
    return access_token


@router.get("/me/", response_model=UserPublic, name="user:get-current-user")
async def get_currently_authenticated_user(
        current_user: UserInDB = Security(get_current_active_user, scopes=["me"])
) -> UserPublic:
    cur = UserPublic.model_construct(
        **current_user.model_dump(exclude={"password", "salt"}),
        access_token=None
    )
    return cur
