from pydantic import BaseModel
from typing import List
class RepoIndexRequest(BaseModel):
    repo_path:str
class RepoIndexResponse(BaseModel):
    repo_name:str
    files_indexed:int
    files:List[str]
class ChunckPreview(BaseModel):
    file_path:str
    chunck_index:int
    text_preview:str
class RepoChunckResponse(BaseModel):
    repo_name:str
    total_files:int
    total_chuncks:int
    chunck_preview:List[ChunckPreview]
class RepoChunckRequest(BaseModel):
    repo_path:str
    chunck_size:int=1000
    overlap:int=1000

