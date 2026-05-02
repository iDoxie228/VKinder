from dataclasses import dataclass, field

class DialogState:
    IDLE = "idle"
    WAITING_SEX = "waiting_sex"
    WAITING_AGE_FROM = "waiting_age_from"
    WAITING_AGE_TO = "waiting_age_to"
    WAITING_CITY = "waiting_city"
    VIEWING_CANDIDATES = "viewing_candidates"


@dataclass
class UserDialogSession:
    state: str = DialogState.IDLE
    app_user_id: int | None = None
    sex: int | None = None
    age_from: int | None = None
    age_to: int | None = None
    city_id: int | None = None
    candidate_ids: list[int] = field(default_factory=list)
    index: int = 0


_sessions: dict[int, UserDialogSession] = {}


def get_session(vk_user_id: int) -> UserDialogSession:
    if vk_user_id not in _sessions:
        _sessions[vk_user_id] = UserDialogSession()
    return _sessions[vk_user_id]


def reset_session(vk_user_id: int) -> None:
    _sessions[vk_user_id] = UserDialogSession()


def set_state(vk_user_id: int, state: str) -> None:
    session = get_session(vk_user_id)
    session.state = state