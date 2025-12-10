import os
import secrets

def read_file(name: str):
  with open(name, "r") as file:
    return file.read().strip()

CONFIG_PATH_PREFIX = "./"
JWT_SECRET_FILE_NAME = CONFIG_PATH_PREFIX + "jwt_secret"
REALM_STR_FILE_NAME = CONFIG_PATH_PREFIX + "realm"
STORAGE_DEFAULT_PATH = CONFIG_PATH_PREFIX + "storage"

data = {}

if not os.path.isfile(JWT_SECRET_FILE_NAME):
  secret = secrets.token_urlsafe()
  with open(JWT_SECRET_FILE_NAME, "w") as file:
    file.write(secret)

if not os.path.isfile(REALM_STR_FILE_NAME):
  realm = "http-test@example.com"
  with open(REALM_STR_FILE_NAME, "w") as file:
    file.write(realm)

class AppConfig:
  def get(key: str):
    return data.get(key, None)

  def reload():
    data["jwt_secret"] = read_file(JWT_SECRET_FILE_NAME)
    data["realm"] = read_file(REALM_STR_FILE_NAME)
    data["nonce_time"] = 300
    data["storage_path"] = STORAGE_DEFAULT_PATH


AppConfig.reload()