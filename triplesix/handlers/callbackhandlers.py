#     Video Stream Bot, by Abdul
#     Copyright (C) 2021  Shohih Abdul
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from youtube_search import YoutubeSearch

from triplesix.clients import player
from triplesix.handlers.stream import InlineKeyboardButton, InlineKeyboardMarkup
from dB import lang_flags, set_lang, get_message


def inline_keyboard(query: str, user_id: int):
    i = 5
    j = 4
    for _ in range(3):
        i += 1
        j += 1
        yield InlineKeyboardButton(
            f"{i}", callback_data=f"stream {j}|{query}|{user_id}"
        )


def inline_keyboard2(query: str, user_id: int):
    i = 8
    j = 7
    for _ in range(2):
        i += 1
        j += 1
        yield InlineKeyboardButton(
            f"{i}", callback_data=f"stream {j}|{query}|{user_id}"
        )


@Client.on_callback_query(filters.regex(pattern=r"close"))
async def close_inline(_, cb: CallbackQuery):
    callback = cb.data.split("|")
    user_id = int(callback[1])
    message = cb.message
    person = await message.chat.get_member(cb.from_user.id)
    if cb.from_user.id != user_id:
        await cb.answer("this is not for you.", show_alert=True)
        return
    if person.status in ("creator", "administrator"):
        return await message.delete()
    await message.delete()


@Client.on_callback_query(filters.regex(pattern=r"stream"))
async def play_callback(_, cb: CallbackQuery):
    callback = cb.data.split("|")
    x = int(callback[0].split(" ")[1])
    query = callback[1]
    user_id = int(callback[2])
    if cb.from_user.id != user_id:
        await cb.answer("this is not for u.", show_alert=True)
        return
    res = YoutubeSearch(query, 10).to_dict()
    title = res[x]["title"]
    await cb.message.delete()
    await player.start_stream_via_callback(title, cb)


@Client.on_callback_query(filters.regex(pattern=r"next"))
async def next_callback(_, cb: CallbackQuery):
    message = cb.message
    callback = cb.data.split("|")
    query = callback[1]
    user_id = int(callback[2])
    if cb.from_user.id != user_id:
        await cb.answer("this is not for u.", show_alert=True)
        return
    rez = "\n"
    i = 5
    j = 4
    for _ in range(5):
        i += 1
        j += 1
        res = YoutubeSearch(query, 10).to_dict()
        rez += f"|- {i}. [{res[j]['title'][:35]}...](https://youtube.com{res[j]['url_suffix']})\n"
        rez += f" - Duration - {res[j]['duration']}\n"
    await message.edit(
        f"Results\n{rez}\n|- Owner @shohih_abdul2",
        reply_markup=InlineKeyboardMarkup(
            [
                list(inline_keyboard(query, user_id)),
                list(inline_keyboard2(query, user_id)),
                [InlineKeyboardButton("Close", f"close|{user_id}")],
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex(pattern=r"set_lang_(.*)"))
async def change_language(_, cb: CallbackQuery):
    langs = cb.matches[0].group(1)
    chat = cb.message.chat
    lang = lang_flags[langs]
    try:
        set_lang(chat.id, lang)
        await cb.message.edit(get_message(chat.id, "lang_changed"))
    except Exception as e:
        await cb.message.edit(f"an error occured\n\n{e}")
