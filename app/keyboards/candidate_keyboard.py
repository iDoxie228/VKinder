from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from app.keyboards.buttons import (
    ADD_TO_FAVORITES, 
    NEXT_CANDIDATE, 
    ADD_TO_BLACKLIST, 
    LIST_FAVORITES, 
    FINISH_SEARCH
)

def get_candidate_keyboard() -> str:
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(
        ADD_TO_FAVORITES,
        color=VkKeyboardColor.POSITIVE,
    )

    keyboard.add_button(
        NEXT_CANDIDATE,
        color=VkKeyboardColor.PRIMARY,
    )

    keyboard.add_line()

    keyboard.add_button(
        ADD_TO_BLACKLIST,
        color=VkKeyboardColor.NEGATIVE,
    )

    keyboard.add_line()

    keyboard.add_button(
        LIST_FAVORITES,
        color=VkKeyboardColor.SECONDARY,
    )

    keyboard.add_button(
        FINISH_SEARCH,
        color=VkKeyboardColor.SECONDARY,
    )

    return keyboard.get_keyboard()