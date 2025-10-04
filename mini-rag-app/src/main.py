from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from routers import base

app = FastAPI()
app.include_router(base.base_router)

