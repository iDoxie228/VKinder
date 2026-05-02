from dataclasses import dataclass

from infrastructure.db.models import Candidate
from infrastructure.db.repositories.blacklist_repository import BlacklistRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.shown_candidate_repository import ShownCandidateRepository
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.vk.search_service import VkSearchService
from infrastructure.vk.user_service import VKUsersService
@dataclass
class StartSearchResult:
    success: bool
    message: str
    candidate_ids: list[int]

def start_search(
    vk_user_id: int,
    sex: int,
    age_from: int,
    age_to: int,
    vk_search_service: VkSearchService,
    vk_users_service: VKUsersService,
    blacklist_repository: BlacklistRepository,
    shown_candidate_repository: ShownCandidateRepository,
    user_repository: UserRepository,
    candidate_repository: CandidateRepository,        
) -> StartSearchResult:
    user_data = vk_users_service.get_user_profile(vk_user_id)

    city_id = user_data.get("city_id")
    city_name = user_data.get("city_name")
    
    if city_id is None:
        return StartSearchResult(
            success=False,
            message="Укажите свой город в профиле или введите его вручную",
            app_user_id=None,
            candidate_ids=[],
        )
    
    app_user, _ = user_repository.get_or_create(
        vk_user_id=vk_user_id,
        defaults={
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "sex": user_data.get("sex"),
            "birth_date": user_data.get("birth_date"),
            "age": user_data.get("age"),
            "city_id": city_id,
            "city_name": city_name,
            "profile_url": user_data.get("profile_url"),
        },
    )

    user_repository.update(
        app_user,
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        sex=user_data.get("sex"),
        birth_date=user_data.get("birth_date"),
        age=user_data.get("age"),
        city_id=city_id,
        city_name=city_name,
        profile_url=user_data.get("profile_url"),
    )

    raw_candidates = vk_search_service.search_candidates(
        city_id=city_id,
        sex=sex,
        age_from=age_from,
        age_to=age_to,
    )

    if not raw_candidates:
        return StartSearchResult(
            success=False,
            message=f"Кандидаты в городе {city_name or city_id} по заданным критериям не найдены",
            app_user_id=app_user.id,
            candidate_ids=[],
        )
    
    blacklisted_candidates = blacklist_repository.list_blacklist(app_user.id)
    blacklisted_ids = {candidate.id for candidate in blacklisted_candidates}

    shown_ids = set(shown_candidate_repository.list_shown_ids(app_user.id))

    saved_candidate_ids: list[int] = []

    for candidate_data in raw_candidates:
        candidate, _ = candidate_repository.get_or_create(
            vk_candidate_id=candidate_data["vk_candidate_id"],
            defaults={
                "first_name": candidate_data.get("first_name"),
                "last_name": candidate_data.get("last_name"),
                "sex": candidate_data.get("sex"),
                "birth_date": candidate_data.get("birth_date"),
                "age": candidate_data.get("age"),
                "city_id": candidate_data.get("city_id"),
                "city_name": candidate_data.get("city_name"),
                "profile_url": candidate_data.get("profile_url"),
                "is_closed": candidate_data.get("is_closed", False),
            },
        )

        if candidate.id in blacklisted_ids:
            continue

        if candidate.id in shown_ids:
            continue

        if candidate.is_closed:
            continue

        if candidate.vk_candidate_id == vk_user_id:
            continue

        saved_candidate_ids.append(candidate.id)

    if not saved_candidate_ids:
        return StartSearchResult(
            success=False,
            message="Нет новых кандидатов для показа",
            app_user_id=app_user.id,
            candidate_ids=[],
        )
    
    return StartSearchResult(
        success=True,
        message=f"Найдено кандидатов в городе {city_name}: {len(saved_candidate_ids)}",
        app_user_id=app_user.id,
        candidate_ids=saved_candidate_ids,
    )