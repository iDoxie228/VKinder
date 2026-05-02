from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from app.keyboards.buttons import START_SEARCH, LIST_FAVORITES, HELP

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_main_keyboard() -> str:
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(
       START_SEARCH,
        color=VkKeyboardColor.POSITIVE,
    )

    keyboard.add_line()

    keyboard.add_button(
        LIST_FAVORITES,
        color=VkKeyboardColor.PRIMARY,
    )

    keyboard.add_button(
        HELP,
        color=VkKeyboardColor.SECONDARY,
    )

    return keyboard.get_keyboard()