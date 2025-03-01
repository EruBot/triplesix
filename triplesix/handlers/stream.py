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


from pyrogram import Client, emoji, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from triplesix.functions import command, yt_searcher, rem
from triplesix.clients import player


def inline_keyboard(user_id: int):
    i = 0
    k = 0
    for j in range(5):
        i += 1
        yield InlineKeyboardButton(f"{i}", callback_data=f"stream {k}|{user_id}")
        k += 1


@Client.on_message(command("stream"))
async def start_stream(_, message: Message):
    query = " ".join(message.command[1:])
    reply = message.reply_to_message
    if query:
        await player.start_stream("yt", message, query)
    elif reply:
        if reply.video or reply.document:
            await player.start_stream("local", message)
        else:
            await message.reply("Reply to video or document.")
    else:
        await message.reply("Pass the query after /stream command!")


@Client.on_message(command("streamv2"))
async def stream_v2(_, message: Message):
    query = " ".join(message.command[1:])
    user_id = message.from_user.id
    temps = []
    x = list(yt_searcher(query))
    # enumerate for yt
    for i, j in enumerate(x, start=1):
        temps.append(j)
        if i % 5 == 0:
            rem.append(temps)
            temps = []
        if i == len(x):
            rem.append(temps)
    x.clear()
    rez = "\n"
    k = 0
    for i in rem[0]:
        k += 1
        rez += f"|- {k}. [{i['title'][:35]}]({i['url']})\n"
        rez += f"|- Duration - {i['duration']}\n\n"

    temp = []
    keyboard = []
    # enumerate for keyboard
    for count, j in enumerate(list(inline_keyboard(user_id)), start=1):
        temp.append(j)
        if count % 3 == 0:
            keyboard.append(temp)
            temp = []
        if count == len(list(inline_keyboard(user_id))):
            keyboard.append(temp)
    await message.reply(f"Results\n{rez}\n|- Owner @shohih_abdul2", reply_markup=InlineKeyboardMarkup(
        [
            keyboard[0],
            keyboard[1],
            [
              InlineKeyboardButton(f"Next {emoji.RIGHT_ARROW}", f"next|{user_id}")
            ],
            [
                InlineKeyboardButton(f"Close {emoji.WASTEBASKET}", f"close|{user_id}")
            ]
        ]
    ), disable_web_page_preview=True)


@Client.on_message(command("playlist"))
async def get_playlist(_, message: Message):
    playlist = player.playlist
    if not playlist:
        await message.reply("No playlist")
    chat_id = message.chat.id
    if not player.call.get_call(chat_id):
        await message.reply("Not playing")
    current = playlist[chat_id][0]
    ples = "\n"
    j = 0
    for i in playlist[chat_id][1:]:
        j += 1
        query = i["query"]
        ples += f"{j}. {query}\n"
    await message.reply(
        f"Current streaming\n{current['query']}\n\n{'On Playlist' if playlist[chat_id][1:] else ''}\n\n{ples}"
    )
