from dataclasses import dataclass
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.favorites_repository import FavoriteRepository
from infrastructure.db.repositories.blacklist_repository import BlacklistRepository

@dataclass
class AddToBlacklistResult:
    success: bool
    message: str

def add_to_blacklist(
        app_user_id: int, 
        candidate_id: int,
        user_repository: UserRepository,
        candidate_repository: CandidateRepository,
        favorites_repository: FavoriteRepository,
        blacklist_repository: BlacklistRepository
) -> AddToBlacklistResult:
    
    app_user = user_repository.get_by_id(app_user_id)
    if app_user is None:
        return AddToBlacklistResult(
            success=False,
            message="Пользователь не найден"
        )
    
    candidate = candidate_repository.get_by_id(candidate_id)
    if candidate is None:
        return AddToBlacklistResult(
            success=False,
            message="Кандидат не найден"
        )
    
    is_blacklisted = blacklist_repository.is_blacklisted(app_user_id, candidate_id)
    if is_blacklisted:
        return AddToBlacklistResult(
            success=False,
            message="Этот кандидат уже был добавлен в ЧС"
        )

    is_favorite = favorites_repository.is_favorite(app_user_id, candidate_id)
    if is_favorite:
        return AddToBlacklistResult(
            success=False,
            message="Этот кандидат добавлен у вас в избранное"
        )    

    blacklist_repository.add_to_blacklist(app_user_id, candidate_id)
    return AddToBlacklistResult(
            success=True,
            message=f"Кандидат {user_repository.get_by_id(app_user_id).first_name} добавлен в ЧС"
        )


