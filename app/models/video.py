import uuid
from sqlalchemy import Column, String, DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from app.db.database import Base

class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String, nullable=False)
    status = Column(Enum(VideoStatus), default=VideoStatus.PENDING)
    
    # Caminhos no NFS (que configuramos na branch anterior)
    input_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)
    
    # Metadados
    original_size_mb = Column(Float, nullable=True)
    final_size_mb = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)