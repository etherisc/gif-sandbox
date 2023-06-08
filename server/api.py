import logging
from typing import List

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.openapi.utils import get_openapi

from server.category import FireCategory
from server.config import Config, PostConfig
from server.policy import Policy
from server.request import Request
from server.node import Node

app = FastAPI()
node = Node()

@app.get('/requests', response_model=int, tags=['Oracle'])
def get_oracle_requests():
    global node
    return node.requests

@app.get('/requests/{request_id}', response_model=int, tags=['Oracle'])
def get_oracle_request(request_id:str):
    try:
        global node
        return node.getRequest(request_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put('/requests/{request_id}/respond', tags=['Oracle'])
def respond_to_oracle_request(request_id:int, fire_category:FireCategory):
    try:
        global node
        node.sendResponse(request_id, fire_category)
    except ValueError as e:
        logging.error(e)
        raise HTTPException(status_code=404, detail=str(e))

@app.post('/policies', response_model=str, tags=['Policy'])
def apply_for_fire_policy(object_name: str, object_value:int, response:Response):
    try:
        global node
        process_id = node.applyForPolicy(object_name, object_value)
        response.status_code = status.HTTP_201_CREATED
        return str(process_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/policies/{process_id}', response_model=Policy, tags=['Policy'])
def get_fire_policy(process_id:str):
    try:
        global node
        return node.getPolicy(process_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put('/policies/{process_id}/expire', tags=['Policy'])
def expire_fire_policy(process_id:str):
    try:
        global node
        node.expirePolicy(process_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get('/config', response_model=Config, tags=['Config'])
def get_node_config():
    global node
    return node.config

@app.post('/config', response_model=Config, tags=['Config'])
def set_node_config(config: PostConfig):
    global node
    node.config = config
    return node.config

def custom_openapi():
    global node
    openapi_schema = get_openapi(
        title = 'Fire Insurance API',
        version = '0.1.0',
        description = "This is the OpenAPI for the Fire Insurance",
        routes = app.routes)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
