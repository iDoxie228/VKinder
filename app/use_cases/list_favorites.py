from dataclasses import dataclass
from infrastructure.db.models import Candidate
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.repositories.favorites_repository import FavoriteRepository

@dataclass
class ListOfFavResult:
    success: bool
    favorites: list[Candidate]
    message: str

def get_list_favorites(
    app_user_id: int, 
    user_repository: UserRepository,
    favorites_repository: FavoriteRepository 
) -> ListOfFavResult:
    app_user = user_repository.get_by_id(app_user_id)
    if app_user is None:
        return ListOfFavResult(
            success=False,
            favorites=[],
            message="Пользователь не найден"
        )
    
    list_favorites = favorites_repository.list_favorites(app_user_id)
    if len(list_favorites) > 0:
        return ListOfFavResult(
            success=True,
            favorites=list_favorites,
            message="Список избранных успешно получен"
        )
    else:
        return ListOfFavResult(
            success=True,
            favorites=[],
            message="Список избранных пуст"
        )