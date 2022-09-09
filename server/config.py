from pydantic import BaseModel

class Config(BaseModel):
    product_address: str = None
    oracle_address: str = None
    firecoin_address: str = None
    mnemonic: str = None
    product_account_no:int = None
    oracle_account_no:int = None
    customer_account_no:int = None
    riskpool_wallet_account_no:int = None
    investor_account_no:int = None

class PostConfig(BaseModel):
    registry_address: str = None
    mnemonic: str = None
