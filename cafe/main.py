from fastapi import FastAPI
from cafe.protocols.api import router

app = FastAPI(title="Cafe")
app.include_router(router)
