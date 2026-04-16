from sqlalchemy import select
from sqlalchemy.orm import Session
from infrastructure.db.models import Candidate, ShownCandidate

class ShownCandidateRepository: 
    def __init__(self, db: Session):
        self.db = db

    def get_shown_candidate(self, app_user_id: int, candidate_id: int) -> ShownCandidate | None:
        stmt = select(ShownCandidate).where(
            ShownCandidate.candidate_id == candidate_id,
            ShownCandidate.app_user_id == app_user_id
            )
        return self.db.execute(statement=stmt).scalar_one_or_none()

    def mark_as_shown(self, app_user_id: int, candidate_id: int) -> ShownCandidate:
        shown_candidate = self.get_shown_candidate(app_user_id, candidate_id)
        if shown_candidate: return shown_candidate

        shown_candidate = ShownCandidate(
            app_user_id = app_user_id,
            candidate_id = candidate_id
        )

        self.db.add(shown_candidate)
        self.db.commit()
        self.db.refresh(shown_candidate)

        return shown_candidate
    
    def is_shown(self, app_user_id: int, candidate_id: int) -> bool:
        return self.get_shown_candidate(app_user_id, candidate_id) is not None
    
    def list_shown_candidates(self, app_user_id: int) -> list[Candidate]:
        stmt = (
            select(Candidate)
            .join(ShownCandidate, ShownCandidate.candidate_id == Candidate.id)
            .where(ShownCandidate.app_user_id == app_user_id)
            .order_by(ShownCandidate.shown_at.desc())
        )

        return list(self.db.execute(statement=stmt).scalars().all())

    def list_shown_ids(self, app_user_id: int) -> list[int]:
        stmt = select(ShownCandidate.candidate_id).where(
            ShownCandidate.app_user_id == app_user_id
        )
        return list(self.db.execute(stmt).scalars().all())
    
