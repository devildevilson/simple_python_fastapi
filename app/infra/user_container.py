import uuid
import hashlib
import json
import os
import aiofiles as aiof

from app.domain.models import User
from app.core.config import AppConfig

def create_uuid_from_string(val: str):
  hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
  return uuid.UUID(hex=hex_string)

def make_folder_path_from_uuid(id_handle: uuid.UUID):
  str_uuid_splited = str(id_handle).split("-")
  return f"{AppConfig.get("storage_path")}/{str_uuid_splited[0]}/{str_uuid_splited[1]}/{str_uuid_splited[2]}/{str_uuid_splited[3]}/{str_uuid_splited[4]}"

class UserContainer:
  async def get_user(username: str):
    id_handle = create_uuid_from_string(username)
    path_folder = make_folder_path_from_uuid(id_handle)
    userdata_path = f"{path_folder}/user.json"
    try:
      async with aiof.open(userdata_path, "r") as file:
        content = await file.read()
        if not content: return None
        data = json.loads(content)
        return User(**data)
    except FileNotFoundError:
      return None

  async def save_user(user: User):
    id_handle = create_uuid_from_string(user.username)
    path_folder = make_folder_path_from_uuid(id_handle)
    os.makedirs(path_folder, exist_ok=True)
    userdata_path = f"{path_folder}/user.json"
    try:
      async with aiof.open(userdata_path, "x") as file:
        content = json.dumps(vars(user))
        await file.write(content)
        await file.flush()
        return True
    except FileExistsError:
      return False