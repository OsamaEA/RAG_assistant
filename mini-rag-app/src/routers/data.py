from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse
import os 
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
from controllers.ProcessController import ProcessController
from models import ResponseSignal
import aiofiles
import logging
logger = logging.getLogger("uvicorn.error")
from .schemes import ProcessRequest

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
    file_path, file_id = DataController().generate_unique_filename(original_filename=file.filename, project_id=project_id)

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
        content = {"detail": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
                   "file_id": file_id,
                   "file_path": file_path,
                   "project_id": project_id})

@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_content_from_file(file_id=file_id)
    file_chunks = process_controller.process_file_content(file_content=file_content,
                                                            file_id=file_id,
                                                            chunk_size=chunk_size,
                                                            overlap_size=overlap_size)  
    
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"detail": ResponseSignal.PROCESSING_FAILED.value}
        )   
    
    return file_chunks