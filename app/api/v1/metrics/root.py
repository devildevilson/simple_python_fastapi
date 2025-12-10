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

router = APIRouter(prefix='/metrics', tags=["metrics"])

@router.get("/progress", summary="Получим прогресс пользователя по задачам")
async def get_progress(request: Request, username = Depends(parse_authorization)):
  logger.info(f"Got into {request.url.path}")
  # сначала мы хотим убедиться что перед нами User
  # тут мы хотим посчитать два числа и разделить одно и другое
  tasks = await TaskContainer.get(username)
  total_count = len(tasks)
  completed_count = 0
  for t in tasks:
    if t.completed: completed_count += 1
  progress = 100 if total_count == 0 else ((completed_count / total_count) * 100)
  return { "user": username, "completed": completed_count, "total": total_count, "progress": progress }

