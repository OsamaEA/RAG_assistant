from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 524288  # Default chunk size of 512KB
    overlap_size: Optional[int] = 20  # Default no overlap
    do_reset: Optional[bool] = False