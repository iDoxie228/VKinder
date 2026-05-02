from app.keyboards.search_keyboard import get_sex_keyboard
from app.state.dialog_state import DialogState, get_session, reset_session

def handle_start(
    vk_user_id: int,
    messages_service,
) -> None:
    reset_session(vk_user_id)

    session = get_session(vk_user_id)
    session.state = DialogState.WAITING_SEX

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message="Укажите, кого Вы хотите найти:",
        keyboard=get_sex_keyboard(),
    )