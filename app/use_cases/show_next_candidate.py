from dataclasses import dataclass
from infrastructure.db.models import Candidate
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.candidate_photo_repository import CandidatePhotoRepository
from infrastructure.db.repositories.shown_candidate_repository import ShownCandidateRepository
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.vk.photos_service import VKPhotosService

@dataclass
class ShowNextResult:
    success: bool
    message: str
    candidate: Candidate | None
    photos: list[dict] 

def show_next_candidate(
        app_user_id: int,
        candidate_id: int,
        vk_photo_service: VKPhotosService,
        shown_candidate_repository: ShownCandidateRepository,
        candidate_photo_repository: CandidatePhotoRepository,
        user_repository: UserRepository,
        candidate_repository: CandidateRepository,
) -> ShowNextResult:
    app_user = user_repository.get_by_id(app_user_id)

    if app_user is None:
        return ShowNextResult(
            success=False,
            message="Пользователь не найден",
            candidate=None,
            photos=[]
        )
    
    candidate  = candidate_repository.get_by_id(candidate_id)

    if candidate is None:
        return ShowNextResult(
            success=False,
            message="Кандидат не найден",
            candidate=None,
            photos=[]
        )
    
    shown_candidate_repository.mark_as_shown(app_user.id, candidate.id)

    photos = vk_photo_service.get_top_photos(candidate.vk_candidate_id)

    if not photos:
        return ShowNextResult(
            success=True,
            message="У пользователя нет доступных фото",
            candidate=candidate,
            photos=[]
        )  

    candidate_photo_repository.add_many(candidate_id=candidate.id, photos_data=photos)

    return ShowNextResult(
            success=True,
            message="У пользователя нет доступных фото",
            candidate=candidate,
            photos=photos
        ) 