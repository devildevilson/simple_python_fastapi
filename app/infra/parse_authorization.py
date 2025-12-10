from fastapi import Request, Header, HTTPException, status
import hashlib
import uuid

from app.infra.nonce_container import NonceContainer
from app.infra.user_container import UserContainer
from app.core.config import AppConfig

HASH_TYPE_STR = "SHA-256"
#HASH_TYPE_STR = "MD5"

def parse_digest(token: str):
  fin_list = dict(map(lambda v: tuple(list(map(lambda v: v.strip().replace('"', ''), v.split('=', 1)))), list(map(lambda v: v.strip(), token.split(",")))))
  return fin_list

def sha256(string: str):
  return hashlib.sha256(string.encode('utf-8')).hexdigest()

def md5(string: str):
  return hashlib.md5(string.encode('utf-8')).hexdigest()

def hash(string: str): return sha256(string)

async def challenge_digest_and_get_username(request: Request, token: str):
  digest_data = parse_digest(token)

  cnonce = digest_data.get("cnonce", None)
  qop = digest_data.get("qop", None)
  realm = digest_data.get("realm", None)
  nonce = digest_data.get("nonce", None)
  cnonce = digest_data.get("cnonce", None)
  nc = digest_data.get("nc", None)
  response = digest_data.get("response", None)
  username = digest_data.get("username", None)
  counter = 0 if not nc else int(nc)

  if not realm or realm != AppConfig.get("realm"):
    raise HTTPException(status_code=403, detail="Forbidden")
  if not nc or not nc.isdigit():
    raise HTTPException(status_code=403, detail="Forbidden")
  if not cnonce:
    raise HTTPException(status_code=403, detail="Forbidden")
  if not response:
    raise HTTPException(status_code=403, detail="Forbidden")
  if not qop or qop != "auth":
    raise HTTPException(status_code=403, detail="Forbidden")
  if not nonce or not NonceContainer.validate(nonce, counter):
    raise HTTPException(status_code=403, detail="Forbidden")
  if not username:
    raise HTTPException(status_code=403, detail="Forbidden")
  user = await UserContainer.get_user(username)
  if not user:
    raise HTTPException(status_code=403, detail="Forbidden")

  #HA1 = hash(f"{user.digest_hash}:{nonce}:{cnonce}")
  HA1 = user.digest_hash
  HA2 = hash(f"{request.method}:{request.url.path}")
  response = hash(f"{HA1}:{nonce}:{counter:08d}:{cnonce}:{qop}:{HA2}")

  if response != digest_data["response"]:
    raise HTTPException(status_code=403, detail="Forbidden")
  return user.username

async def parse_authorization(request: Request, auth: str | None = Header(None, alias="Authorization")):
  username = None

  if auth and auth.startswith("Bearer "):
    token = auth.removeprefix("Bearer ")
    try:
      payload = jwt.decode(token, AppConfig.get("jwt_secret"), algorithms="HS256")
      username = payload["username"]
    except Exception as e:
      raise HTTPException(status_code=403, detail="Forbidden")
  
  if auth and auth.startswith("Digest "):
    token = auth.removeprefix("Digest ")
    username = await challenge_digest_and_get_username(request, token)

  if not auth or not username:
    nonce = NonceContainer.generate()
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Auth failed", headers={"WWW-Authenticate": f"Digest realm=\"{AppConfig.get("realm")}\", nonce=\"{nonce}\", algorithm={HASH_TYPE_STR}, qop=auth"})
  
  return username