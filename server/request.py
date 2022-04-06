from typing import Dict
from pydantic import BaseModel

class Response(BaseModel):
    open:bool = True
    fire_category:str = None

class Request(BaseModel):
    log_id:str = None
    address:str = None
    event:str = None
    args:Dict = None
    response:Response = None
