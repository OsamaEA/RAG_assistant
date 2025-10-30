from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, status, Request
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
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_scehmes.minirag import DataChunk, Asset, Project
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum


data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: int, file: UploadFile,
                    app_settings: Settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(db_client = request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

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


    asset_model = await AssetModel.create_instance(db_client = request.app.db_client)
    asset_resource = Asset(
        asset_project_id=project.project_id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name= file_id,
        asset_size= os.path.getsize(file_path))

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(status_code = status.HTTP_200_OK,
        content = {"detail": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
                   "file_id": str(asset_record.asset_project_id),
                   "file_path": file_path,
                   "old_project_id": project_id,
                   "project_id": str(project.project_id)})


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest):
    #file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    chunk_model = await ChunkModel.create_instance(db_client = request.app.db_client)

    project_model = await ProjectModel.create_instance(db_client = request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # process all files if no file_id is provided
    asset_model = await AssetModel.create_instance(db_client = request.app.db_client)
    project_files_ids = []
    if process_request.file_id is not None:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.project_id, #get actual project id from database not the project_id
            asset_name=process_request.file_id
        )

        if asset_record is not None:
            project_files_ids = {asset_record.asset_id: asset_record.asset_name}
        else:
            return JSONResponse(
                status_code = status.HTTP_400_BAD_REQUEST,
                content = {"detail": ResponseSignal.FILE_ID_ERROR.value}
            )
    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.project_id, #get actual project id from database not the project_id
            asset_type=AssetTypeEnum.FILE.value)
        project_files_ids = {file_record.asset_id: file_record.asset_name for file_record in project_files}

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"detail": ResponseSignal.NO_FILES_FOUND.value}
        )
    process_controller = ProcessController(project_id=project_id)
    
    no_records = 0
    no_files = 0

    if do_reset == 1:
        deleted_count = await chunk_model.delete_chunks_by_project_id(project_id=project.project_id)
        logger.info(f"Deleted {deleted_count} chunks for project_id: {project.project_id}")


    for asset_id, file_id in project_files_ids.items():    
        file_content = process_controller.get_content_from_file(file_id=file_id)
        if file_content is None:
            logger.error(f"File not found or could not be loaded: {file_id}")
            continue
        file_chunks = process_controller.process_file_content(file_content=file_content,
                                                                file_id=file_id,
                                                                chunk_size=chunk_size,
                                                                overlap_size=overlap_size)  
        
        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code = status.HTTP_400_BAD_REQUEST,
                content = {"detail": ResponseSignal.PROCESSING_FAILED.value}
            )   
        
        file_chunks_records = [DataChunk(

            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset_id
        ) for i, chunk in enumerate(file_chunks)
        ]

            
        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records, batch_size=100)
        no_files += 1

    return JSONResponse(
        content = {
            "detail": ResponseSignal.PROECSSIGN_SUCCESS.value,
            "no_of_chunks": no_records,
            "processed_files": no_files
        })