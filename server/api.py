import logging

from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi

from server.category import FireCategory
from server.config import Config, PostConfig
from server.policy import Policy
from server.request import Request
from server.node import Node

app = FastAPI()
node = Node()

@app.get('/requests', response_model=List[Request], tags=['Oracle Request'])
def get_oracle_requests():
    global node
    return node.requests

@app.get('/requests/{request_id}', response_model=Request, tags=['Oracle Request'])
def get_oracle_request(request_id:int):
    try:
        global node
        return node.getRequest(request_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put('/requests/{request_id}/respond', tags=['Oracle Request'])
def respond_to_oracle_request(request_id:int, fire_category:FireCategory):
    try:
        global node
        node.sendResponse(request_id, fire_category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get('/policies', response_model=List[Policy], tags=['Policy'])
def get_fire_policies():
    global node
    return node.policies

@app.post('/policies', response_model=Policy, tags=['Policy'])
def apply_for_fire_policy(objectName: str, premium:int):
    try:
        global node
        return node.applyForPolicy(objectName, premium)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/policies/{policy_id}', response_model=Policy, tags=['Policy'])
def get_fire_policy(policy_id:str):
    try:
        global node
        return node.getPolicy(policy_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put('/policies/{policy_id}/expire', tags=['Policy'])
def expire_fire_policy(policy_id:str):
    try:
        global node
        node.expirePolicy(policy_id)
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
        title = 'Fire Insurane API',
        version = '0.1.0',
        description = node.info(),
        routes = app.routes)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
