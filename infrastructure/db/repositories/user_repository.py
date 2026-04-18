from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models import AppUser

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> AppUser | None:
        return self.db.get(AppUser, user_id)
    
    def get_by_vk_user_id(self, vk_user_id: int) -> AppUser | None:
        stmt = select(AppUser).where(AppUser.vk_user_id == vk_user_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def create(
            self, 
            vk_user_id: int,
            first_name: str | None = None,
            last_name: str | None = None,
            sex: int | None = None,
            birth_date: Any | None = None,
            age: int | None = None,
            city_id: int | None = None,
            city_name: str | None = None,
            profile_url: str | None = None
            ) -> AppUser:
        app_user = AppUser(
            vk_user_id = vk_user_id,
            first_name = first_name,
            last_name = last_name,
            sex = sex,
            birth_date = birth_date,
            age = age,
            city_id = city_id,
            city_name = city_name,
            profile_url = profile_url
        )

        self.db.add(app_user)
        self.db.commit()
        self.db.refresh(app_user)

        return app_user

    def get_or_create(
            self,
            vk_user_id: int,
            defaults: dict[str, Any] | None = None
    ) -> tuple[AppUser, bool]:
        app_user = self.get_by_vk_user_id(vk_user_id)
        if app_user: return app_user, False

        defaults = defaults or {}

        app_user = self.create(
            vk_user_id=vk_user_id,
            first_name=defaults.get("first_name"),
            last_name = defaults.get("last_name"),
            sex = defaults.get("sex"),
            birth_date = defaults.get("birth_date"),
            age = defaults.get("age"),
            city_id = defaults.get("city_id"),
            city_name = defaults.get("city_name"),
            profile_url = defaults.get("profile_url")
        )

        return app_user, True
    
    def update(
            self,
            app_user: AppUser,
            **kwargs: Any
    ) -> AppUser:
        forbidden_kwargs = {"id", "created_at", "vk_user_id"}
        for field_name, value in kwargs.items():
            if field_name in forbidden_kwargs:
                continue
            if hasattr(app_user, field_name):
                setattr(app_user, field_name, value)
        
        self.db.commit()
        self.db.refresh(app_user)
        return app_user
    
    def delete(
            self,
            user_id: int,
    ) -> bool:
        app_user = self.get_by_id(user_id)
        if app_user is None:
            return False
        
        self.db.delete(app_user)
        self.db.commit()
        return True