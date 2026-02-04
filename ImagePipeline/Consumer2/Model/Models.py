from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func
from datetime import datetime

class Base(DeclarativeBase):
    pass

# Post Model
class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    imageUrl: Mapped[str] = mapped_column(String(1000), name="image_url", nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)

# Tag Model
class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime, name="created_at", default=func.now())

# PostTag Model
class PostTag(Base):
    __tablename__ = "post_tag"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime, name="created_at", default=func.now())
