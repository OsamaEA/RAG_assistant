from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, status, Request
from fastapi.responses import JSONResponse
from routers.schemes.nlp_scheme import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers.NLPController import NLPController
from models import ResponseSignal

import logging
logger = logging.getLogger("uvicorn.error")


nlp_router = APIRouter(
    prefix = "/api/v1/nlp",
    tags = ["api_v1", "nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str,
                        push_request: PushRequest):
    
    project_model = await ProjectModel.create_instance(db_client= request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        logger.error(f"Project {project_id} not found.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
    
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                      generation_client=request.app.generation_client,
                                      embedding_client=request.app.embedding_client,
                                      template_parser=request.app.template_parser)
    

    chunk_model = await ChunkModel.create_instance(db_client= request.app.db_client)
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0
    
    while has_records:
        chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)
        if len(chunks):
            page_no += 1
            
        if not chunks or len(chunks) == 0:
            has_records = False
            break
        
        chunk_ids = list(range(idx, idx + len(chunks)))
        idx += len(chunks)

        is_inserted = nlp_controller.index_into_vector_db(project=project,
                                                    chunks=chunks,
                                                    do_reset= bool(push_request.do_reset),
                                                    chunk_ids=chunk_ids)
        if not is_inserted:
            logger.error(f"Failed to index project {project_id} into vector database.")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={"signal": ResponseSignal.FAILED_TO_INSERT.value})
        inserted_items_count += len(chunks)
        
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"inserted_items_count": inserted_items_count})



@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model = await ProjectModel.create_instance(db_client= request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        logger.error(f"Project {project_id} not found.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
    
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                      generation_client=request.app.generation_client,
                                      embedding_client=request.app.embedding_client,
                                      template_parser=request.app.template_parser)
    
    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"collection_info": collection_info})

@nlp_router.post("/index/search/{project_id}")
async def get_project_index_info(request: Request, project_id: str, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(db_client= request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        logger.error(f"Project {project_id} not found.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
    
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                      generation_client=request.app.generation_client,
                                      embedding_client=request.app.embedding_client,
                                      template_parser=request.app.template_parser)
    
    results = nlp_controller.search_vector_db_collection(project=project,
                                                        text=search_request.text,
                                                        limit=search_request.limit)
    if not results:
        logger.error(f"Search in project {project_id} returned no results.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.VECTOR_DB_SEARCH_FAILED.value})
        
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"signal": ResponseSignal.VECTOR_DB_SEARCH_SUCCESS.value,
                                  "results": results})


@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client= request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        logger.error(f"Project {project_id} not found.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value})
    
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                      generation_client=request.app.generation_client,
                                      embedding_client=request.app.embedding_client,
                                      template_parser=request.app.template_parser)

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(project=project,
                                                                          query=search_request.text,
                                                                          limit=search_request.limit)

    if not answer:
        logger.error(f"Answer generation failed for project {project_id}.")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.ANSWER_GENERATION_FAILED.value})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"signal": ResponseSignal.ANSWER_GENERATION_SUCCESS.value,
                                  "answer": answer,
                                  "full_prompt": full_prompt,
                                  "chat_history": chat_history})
