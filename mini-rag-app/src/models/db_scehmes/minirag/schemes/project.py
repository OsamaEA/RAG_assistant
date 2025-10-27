from .minirag_base import SQLAlchmeyBase
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(SQLAlchmeyBase):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key = True, autoincrement=True)
    project_uid = Column(UUID(as_uuid=True), default = uuid.uuid4, unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    