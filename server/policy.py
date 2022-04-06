from typing import Dict
from pydantic import BaseModel

class Policy(BaseModel):
    id:str = None
    object_name:str = None
    request_id:int = None
    premium:int = None
    sum_insured:int = None
