import uuid
import hashlib
import json
import os
import aiofiles as aiof

from app.domain.models import Task
from app.core.config import AppConfig

def create_uuid_from_string(val: str):
  hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
  return uuid.UUID(hex=hex_string)

def make_folder_path_from_uuid(id_handle: uuid.UUID):
  str_uuid_splited = str(id_handle).split("-")
  return f"{AppConfig.get("storage_path")}/{str_uuid_splited[0]}/{str_uuid_splited[1]}/{str_uuid_splited[2]}/{str_uuid_splited[3]}/{str_uuid_splited[4]}"

class TaskContainer:
  async def get(username: str, id: str | None = None):
    id_handle = create_uuid_from_string(username)
    path_folder = make_folder_path_from_uuid(id_handle)
    os.makedirs(path_folder, exist_ok=True)
    tasksdata_path = f"{path_folder}/tasks.json"
    try:
      async with aiof.open(tasksdata_path, "r") as file:
        content = await file.read()
        data = json.loads(content)
        if not id: return list(map(lambda v: Task(**v), data.values()))
        return [ Task(**data[id]) ]
    except FileNotFoundError:
      return []

  async def create(username: str, task: Task):
    id_handle = create_uuid_from_string(username)
    path_folder = make_folder_path_from_uuid(id_handle)
    os.makedirs(path_folder, exist_ok=True)
    tasksdata_path = f"{path_folder}/tasks.json"
    data = {}
    if os.path.exists(tasksdata_path):
      async with aiof.open(tasksdata_path, "r") as file:
        content = await file.read()
        data = json.loads(content)
    
    async with aiof.open(tasksdata_path, "w") as file:
      data[task.id] = vars(task)
      await file.write(json.dumps(data))
      await file.flush()
      return True
    return True

  async def modify(username: str, task: Task):
    id_handle = create_uuid_from_string(username)
    path_folder = make_folder_path_from_uuid(id_handle)
    os.makedirs(path_folder, exist_ok=True)
    tasksdata_path = f"{path_folder}/tasks.json"
    data = {}
    try:
      async with aiof.open(tasksdata_path, "r") as file:
        content = await file.read()
        data = json.loads(content)
    except FileNotFoundError:
      return False

    if not data.get(task.id, None): return False  

    try:
      async with aiof.open(tasksdata_path, "w") as file:
        for attr_name, attr_value in vars(task).items():
          if attr_name == "id": continue
          if attr_name.startswith("__"): continue
          if attr_value: data[task.id][attr_name] = attr_value
        await file.write(json.dumps(data))
        await file.flush()
        return True
    except FileNotFoundError:
      return False

  async def remove(username: str, id: str):
    id_handle = create_uuid_from_string(username)
    path_folder = make_folder_path_from_uuid(id_handle)
    os.makedirs(path_folder, exist_ok=True)
    tasksdata_path = f"{path_folder}/tasks.json"
    data = {}
    try:
      async with aiof.open(tasksdata_path, "r") as file:
        content = await file.read()
        data = json.loads(content)
    except FileNotFoundError:
      return False

    if not data.get(id, None): return False

    try:
      async with aiof.open(tasksdata_path, "w") as file:
        del data[id]
        await file.write(json.dumps(data))
        await file.flush()
        return True
    except FileNotFoundError:
      return False