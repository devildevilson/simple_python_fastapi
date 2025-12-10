from dataclasses import dataclass
import datetime

@dataclass
class User:
  username: str
  password: str
  digest_hash: str | None = None
  def to_dict(self):
    return { "username": self.username, "password": self.password, "digest_hash": self.digest_hash }

@dataclass
class Task:
  id: str | None = None
  title: str | None = None
  completed: bool | None = None
  created_at: datetime.datetime | None = None
  def to_dict(self):
    return { "id": self.id, "title": self.title, "completed": self.completed, "created_at": self.created_at }