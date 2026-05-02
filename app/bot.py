from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from infrastructure.config.settings import VK_GROUP_TOKEN, VK_USER_TOKEN, VK_GROUP_ID
from infrastructure.db.session import SessionLocal
from infrastructure.db.repositories.user_repository import UserRepository
from infrastructure.db.repositories.candidate_repository import CandidateRepository
from infrastructure.db.repositories.favorites_repository import FavoriteRepository
from infrastructure.db.repositories.blacklist_repository import BlacklistRepository
from infrastructure.db.repositories.candidate_photo_repository import CandidatePhotoRepository
from infrastructure.db.repositories.shown_candidate_repository import ShownCandidateRepository

from infrastructure.vk.vk_api_client import VKApiClient
from infrastructure.vk.search_service import VkSearchService
from infrastructure.vk.photos_service import VKPhotosService
from infrastructure.vk.user_service import VKUsersService
from infrastructure.vk.messages_service import MessagesService

from app.keyboards.buttons import (
    START_SEARCH,
    LIST_FAVORITES,
    HELP,
    MAIN_MENU,
    CANCEL,
    NEXT_CANDIDATE,
    ADD_TO_FAVORITES,
    ADD_TO_BLACKLIST,
    FINISH_SEARCH,
)

from app.state.dialog_state import DialogState, get_session

from app.handlers.start_handler import handle_start
from app.handlers.search_handler import handle_search_step
from app.handlers.candidate_handler import (
    handle_next_candidate,
    handle_add_to_favorites,
    handle_add_to_blacklist,
    handle_finish_search,
)
from app.handlers.favorites_list_handler import handle_list_favorites
from app.handlers.help_handler import handle_help, handle_main_menu, handle_cancel

def run_bot() -> None:
    db = SessionLocal()

    user_repo = UserRepository(db)
    candidate_repo = CandidateRepository(db)
    favorites_repo = FavoriteRepository(db)
    blacklist_repo = BlacklistRepository(db)
    photo_repo = CandidatePhotoRepository(db)
    shown_repo = ShownCandidateRepository(db)

    group_client = VKApiClient(VK_GROUP_TOKEN)
    user_client = VKApiClient(VK_USER_TOKEN)

    group_vk = group_client.get_api()
    user_vk = user_client.get_api()

    messages_service = MessagesService(group_vk)
    search_service = VkSearchService(user_vk)
    photos_service = VKPhotosService(user_vk)
    users_service = VKUsersService(user_vk)

    longpoll = VkBotLongPoll(group_client.vk_session, VK_GROUP_ID)

    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        if not event.object.message.get("text"):
            continue

        vk_user_id = event.object.message["from_id"]
        text = event.object.message["text"].strip()
        request = text.lower()

        session = get_session(vk_user_id)

        if request in ("начать", "/start", START_SEARCH.lower()):
            handle_start(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
            )
            continue

        if request == HELP.lower():
            handle_help(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
            )
            continue

        if request == MAIN_MENU.lower():
            handle_main_menu(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
            )
            continue

        if request == CANCEL.lower():
            handle_cancel(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
            )
            continue

        if request == LIST_FAVORITES.lower():
            handle_list_favorites(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
                user_repository=user_repo,
                favorites_repository=favorites_repo,
            )
            continue

        if request == NEXT_CANDIDATE.lower():
            handle_next_candidate(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
                user_repository=user_repo,
                candidate_repository=candidate_repo,
                shown_candidate_repository=shown_repo,
                candidate_photo_repository=photo_repo,
                vk_photos_service=photos_service,
            )
            continue

        if request == ADD_TO_FAVORITES.lower():
            handle_add_to_favorites(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
                user_repository=user_repo,
                candidate_repository=candidate_repo,
                favorites_repository=favorites_repo,
                blacklist_repository=blacklist_repo,
            )
            continue

        if request == ADD_TO_BLACKLIST.lower():
            handle_add_to_blacklist(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
                user_repository=user_repo,
                candidate_repository=candidate_repo,
                favorites_repository=favorites_repo,
                blacklist_repository=blacklist_repo,
                shown_candidate_repository=shown_repo,
                candidate_photo_repository=photo_repo,
                vk_photos_service=photos_service,
            )
            continue

        if request == FINISH_SEARCH.lower():
            handle_finish_search(
                vk_user_id=vk_user_id,
                messages_service=messages_service,
            )
            continue

        if session.state in (
            DialogState.WAITING_SEX,
            DialogState.WAITING_AGE_FROM,
            DialogState.WAITING_AGE_TO,
            DialogState.WAITING_CITY,
        ):
            handle_search_step(
                vk_user_id=vk_user_id,
                text=text,
                messages_service=messages_service,
                user_repository=user_repo,
                candidate_repository=candidate_repo,
                blacklist_repository=blacklist_repo,
                shown_candidate_repository=shown_repo,
                candidate_photo_repository=photo_repo,
                vk_search_service=search_service,
                vk_users_service=users_service,
                vk_photos_service=photos_service,
            )
            continue

        messages_service.send_text(
            user_id=vk_user_id,
            message=f"Не понял, что Вы написали. Нажмите {START_SEARCH} или {HELP}",
        )


if __name__ == "__main__":
    run_bot()