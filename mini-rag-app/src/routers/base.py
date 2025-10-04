from fastapi import FastAPI, APIRouter
import os 

base_router = APIRouter(
    prefix = "/api/v1",
    tags = ["api_v1"]
)

@base_router.get("/")
def welcome():
    app_name = os.getenv("APP_NAME")
    app_ver = os.getenv("APP_Version")

    return({"Message": os.getenv("APP_Version")})