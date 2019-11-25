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

from .. import loader, utils

import logging
logger = logging.getLogger("FilterModule")


def register(cb):
    cb(Filters())


class Filters(loader.Module):
    """When you filter a text, it auto responds to it if a user triggers the word)"""

    def __init__(self):
        self.name = _("Filters")
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me()

    async def filtercmd(self, message):
        """Adds a filter into the list."""
        args = (utils.get_args_raw(message)).split(",")
        chatid = message.chat_id
        filters = self._db.get("FilterModule", "filters", {})
        if args[0] == "":
            await message.edit(_("<b>Enter a name for the filter first!</b>"))
            return
        name = args[0]
        if chatid not in filters:
            filters.setdefault(chatid, {})
        if not message.is_reply:
            if len(args) == 1:
                await message.edit(_("<b>Please reply to a message or enter a text to save as filter.!</b>"))
                return
            else:
                value = args[1]
                msg_to_log = await self._db.store_asset(value)
        else:
            value = await message.get_reply_message()
            msg_to_log = await self._db.store_asset(value)
        filters[chatid][name] = msg_to_log
        self._db.set("FilterModule", "filters", filters)
        await message.edit(_("<b>Text ''{}'' has been successfully filtered in this chat.</b>".format(name)))

    async def stopcmd(self, message):
        """Removes a filter from the list."""
        filtern = utils.get_args_raw(message)
        filters = self._db.get("FilterModule", "filters")
        chatid = message.chat_id
        if not filtern:
            await message.edit(_("<b>Please specify the name of the filter.</b>"))
            return
        try:
            del filters[chatid][filtern]
            await message.edit(_("<b>Filter ''{}'' successfully removed from the chat.</b>".format(filtern)))
            self._db.set("FilterModule", "filters", filters)
        except Exception:
            await message.edit(_("<b>Filter ''{}'' not found in this chat</b>".format(filtern)))

    async def stopallcmd(self, message):
        """Clears out the filter list."""
        filters = self._db.get("FilterModule", "filters")
        chatid = message.chat_id
        try:
            del filters[chatid]
            self._db.set("FilterModule", "filters", filters)
            await message.edit(_("<b>All filters successfully removed from the chat.</b>"))
        except Exception:
            await message.edit(_("<b>There are no filters to clear out in this chat.</b>"))

    async def filterscmd(self, message):
        """Shows saved filters."""
        filters = ""
        filt = self._db.get("FilterModule", "filters")
        chatid = message.chat_id
        try:
            for i in filt[chatid]:
                filters += "<b> -  " + str(i) + "</b>\n"
                pass
        except Exception:
            pass
        filterl = "<b>Texts that you filtered in this chat: </b>\n\n{}".format(filters)
        if filters:
            await message.edit(filterl)
        else:
            await message.edit(_("<b>No filters found in this chat.</b>"))

    async def watcher(self, message):
        # This is to execute cmds
        exec = True
        for load in self.allloaders:
            if load.client is self._client:
                break
        args = str(message.text.lower())
        filters = self._db.get("FilterModule", "filters")
        chatid = message.chat_id
        current_prefix = self._db.get("friendly-telegram.main", "command_prefix", {})
        if not current_prefix:
            current_prefix = "."
        if filters and chatid in filters:
            for key in filters[chatid]:
                if key.lower() in args.lower():
                    id = filters[chatid][key]
                    value = await self._db.fetch_asset(int(id))
                    if not value.media and not value.web_preview:
                        if value.text.startswith(current_prefix):
                            cmd = value.message[1::]
                        if value.text.startswith(current_prefix * 2):
                            cmd = value.message[2::]
                        if not value.text.startswith(current_prefix):
                            exec = False
                            cmd = value.message
                        if not exec:
                            await message.reply(value)
                        else:
                            cmdspl = cmd.lower().split(" ")
                            respond = await message.reply(value)
                            try:
                                await load.dispatch(cmdspl[0], respond)
                            except Exception:
                                pass
                    else:
                        await message.reply(value)
                        return
