from app.keyboards.main_keyboard import get_main_keyboard
from app.state.dialog_state import reset_session
from app.keyboards.buttons import (
    START_SEARCH, 
    ADD_TO_FAVORITES, 
    NEXT_CANDIDATE, 
    ADD_TO_BLACKLIST, 
    LIST_FAVORITES
)

def handle_help(
    vk_user_id: int,
    messages_service,
) -> None:
    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message=(
            f"""VKinder помогает найти людей для знакомств во ВКонтакте.\n\n
Как этим пользоваться:\n
Нажмите "{START_SEARCH}", чтобы найти человка;\n
"{NEXT_CANDIDATE}", чтобы показать следующего;\n
"{ADD_TO_FAVORITES}", чтобы сохранить понравившегося человека;\n
"{ADD_TO_BLACKLIST}", чтобы больше не показывать этого человека;\n
"{LIST_FAVORITES}", чтобы посмотреть свои избранные"""
        ),
        keyboard=get_main_keyboard(),
    )


def handle_main_menu(
    vk_user_id: int,
    messages_service,
) -> None:
    reset_session(vk_user_id)

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message="Вы вернулись в главное меню",
        keyboard=get_main_keyboard(),
    )


def handle_cancel(
    vk_user_id: int,
    messages_service,
) -> None:
    reset_session(vk_user_id)

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message="Поиск отменен",
        keyboard=get_main_keyboard(),
    )