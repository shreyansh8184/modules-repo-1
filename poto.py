# -*- coding: future_fstrings -*-

#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from .. import loader, utils

logger = logging.getLogger(__name__)


def register(cb):
    cb(GetPPMod())


class GetPPMod(loader.Module):
    """Description for module"""
    def __init__(self):
        self.name = _("Profile Photos")

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def potocmd(self, message):
        """Gets the profile photos of replied users, channels or chats"""
        id = utils.get_args_raw(message)
        user = await message.get_reply_message()
        chat = message.input_chat
        if user:
            photos = await self.client.get_profile_photos(user.sender)
        else:
            photos = await self.client.get_profile_photos(chat)
        if id.strip() == "":
            try:
                await self.client.send_file(message.chat_id, photos)
            except:
                photo = await self.client.download_profile_photo(chat)
                await self.client.send_file(message.chat_id, photo)
        else:
            try:
                id = int(id)
                if id <= 0:
                    await message.edit("<code>ID number you entered is invalid</code>")
                    return
            except:
                 await message.edit("<code>ID number you entered is invalid</code>")
                 return
            if int(id) <= (len(photos)):
                send_photos = await self.client.download_media(photos[id - 1])
                await self.client.send_file(message.chat_id, send_photos)
            else:
                await message.edit("<code>No photo found with that id</code>")
                return
