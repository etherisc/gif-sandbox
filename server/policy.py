from typing import Dict
from pydantic import BaseModel

class Policy(BaseModel):
    id:str = None
    object_name:str = None
    premium:int = None
    premium_paid:int = None
    sum_insured:int = None
    application_state:int = None
    policy_state:int = None
    claims_count:int = None
    payout_amount:int = None
