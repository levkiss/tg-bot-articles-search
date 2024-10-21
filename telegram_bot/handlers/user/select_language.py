from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

from telegram_bot import states
from telegram_bot.keyboards.inline.user import BasicInlineButtons

async def language_selection(msg: types.Message, state: FSMContext) -> None:
    if msg.from_user is None:
        return
    
    # Send a message to the user asking to select a language
    await msg.answer("🌍 Выбери язык, на котором я буду делать подборки и обзоры статей:", 
                     reply_markup=BasicInlineButtons.language_selection())
    
    # Set the state to wait for language selection
    await state.set_state(states.user.UserLanguageSelection.selecting)

async def handle_language_selection(call: types.CallbackQuery, state: FSMContext) -> None:
    language = call.data.split("_")[-1]
    print(language)

    if language == "russian":
        response_text = "Язык установлен на Русский. Давай начнем!"
    elif language == "english":
        response_text = "Language set to English. Let's get started!"
    else:
        response_text = "Invalid language selection."

    await call.message.edit_text(text=response_text, reply_markup=None)
    await state.update_data(language=language) 
    await state.set_state(states.user.UserMainMenu.menu)  # Change to the main menu state


async def get_selected_language(msg: types.Message, state: FSMContext) -> None:
    """
    Handler to get the selected language of the user.
    """
    user_data = await state.get_data()
    selected_language = user_data.get("language", "Not set")

    await msg.answer(f"Your selected language is: {selected_language}")
