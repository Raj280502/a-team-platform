from pydantic import BaseModel
from typing import List


class BackendContract(BaseModel):
    must_exist: List[str]          # real file paths only
    must_expose_routes: List[str]  # "METHOD /path"


class SystemContract(BaseModel):
    backend: BackendContract
