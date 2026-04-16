from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models import Candidate, Blacklist, ShownCandidate


class CandidateRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, candidate_id: int) -> Candidate | None:
        return self.db.get(Candidate, candidate_id)

    def get_by_vk_candidate_id(self, vk_candidate_id: int) -> Candidate | None:
        stmt = select(Candidate).where(Candidate.vk_candidate_id == vk_candidate_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_many_by_ids(self, candidate_ids: Sequence[int]) -> list[Candidate]:
        if not candidate_ids:
            return []

        stmt = select(Candidate).where(Candidate.id.in_(candidate_ids))
        return list(self.db.execute(stmt).scalars().all())

    def get_many_by_vk_ids(self, vk_candidate_ids: Sequence[int]) -> list[Candidate]:
        if not vk_candidate_ids:
            return []

        stmt = select(Candidate).where(Candidate.vk_candidate_id.in_(vk_candidate_ids))
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        vk_candidate_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        sex: int | None = None,
        birth_date: Any | None = None,
        age: int | None = None,
        city_id: int | None = None,
        city_name: str | None = None,
        profile_url: str | None = None,
        is_closed: bool = False,
    ) -> Candidate:
        candidate = Candidate(
            vk_candidate_id=vk_candidate_id,
            first_name=first_name,
            last_name=last_name,
            sex=sex,
            birth_date=birth_date,
            age=age,
            city_id=city_id,
            city_name=city_name,
            profile_url=profile_url,
            is_closed=is_closed,
        )
        self.db.add(candidate)

        self.db.commit()
        self.db.refresh(candidate)

        return candidate

    def get_or_create(
        self,
        vk_candidate_id: int,
        defaults: dict[str, Any] | None = None
    ) -> tuple[Candidate, bool]:
        candidate = self.get_by_vk_candidate_id(vk_candidate_id)
        if candidate is not None:
            return candidate, False

        defaults = defaults or {}
        candidate = self.create(
            vk_candidate_id=vk_candidate_id,
            first_name=defaults.get("first_name"),
            last_name=defaults.get("last_name"),
            sex=defaults.get("sex"),
            birth_date=defaults.get("birth_date"),
            age=defaults.get("age"),
            city_id=defaults.get("city_id"),
            city_name=defaults.get("city_name"),
            profile_url=defaults.get("profile_url"),
            is_closed=defaults.get("is_closed", False)
        )
        return candidate, True

    def update(
        self,
        candidate: Candidate,
        **kwargs: Any,
    ) -> Candidate:
        forbidden_kwargs = {"id", "created_at", "vk_candidate_id"}
        for field_name, value in kwargs.items():
            if field_name in forbidden_kwargs:
                continue
            if hasattr(candidate, field_name):
                setattr(candidate, field_name, value)

        self.db.commit()
        self.db.refresh(candidate)
        return candidate


    def get_available_for_user(
        self,
        app_user_id: int,
        limit: int = 20
    ) -> list[Candidate]:
        
        stmt = select(Candidate).where(Candidate.is_closed.is_(False)) # исключаем закрытые профили

        blacklist_query = (
            select(Blacklist.candidate_id)
            .where(Blacklist.app_user_id == app_user_id)
        )

        shown_query = (
            select(ShownCandidate.candidate_id)
            .where(ShownCandidate.app_user_id == app_user_id)
        )

        stmt = (
            stmt.where(Candidate.id.not_in(blacklist_query))
            .where(Candidate.id.not_in(shown_query))
            .order_by(Candidate.id.asc())
            .limit(limit)
        )

        return list(self.db.execute(stmt).scalars().all())
    
    def delete(self, candidate_id: int) -> bool:
        candidate = self.get_by_id(candidate_id)
        if candidate is None:
            return False

        self.db.delete(candidate)
        self.db.commit()
        return True