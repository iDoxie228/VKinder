from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from infrastructure.db.models import CandidatePhoto

class CandidatePhotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_photo(self, candidate_id: int, vk_photo_id: int) -> CandidatePhoto | None:
        stmt = select(CandidatePhoto).where(
            CandidatePhoto.vk_photo_id == vk_photo_id,
            CandidatePhoto.candidate_id == candidate_id
            )

        return self.db.execute(statement=stmt).scalar_one_or_none()

    def add_photo(self, candidate_id: int, vk_photo_id: int, photo_url: str | None, likes_amount: int = 0) -> CandidatePhoto:
        candidate_photo = self.get_photo(candidate_id, vk_photo_id)
        if candidate_photo: return candidate_photo

        candidate_photo = CandidatePhoto(
            candidate_id = candidate_id,
            vk_photo_id = vk_photo_id,
            photo_url = photo_url,
            likes_amount = likes_amount
        )

        self.db.add(candidate_photo)
        self.db.commit()
        self.db.refresh(candidate_photo)

        return candidate_photo
    
    def get_top_photos(self, candidate_id: int, limit: int = 3) -> list[CandidatePhoto]:
        stmt = (
            select(CandidatePhoto)
            .where(CandidatePhoto.candidate_id == candidate_id)
            .order_by(CandidatePhoto.likes_amount.desc())
            .limit(limit)
        )

        return list(self.db.execute(stmt).scalars().all())
    
    def delete_by_candidate_id(self, candidate_id: int) -> bool:
        stmt = delete(CandidatePhoto).where(
            CandidatePhoto.candidate_id == candidate_id
        )
        
        res = self.db.execute(stmt)
        self.db.commit()
        
        return res.rowcount > 0
    
    def add_many(self, candidate_id: int, photos_data: list[dict]) -> list[CandidatePhoto]:
        added_photos = []

        for photo in photos_data:
            photo = self.add_photo(
                candidate_id=candidate_id,
                vk_photo_id=photos_data["vk_photo_id"],
                photo_url=photos_data["photo_url"],
                likes_amount=photos_data.get("likes_amount", 0)
            )
        added_photos.append(photo)

        return added_photos