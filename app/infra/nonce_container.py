import secrets
import time

from app.core.config import AppConfig

nonce_store = {}

class NonceContainer:
  def generate():
    nonce = secrets.token_urlsafe()
    nonce_store[nonce] = (0, time.time())
    return nonce

  def validate(nonce: str, counter: int):
    cur_time = time.time()
    pair = nonce_store.get(nonce, None)
    if not pair: return False
    nc, cur = pair
    if cur_time - cur > AppConfig.get("nonce_time"):
      nonce_store[nonce] = None
      return False
    if nc >= counter:
      nonce_store[nonce] = None
      return False
    nonce_store[nonce] = (counter, cur_time)
    return True