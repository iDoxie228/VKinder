from app.keyboards.candidate_keyboard import get_candidate_keyboard
from app.keyboards.main_keyboard import get_main_keyboard
from app.keyboards.search_keyboard import get_cancel_keyboard
from app.state.dialog_state import DialogState, get_session
from app.handlers.candidate_parse import send_candidate_result

from app.use_cases.start_search import start_search
from app.use_cases.show_next_candidate import show_next_candidate

from infrastructure.db.repositories.blacklist_repository import BlacklistRepository
from infrastructure.db.repositories.candidate_photo_repository import CandidatePhotoRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.shown_candidate_repository import ShownCandidateRepository
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.vk.photos_service import VKPhotosService
from infrastructure.vk.search_service import VkSearchService
from infrastructure.vk.user_service import VKUsersService

from app.keyboards.buttons import (
    SEX_ANY, 
    SEX_MALE, 
    SEX_FEMALE, 
    START_SEARCH
)


def _parse_sex(text: str) -> int | None:
    text = text.strip().lower()

    if text == "женщина":
        return 1

    if text == "мужчина":
        return 2

    if text == "неважно":
        return 0

    return None


def _parse_age(text: str) -> int | None:
    try:
        age = int(text.strip())
    except ValueError:
        return None

    if age < 0 or age > 150:
        return None

    return age


def handle_search_step(
    vk_user_id: int,
    text: str,
    messages_service,
    user_repository: UserRepository,
    candidate_repository: CandidateRepository,
    blacklist_repository: BlacklistRepository,
    shown_candidate_repository: ShownCandidateRepository,
    candidate_photo_repository: CandidatePhotoRepository,
    vk_search_service: VkSearchService,
    vk_users_service: VKUsersService,
    vk_photos_service: VKPhotosService,
) -> None:
    session = get_session(vk_user_id)

    if session.state == DialogState.WAITING_SEX:
        sex = _parse_sex(text)

        if sex is None:
            messages_service.send_text_with_keyboard(
                user_id=vk_user_id,
                message=f"Выберите пол кнопкой: {SEX_FEMALE}, {SEX_MALE} или {SEX_ANY}.",
                keyboard=get_cancel_keyboard(),
            )
            return

        session.sex = sex
        session.state = DialogState.WAITING_AGE_FROM

        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message="Введите минимальный возраст, например: 18",
            keyboard=get_cancel_keyboard(),
        )
        return

    if session.state == DialogState.WAITING_AGE_FROM:
        age_from = _parse_age(text)

        if age_from is None:
            messages_service.send_text_with_keyboard(
                user_id=vk_user_id,
                message="Введите возраст от 0 до 150",
                keyboard=get_cancel_keyboard(),
            )
            return

        session.age_from = age_from
        session.state = DialogState.WAITING_AGE_TO

        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message="Введите максимальный возраст, например: 35",
            keyboard=get_cancel_keyboard(),
        )
        return

    if session.state == DialogState.WAITING_AGE_TO:
        age_to = _parse_age(text)

        if age_to is None:
            messages_service.send_text_with_keyboard(
                user_id=vk_user_id,
                message="Введите возраст от 0 до 150",
                keyboard=get_cancel_keyboard(),
            )
            return

        if session.age_from is not None and age_to < session.age_from:
            messages_service.send_text_with_keyboard(
                user_id=vk_user_id,
                message="Возраст «до» не может быть меньше возраста «от». Введите возраст до ещё раз.",
                keyboard=get_cancel_keyboard(),
            )
            return

        session.age_to = age_to

        search_result = start_search(
            vk_user_id=vk_user_id,
            sex=session.sex,
            age_from=session.age_from,
            age_to=session.age_to,
            user_repository=user_repository,
            candidate_repository=candidate_repository,
            blacklist_repository=blacklist_repository,
            shown_candidate_repository=shown_candidate_repository,
            vk_search_service=vk_search_service,
            vk_users_service=vk_users_service,
        )

        if not search_result.success:
            session.state = DialogState.IDLE
            session.candidate_ids = []
            session.index = 0
            session.app_user_id = search_result.app_user_id

            messages_service.send_text_with_keyboard(
                user_id=vk_user_id,
                message=search_result.message,
                keyboard=get_main_keyboard(),
            )
            return

        session.app_user_id = search_result.app_user_id
        session.candidate_ids = search_result.candidate_ids
        session.index = 0
        session.state = DialogState.VIEWING_CANDIDATES

        first_candidate_id = session.candidate_ids[session.index]

        candidate_result = show_next_candidate(
            app_user_id=session.app_user_id,
            candidate_id=first_candidate_id,
            vk_photo_service=vk_photos_service,
            shown_candidate_repository=shown_candidate_repository,
            candidate_photo_repository=candidate_photo_repository,
            user_repository=user_repository,
            candidate_repository=candidate_repository,
        )

        send_candidate_result(
            vk_user_id=vk_user_id,
            result=candidate_result,
            messages_service=messages_service,
        )
        return

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message=f"Сейчас поиск не запущен. Нажмите {START_SEARCH}.",
        keyboard=get_main_keyboard(),
    )
