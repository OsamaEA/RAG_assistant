from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse
import os 
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponseSignal
import aiofiles
import logging
logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                    app_settings: Settings = Depends(get_settings)):
    
    is_valid, signal = DataController().valdiate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(status_code = status.HTTP_400_BAD_REQUEST,
        content = {"detail": signal})

    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path = DataController().generate_unique_filename(original_filename=file.filename, project_id=project_id)

    try:
        # Uploading the file as chunks to avoid memory issues with large files
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk:= await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content = {"detail": app_settings.FILE_UPLOAD_FAILED.value})

    return JSONResponse(status_code = status.HTTP_200_OK,
        content = {"detail": ResponseSignal.FILE_UPLOADED_SUCCESS.value})

