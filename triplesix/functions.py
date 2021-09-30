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


from typing import Callable, Any

import asyncio
import requests
from pafy import new
from pyrogram import filters, Client
from pyrogram.types import Message
from youtube_search import YoutubeSearch

from triplesix import bot_username
from dB import get_sudos


def command(cmd: str):
    """
    Function for pyrogram command
    :param str cmd: the command
    """
    return filters.command([cmd, f"{cmd}@{bot_username}"])


async def get_youtube_stream(query: str):
    proc = await asyncio.create_subprocess_exec(
        "youtube-dl",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"https://youtube.com{YoutubeSearch(query, 1).to_dict()[0]['url_suffix']}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode().split("\n")[0]


def admins_only(func: Callable) -> Callable:
    async def wrapper(client: Client, message: Message):
        user_id = message.from_user.id
        person = await message.chat.get_member(user_id)
        if person.status in ("creator", "administrator"):
            return await func(client, message)
    return wrapper


def authorized_users_only(func: Callable) -> Callable:
    """Only authorized users (admin or sudo or owner) can use the command"""

    async def wrapper(client: Client, message: Message):
        user_id = message.from_user.id
        person = await message.chat.get_member(user_id)
        try:
            if user_id in get_sudos(message.chat.id):
                return await func(client, message)
            if person.status in ("creator", "administrator"):
                return await func(client, message)
        except AttributeError:
            if person.is_anonymous:
                return await func(client, message)
    return wrapper


def video_downloader(query: str):
    url = f"https://youtube.com{YoutubeSearch(query, 1).to_dict()[0]['url_suffix']}"
    pufy = new(url)
    title = pufy.title[:30]
    thumbs = pufy.bigthumbhd
    thumb = requests.get(thumbs, allow_redirects=True)
    open(f"thumb{title}.jpg", "wb").write(thumb.content)
    dur = pufy.duration
    vid = pufy.getbestvideo()
    filename = vid.download(quiet=True)
    return dur, filename, title


a: list[dict[str, Any]] = []

rem = []


def yt_searcher(query: str):
    i = 0
    rez = ""
    j = -1
    for _ in range(10):
        i += 1
        res = YoutubeSearch(query, 10).to_dict()
        rez += f"|- {i}. [{res[j]['title'][:35]}...](https://youtube.com{res[j]['url_suffix']})\n"
        rez += f" - Duration - {res[j]['duration']}\n"
        x = {
            "title": res[j]["title"],
            "url": f"https://youtube.com{res[j]['url_suffix']}",
            "duration": res[j]["duration"]
        }
        a.append(x.copy())
        j += 1
    return a
