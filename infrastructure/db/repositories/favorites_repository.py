from sqlalchemy import select, func
from sqlalchemy.orm import Session
from infrastructure.db.models import Favorite, Candidate

class FavoriteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_favorite(self, app_user_id: int, candidate_id: int) -> Favorite | None:
        stmt = select(Favorite).where(
            Favorite.app_user_id == app_user_id,
            Favorite.candidate_id == candidate_id
            )
        return self.db.execute(statement=stmt).scalar_one_or_none()

    def add_to_favorites(self, app_user_id: int, candidate_id: int) -> Favorite:
        favorite = self.get_favorite(app_user_id, candidate_id)
        if favorite: return favorite
        
        favorite = Favorite(
            app_user_id = app_user_id,
            candidate_id = candidate_id
        )
        
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)

        return favorite
    
    def remove_from_favorites(self, app_user_id: int, candidate_id: int) -> bool:
        favorite = self.get_favorite(app_user_id, candidate_id)
        if favorite is None: return False
                
        self.db.delete(favorite)
        self.db.commit()

        return True
    
    def is_favorite(self, app_user_id: int, candidate_id: int) -> bool:
        favorite = self.get_favorite(app_user_id, candidate_id)
        return favorite is not None
    
    def list_favorites(self, app_user_id: int) -> list[Candidate]:
        stmt = (
            select(Candidate)
            .join(Favorite, Favorite.candidate_id == Candidate.id)
            .where(Favorite.app_user_id == app_user_id)
            .order_by(Favorite.created_at.desc())
        )

        return list(self.db.execute(statement=stmt).scalars().all())
    
    def count_favorites(self, app_user_id: int) -> int:
        stmt = select(func.count(Favorite.id)).where(Favorite.app_user_id==app_user_id)
        return self.db.execute(statement=stmt).scalar_one()