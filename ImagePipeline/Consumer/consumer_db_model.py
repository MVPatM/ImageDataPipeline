from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.mysql import BIGINT
from datetime import datetime
from sqlalchemy import String, DateTime, func

class Base(DeclarativeBase):
    pass

class ImageData(Base):
    __tablename__ = "ImageData"
    
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    s3_url: Mapped[str] = mapped_column(String(100))
    image_class: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, server_default=func.now())
    
    """
    create table ImageData(
        `id` bigint unsigned NOT NULL AUTO_INCREMENT, 
        `s3_url` VARCHAR(100) NOT NULL,
        `image_class` VARCHAR(100) NOT NULL,
        `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
        primary key (`id`)
    );
    """
