from fastapi import FastAPI, APIRouter
from app.api.v1.auth.root import router as auth_router
from app.api.v1.tasks.root import router as tasks_router
from app.api.v1.metrics.root import router as metrics_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(metrics_router)

@app.get("/")
def root():
  return {"message": "Hello Bigger Applications!"}