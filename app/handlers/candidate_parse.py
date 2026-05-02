from app.keyboards.candidate_keyboard import get_candidate_keyboard
from app.keyboards.main_keyboard import get_main_keyboard


def send_candidate_result(
    vk_user_id: int,
    result,
    messages_service,
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

    messages_service.send_text_with_keyboard(
        user_id=vk_user_id,
        message=text,
        keyboard=get_candidate_keyboard(),
    )

    attachments = [
        photo["attachment"]
        for photo in result.photos
        if photo.get("attachment")
    ]

    messages_service.send_attachments(
        user_id=vk_user_id,
        attachments=attachments,
    )