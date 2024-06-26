from typing import List, Tuple

from config import App
from db import models

from aiogram import types


async def send_message(text, reply_markup=None, event=None, user: models.User = None):
    if not event and user:
        await App.bot().send_message(
            text=text,
            chat_id=user.tg_id,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    if not event and not user:
        raise ValueError("Either event or user should be provided to send a message")

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, parse_mode='HTML')
        if reply_markup:
            await event.message.edit_reply_markup(reply_markup=reply_markup)
        return

    await event.answer(text, reply_markup=reply_markup, parse_mode='HTML')


class MessageTemplates:
    def get_new_word_message(word_and_translation: Tuple[models.Word, models.WordTranslation]):
        word_to_learn, word_translation = word_and_translation

        message = (
            f"<b>Слово:</b> {word_to_learn.word.capitalize()}\n"
            f"<b>Перевод:</b> {word_translation.translation.capitalize()}\n"
        )

        word_examples: List[models.WordExamples] = models.DBSession.query(
            models.WordExamples
        ).filter(
            models.WordExamples.word_id == word_to_learn.id
        ).limit(2).all()

        if not word_examples:
            return message

        examples = [f"- {word_example.example_sentece}" for word_example in word_examples]

        message += "\n<b>Примеры:</b>\n"
        message += '\n'.join(examples)

        return message

    def get_new_daily_word_message(word_and_translation: Tuple[models.Word, models.WordTranslation]):
        message = "<b>Ваше слово дня</b>\n\n"

        message += MessageTemplates.get_new_word_message(word_and_translation)
        return message
