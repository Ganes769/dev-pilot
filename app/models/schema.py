from pydantic import BaseModel
from typing import List
class RepoIndexRequest(BaseModel):
    repo_path:str
class RepoIndexResponse(BaseModel):
    repo_name:str
    files_indexed:int
    files:List[str]