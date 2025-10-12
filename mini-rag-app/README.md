# RAG_assistant
A productionized version of RAG assistant for Q&A.

## Requirements
- Python 3.8 or later

## Install Python using MiniConda
1) Download and install MiniConda
2) Create a new environment
3) Activate
4) Use WSL-VSCode

## Installation
```bash
$pip install -r requirements.txt
```

## Setup environment variables
```bash
$ cp .env.example .env
```
set your environment secret keys in `.env` such as `OPENAI_API_KEY` and others

## Run FastAPI Server
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
## Postman collection might be needed


## Run Docker
```bash
$ cd docker
$ cp .env
```
- update `.env` with your credenitals
