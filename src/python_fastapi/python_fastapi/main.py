from fastapi import FastAPI
# from prometheus_fastapi_instrumentator import Instrumentator

from .routers import payload_router, static_router

app = FastAPI()

app.include_router(static_router, prefix="/static")
app.include_router(payload_router, prefix="/payload")

# instrumentator = Instrumentator().instrument(app)

# @app.on_event("startup")
# async def _startup():
#     instrumentator.expose(app)

@app.get("/")
async def root():
    return {"message": "ok"}
