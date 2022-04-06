from typing import Dict
from pydantic import BaseModel

class Request(BaseModel):
    log_id:str = None
    address:str = None
    event:str = None
    args:Dict = None
    open:bool = True
    fire_category:str = None
