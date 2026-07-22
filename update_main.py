import os

with open("apps/api/src/main.py", "r") as f:
    content = f.read()

import_str = "from .db.models import Job\n"
new_import_str = "from .db.models import Job, Base\nfrom .db.database import engine\n"

content = content.replace(import_str, new_import_str)

startup_event = """
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
"""

if "@app.on_event(\"startup\")" not in content:
    content = content.replace("app = FastAPI(title=\"Nutrition Scanner API\", version=\"1.0.0\")\n", "app = FastAPI(title=\"Nutrition Scanner API\", version=\"1.0.0\")\n" + startup_event + "\n")

with open("apps/api/src/main.py", "w") as f:
    f.write(content)
