with open("apps/api/src/main.py", "r") as f:
    content = f.read()

content = content.replace("from sse_starlette.sse import EventSourceResponse", "from sse_starlette.sse import EventSourceResponse\nfrom .evaluation_api import router as eval_router")

content = content.replace("app.add_middleware(", "app.include_router(eval_router)\n\napp.add_middleware(")

with open("apps/api/src/main.py", "w") as f:
    f.write(content)
