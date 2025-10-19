from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0


class SearchRequest(BaseModel):
    text: str
    limit: Optional[int] = 10
    #top_k: Optional[int] = 5
    #use_generation: Optional[int] = 0
    #generation_params: Optional[dict] = {}
