from sqlalchemy import select, func
from sqlalchemy.orm import Session
from infrastructure.db.models import Blacklist, Candidate

class BlacklistRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_blacklist(self, app_user_id: int, candidate_id: int) -> Blacklist | None:
        stmt = select(Blacklist).where(
            Blacklist.app_user_id == app_user_id,
            Blacklist.candidate_id == candidate_id
            )
        return self.db.execute(statement=stmt).scalar_one_or_none()

    def add_to_blacklist(self, app_user_id: int, candidate_id: int) -> Blacklist:
        blacklist = self.get_blacklist(app_user_id, candidate_id)
        if blacklist: return blacklist
        
        blacklist = Blacklist(
            app_user_id = app_user_id,
            candidate_id = candidate_id
        )
        
        self.db.add(blacklist)
        self.db.commit()
        self.db.refresh(blacklist)

        return blacklist
    
    def remove_from_blacklist(self, app_user_id: int, candidate_id: int) -> bool:
        blacklist = self.get_blacklist(app_user_id, candidate_id)
        if blacklist is None: return False
                
        self.db.delete(blacklist)
        self.db.commit()

        return True
    
    def is_blacklisted(self, app_user_id: int, candidate_id: int) -> bool:
        blacklist = self.get_blacklist(app_user_id, candidate_id)
        return blacklist is not None
    
    def list_blacklist(self, app_user_id: int) -> list[Candidate]:
        stmt = (
            select(Candidate)
            .join(Blacklist, Blacklist.candidate_id == Candidate.id)
            .where(Blacklist.app_user_id == app_user_id)
            .order_by(Blacklist.created_at.desc())
        )

        return list(self.db.execute(statement=stmt).scalars().all())
    
    def count_blacklists(self, app_user_id: int) -> int:
        stmt = select(func.count(Blacklist.id)).where(Blacklist.app_user_id==app_user_id)
        return self.db.execute(statement=stmt).scalar_one()