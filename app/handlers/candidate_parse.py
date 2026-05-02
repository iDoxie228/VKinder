from app.keyboards.candidate_keyboard import get_candidate_keyboard
from app.keyboards.main_keyboard import get_main_keyboard
from infrastructure.vk.messages_service import MessagesService

def send_candidate_result(
    vk_user_id: int,
    result,
    messages_service: MessagesService,
) -> None:
    if not result.success or result.candidate is None:
        messages_service.send_text_with_keyboard(
            user_id=vk_user_id,
            message=result.message,
            keyboard=get_main_keyboard(),
        )
        return

    candidate = result.candidate

    full_name = f"{candidate.first_name or ''} {candidate.last_name or ''}".strip()
    profile_url = candidate.profile_url or f"https://vk.com/id{candidate.vk_candidate_id}"

    text = (
        f"👤 {full_name}\n"
        f"🔗 {profile_url}"
    )

    attachments = [
        photo["attachment"]
        for photo in result.photos
        if photo.get("attachment")
    ]

    messages_service.send_text_attachments_keyboard(
        user_id=vk_user_id,
        message=text,
        attachments=attachments,
        keyboard=get_candidate_keyboard()
    )