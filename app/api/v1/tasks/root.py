import secrets
import hashlib
import uuid
from fastapi import APIRouter, Header, HTTPException, Depends, status, Request
from datetime import datetime

from app.domain.models import User,Task
from app.infra.task_container import TaskContainer
from app.infra.user_container import UserContainer
from app.infra.nonce_container import NonceContainer
from app.infra.parse_authorization import parse_authorization
from app.core.logger import logger

def obj_to_dict(obj):
  return dict(filter(lambda k,v: not k.startswith("__"), dict(vars(obj)).items()))

router = APIRouter(prefix='/tasks', tags=["tasks"])

@router.post("/", summary="Создадим задачу")
async def create_task(request: Request, task: Task, username = Depends(parse_authorization)):
  logger.info(f"Got into {request.url.path}")
  # сначала мы хотим убедиться что перед нами User
  # потом мы хотим отдать данные в хранилище задач
  # чтобы не плодить сущности возьмем уникальный uuid в качестве id 
  # скорее всего он недостаточно уникальный и его бы замешать с чем нибудь по хорошему
  task.id = uuid.uuid4().hex
  if not task.created_at:
    task.created_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
  if not task.completed:
    task.completed = False
  await TaskContainer.create(username, task)
  return { "tasks": [ task ] }

@router.get("/", summary="Получим все существующие задачи")
async def get_tasks(request: Request, username = Depends(parse_authorization)):
  logger.info(f"Got into {request.url.path}")
  # сначала мы хотим убедиться что перед нами User
  # потом получить список всех задач
  tasks_arr = await TaskContainer.get(username)
  remade_tasks = list(map(lambda v: vars(v), tasks_arr))
  return { "tasks": remade_tasks }

@router.get("/{task_id}", summary="Получим конкретную задачу")
async def get_task(request: Request, task_id: str, username = Depends(parse_authorization)):
  logger.info(f"Got into {request.url.path}")
  # сначала мы хотим убедиться что перед нами User
  # тут мы хотим получить задачу по id
  tasks_arr = await TaskContainer.get(username, task_id)
  remade_tasks = list(map(lambda v: vars(v), tasks_arr))
  return { "tasks": remade_tasks }

@router.patch("/{task_id}", summary="Поменяем данные по задаче")
async def modify_task(request: Request, task_id: str, task: Task, username = Depends(parse_authorization)):
  logger.info(f"Got into {request.url.path}")
  # сначала мы хотим убедиться что перед нами User
  # тут мы поменяем название или статус задачи (а время?)
  task.id = task_id
  status = await TaskContainer.modify(username, task)
  return { "status": status }

@router.delete("/{task_id}", summary="Удалим задачу")
async def delete_task(request: Request, task_id: str, username = Depends(parse_authorization)):
  logger.info(f"Got into {request.url.path}")
  # сначала мы хотим убедиться что перед нами User
  # уберем задачу из списка
  status = await TaskContainer.remove(username, task_id)
  return { "status": status }