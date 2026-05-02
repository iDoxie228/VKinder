from app.keyboards.main_keyboard import get_main_keyboard
from app.use_cases.list_favorites import get_list_favorites
from infrastructure.db.repositories.favorites_repository import FavoriteRepository
from infrastructure.db.repositories.user_repository import UserRepository

def handle_list_favorites(
    vk_user_id: int,
    messages_service,
    user_repository: UserRepository,
    favorites_repository: FavoriteRepository,
) -> None:
    app_user = user_repository.get_by_vk_user_id(vk_user_id)

    if app_user is None:
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message="Сначала начните поиск",
            keyboard=get_main_keyboard(),
        )
        return

    result = get_list_favorites(
        app_user_id=app_user.id,
        user_repository=user_repository,
        favorites_repository=favorites_repository,
    )

    if not result.success:
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message=result.message,
            keyboard=get_main_keyboard(),
        )
        return

    if not result.favorites:
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message=result.message,
            keyboard=get_main_keyboard(),
        )
        return

    text = "Ваш список избранных:\n\n"

    for index, candidate in enumerate(result.favorites, start=1):
        full_name = f"{candidate.first_name or ''} {candidate.last_name or ''}".strip()
        profile_url = candidate.profile_url or f"https://vk.com/id{candidate.vk_candidate_id}"

        text += f"{index}. {full_name}\n{profile_url}\n\n"

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message=text,
        keyboard=get_main_keyboard(),
    )