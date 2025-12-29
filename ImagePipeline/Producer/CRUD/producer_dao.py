from ImagePipeline.Producer.producer_db_model import DeadLetter
from sqlalchemy import select, delete
from typing import Generator

class DeadLetterDAO:
    def __init__(self, session):
        self.session = session
        
    def add_dead_letter(self, key, value, topic) -> None:
        data = DeadLetter(key=key, value=value, topic=topic)
        self.session.add(data)
        self.session.commit()
        
    def get_dead_letter(self, batch_size: int = 100) -> Generator:
        last_seen_id = 0
        
        while True:
            stmt = (
                select(DeadLetter)
                .where(DeadLetter.id > last_seen_id)
                .order_by(DeadLetter.id)
                .limit(batch_size)
            )
            
            batch = self.session.scalars(stmt).all()
            
            if not batch:
                break
            
            yield batch
            last_seen_id = batch[-1].id
            
        self.session.commit()
        
    def delete_dead_letter(self, key: bytes) -> None:
        data = self.session.query(DeadLetter).filter(DeadLetter.key == key).first()
       
        if data:
            stmt = delete(DeadLetter).where(DeadLetter.key == key)
            self.session.execute(stmt)
            self.session.commit()
