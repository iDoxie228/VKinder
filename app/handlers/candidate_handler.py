from app.keyboards.candidate_keyboard import get_candidate_keyboard
from app.keyboards.main_keyboard import get_main_keyboard
from app.state.dialog_state import DialogState, get_session, reset_session

from app.use_cases.add_to_favorites import add_to_favorites
from app.use_cases.add_to_blacklist import add_to_blacklist
from app.use_cases.show_next_candidate import show_next_candidate

from infrastructure.db.repositories.blacklist_repository import BlacklistRepository
from infrastructure.db.repositories.candidate_photo_repository import CandidatePhotoRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.favorites_repository import FavoriteRepository
from infrastructure.db.repositories.shown_candidate_repository import ShownCandidateRepository
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.vk.photos_service import VKPhotosService

from app.handlers.candidate_parse import send_candidate_result

def _get_current_candidate_id(vk_user_id: int) -> int | None:
    session = get_session(vk_user_id)

    if session.state != DialogState.VIEWING_CANDIDATES:
        return None

    if not session.candidate_ids:
        return None

    if session.index >= len(session.candidate_ids):
        return None

    return session.candidate_ids[session.index]

def handle_next_candidate(
    vk_user_id: int,
    messages_service,
    user_repository: UserRepository,
    candidate_repository: CandidateRepository,
    shown_candidate_repository: ShownCandidateRepository,
    candidate_photo_repository: CandidatePhotoRepository,
    vk_photos_service: VKPhotosService,
) -> None:
    session = get_session(vk_user_id)

    if session.state != DialogState.VIEWING_CANDIDATES:
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message="Сначала начните поиск.",
            keyboard=get_main_keyboard(),
        )
        return

    session.index += 1

    if session.index >= len(session.candidate_ids):
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message="Кандидаты закончились",
            keyboard=get_main_keyboard(),
        )
        session.state = DialogState.IDLE
        return

    candidate_id = session.candidate_ids[session.index]

    result = show_next_candidate(
        app_user_id=session.app_user_id,
        candidate_id=candidate_id,
        vk_photo_service=vk_photos_service,
        shown_candidate_repository=shown_candidate_repository,
        candidate_photo_repository=candidate_photo_repository,
        user_repository=user_repository,
        candidate_repository=candidate_repository,
    )

    send_candidate_result(
        vk_user_id=vk_user_id,
        result=result,
        messages_service=messages_service,
    )


def handle_add_to_favorites(
    vk_user_id: int,
    messages_service,
    user_repository: UserRepository,
    candidate_repository: CandidateRepository,
    favorites_repository: FavoriteRepository,
    blacklist_repository: BlacklistRepository,
) -> None:
    session = get_session(vk_user_id)
    candidate_id = _get_current_candidate_id(vk_user_id)

    if candidate_id is None or session.app_user_id is None:
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message="Сначала выберите кандидата",
            keyboard=get_main_keyboard(),
        )
        return

    result = add_to_favorites(
        app_user_id=session.app_user_id,
        candidate_id=candidate_id,
        user_repository=user_repository,
        candidate_repository=candidate_repository,
        favorites_repository=favorites_repository,
        blacklist_repository=blacklist_repository,
    )

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message=result.message,
        keyboard=get_candidate_keyboard(),
    )


def handle_add_to_blacklist(
    vk_user_id: int,
    messages_service,
    user_repository: UserRepository,
    candidate_repository: CandidateRepository,
    favorites_repository: FavoriteRepository,
    blacklist_repository: BlacklistRepository,
    shown_candidate_repository: ShownCandidateRepository,
    candidate_photo_repository: CandidatePhotoRepository,
    vk_photos_service: VKPhotosService,
) -> None:
    session = get_session(vk_user_id)
    candidate_id = _get_current_candidate_id(vk_user_id)

    if candidate_id is None or session.app_user_id is None:
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message="Сначала выберите кандидата",
            keyboard=get_main_keyboard(),
        )
        return

    result = add_to_blacklist(
        app_user_id=session.app_user_id,
        candidate_id=candidate_id,
        user_repository=user_repository,
        candidate_repository=candidate_repository,
        favorites_repository=favorites_repository,
        blacklist_repository=blacklist_repository,
    )

    messages_service.send_text(
        user_id=vk_user_id,
        message=result.message,
    )

    handle_next_candidate(
        vk_user_id=vk_user_id,
        messages_service=messages_service,
        user_repository=user_repository,
        candidate_repository=candidate_repository,
        shown_candidate_repository=shown_candidate_repository,
        candidate_photo_repository=candidate_photo_repository,
        vk_photos_service=vk_photos_service,
    )


def handle_finish_search(
    vk_user_id: int,
    messages_service,
) -> None:
    reset_session(vk_user_id)

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message="Поиск завершён",
        keyboard=get_main_keyboard(),
    )