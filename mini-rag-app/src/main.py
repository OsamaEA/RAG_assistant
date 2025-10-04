from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from routers import base, data

app = FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)
