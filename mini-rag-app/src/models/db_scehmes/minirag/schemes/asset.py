from .minirag_base import SQLAlchmeyBase
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Index

class Asset(SQLAlchmeyBase):
    __tablename__ = "assets"
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(UUID(as_uuid=True), default = uuid.uuid4, unique=True, nullable=False)
    
    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=True)
    asset_config = Column(JSONB, nullable=True)

    asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    project = relationship("Project", back_populates="Assets")

    __table_args__ = (
        Index("ix_asset_project_id", asset_project_id),
        Index("ix_asset_type", asset_type)
    )