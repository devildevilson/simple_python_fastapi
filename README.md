# simple_python_fastapi

Запуск:
```
uvicorn main:app --reload
```

Эндпоинты:
```
POST /auth/register
POST /auth/login

POST   /tasks
GET    /tasks
GET    /tasks/{task_id}
PATCH  /tasks/{task_id}
DELETE /tasks/{task_id}

GET /metrics/progress
```

Использую SHA-256 хэш функцию, она поддерживается в версии curl-8.6.0_3. Подробности [тут](https://github.com/curl/curl/issues/6302) и [тут](https://github.com/curl/curl/issues/13056)
Примеры curl запросов:
```
$ curl -X POST http://localhost:8000/auth/register -H 'Content-Type: application/json' -d '{ "username":"newconfig2", "password": "newconfig2" }'
{"message":"Successful registration"}

$ curl -X GET http://localhost:8000/metrics/progress --digest -u newconfig2:newconfig2
{"user":"newconfig2","completed":0,"total":0,"progress":100}

$ curl http://localhost:8000/tasks/ --digest -u newconfig2:newconfig2
{"tasks":[]}

$ curl -X POST http://localhost:8000/tasks/ --digest -u newconfig2:newconfig2 -H 'Content-Type: application/json' -d '{ "title":"task6" }'
{"tasks":[{"id":"78e8795b893c470ca4bea84dd2575287","title":"task6","completed":false,"created_at":"2025-12-09T22:40:39"}]}

$ curl -X PATCH http://localhost:8000/tasks/78e8795b893c470ca4bea84dd2575287 --digest -u newconfig2:newconfig2 -H 'Content-Type: application/json' -d '{ "completed":true }'
{"status":true}

$ curl -X GET http://localhost:8000/metrics/progress --digest -u newconfig2:newconfig2
{"user":"newconfig2","completed":1,"total":1,"progress":100}

$ ./curl -X DELETE http://localhost:8000/tasks/78e8795b893c470ca4bea84dd2575287 --digest -u newconfig2:newconfig2
{"status":true}
```