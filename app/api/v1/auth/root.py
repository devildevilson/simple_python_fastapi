from fastapi import APIRouter, Header, HTTPException, Depends, status, Request
import bcrypt
import jwt
import hashlib

from app.domain.models import User
from app.infra.user_container import UserContainer
from app.core.config import AppConfig
from app.core.logger import logger

router = APIRouter(prefix='/auth', tags=["auth"])

def make_hashed_password_string(pw: str):
  encoded_password = pw.encode("utf-8")
  salt = bcrypt.gensalt(rounds=12) # Generate a salt with a work factor of 12
  return (bcrypt.hashpw(encoded_password, salt)).decode("utf-8")

def sha256(string: str):
  return hashlib.sha256(string.encode('utf-8')).hexdigest()

def md5(string: str):
  return hashlib.md5(string.encode('utf-8')).hexdigest()

def hash(string: str): return sha256(string)

def make_digest_hash(username: str, realm: str, password: str):
  return hash(f"{username}:{realm}:{password}");

def check_pw_match(pw1: str, pw2: str):
  return bcrypt.checkpw(pw1.encode("utf-8"), pw2.encode("utf-8"))

@router.post("/register", tags=["auth"], status_code=status.HTTP_201_CREATED)
async def register_user(request: Request, data: User):
  logger.info(f"Got into {request.url.path}")
  # проверим существует ли юзер, если да то вывалим ошибку
  user = await UserContainer.get_user(data.username)
  if user:
    raise HTTPException(status_code=409, detail=f"'{data.username}' is already exists")
  hashed_pw = make_hashed_password_string(data.password)
  digest_hash = make_digest_hash(data.username, AppConfig.get("realm"), data.password)
  hashed_user = User(data.username, hashed_pw, digest_hash)
  # передадим в инфра юзера с шифрованным паролем
  status = await UserContainer.save_user(hashed_user)
  if not status:
    raise HTTPException(status_code=500, detail=f"Internal server erorr")
  return {"message": "Successful registration"}

# надо будет потом вынести jwt отдельно
@router.post("/login", tags=["auth"])
async def login_user(request: Request, data: User):
  logger.info(f"Got into {request.url.path}")
  # проверим существует ли юзер
  user = await UserContainer.get_user(data.username)
  if not user:
    raise HTTPException(status_code=403, detail="Forbidden")
  # сопоставим пароли и вернем jwt
  if not check_pw_match(data.password, user.password): 
    raise HTTPException(status_code=403, detail="Forbidden")
  encoded_jwt = jwt.encode({"username": data.username}, AppConfig.get("jwt_secret"), algorithm="HS256")
  return { "access_token": encoded_jwt, "token_type": "bearer"}

