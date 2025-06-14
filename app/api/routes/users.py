from fastapi import FastAPI,Depends
from fastapi import APIRouter
from ..services.user import UserService
from ..repositories.user import UserRepository
from typing import Annotated

users_router =APIRouter(prefix="/users",tags=["users"])

async def get_user_repository()->UserRepository:
    """
    Creates and returns a UserRepository instance
    """
    return UserRepository()

async def get_user_service(user_repository:UserRepository=Depends(get_user_repository))->UserService:
    """
    Creates and return a UserService instance with injected UserRepository
    """
    return UserService(user_repository)

UserServiceDep = Annotated[UserService,Depends(get_user_service)]


@users_router.get("/")
async def get_users(user:UserService=Depends(get_user_service)):
    """
    Create a new User
    """
    try:
        user = await user.repository.get_all()
        print(user)
        return user
    except RuntimeError as e:
        raise
