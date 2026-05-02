from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from app.keyboards.buttons import SEX_FEMALE, SEX_MALE, SEX_ANY, CANCEL, MAIN_MENU

def get_sex_keyboard() -> str:
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(
        SEX_FEMALE,
        color=VkKeyboardColor.PRIMARY,
    )

    keyboard.add_button(
        SEX_MALE,
        color=VkKeyboardColor.PRIMARY,
    )

    keyboard.add_line()

    keyboard.add_button(
        SEX_ANY,
        color=VkKeyboardColor.SECONDARY,
    )

    keyboard.add_line()

    keyboard.add_button(
        CANCEL,
        color=VkKeyboardColor.NEGATIVE,
    )

    return keyboard.get_keyboard()


def get_cancel_keyboard() -> str:
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button(
        CANCEL,
        color=VkKeyboardColor.NEGATIVE,
    )

    keyboard.add_button(
        MAIN_MENU,
        color=VkKeyboardColor.SECONDARY,
    )

    return keyboard.get_keyboard()