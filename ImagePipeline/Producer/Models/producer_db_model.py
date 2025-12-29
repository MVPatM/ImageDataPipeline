from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.dialects.mysql import MEDIUMBLOB, BIGINT, VARBINARY

class Base(DeclarativeBase):
    pass

class DeadLetter(Base):
    __tablename__ = "DeadLetter"
    
    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    key: Mapped[bytes] = mapped_column(VARBINARY(100))
    value: Mapped[bytes] = mapped_column(MEDIUMBLOB)
    topic: Mapped[str] = mapped_column(String(20))
    
"""
CREATE TABLE DeadLetter (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`key` VARBINARY(100) NOT NULL,
`value` MEDIUMBLOB NOT NULL,
`topic` VARCHAR(255) NOT NULL,
PRIMARY KEY(`id`)
)
"""
