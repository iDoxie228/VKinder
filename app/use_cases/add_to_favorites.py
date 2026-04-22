from dataclasses import dataclass
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.favorites_repository import FavoriteRepository
from infrastructure.db.repositories.blacklist_repository import BlacklistRepository

@dataclass
class AddToFavResult:
    success: bool
    message: str

def add_to_favorites(
        app_user_id: int, 
        candidate_id: int,
        user_repository: UserRepository,
        candidate_repository: CandidateRepository,
        favorites_repository: FavoriteRepository,
        blacklist_repository: BlacklistRepository
) -> AddToFavResult:
    
    app_user = user_repository.get_by_id(app_user_id)
    if app_user is None:
        return AddToFavResult(
            success=False,
            message="Пользователь не найден"
        )
    
    candidate = candidate_repository.get_by_id(candidate_id)
    if candidate is None:
        return AddToFavResult(
            success=False,
            message="Кандидат не найден"
        )
    
    is_favorite = favorites_repository.is_favorite(app_user_id, candidate_id)
    if is_favorite:
        return AddToFavResult(
            success=False,
            message="Кандидат уже был добавлен в избранное"
        )
    
    is_blacklisted = blacklist_repository.is_blacklisted(app_user_id, candidate_id)
    if is_blacklisted:
        return AddToFavResult(
            success=False,
            message="Этот кандидат был добавлен в ЧС"
        )

    favorites_repository.add_to_favorites(app_user_id, candidate_id)
    return AddToFavResult(
            success=True,
            message=f"Кандидат {candidate.first_name} добавлен в избранное"
        )


