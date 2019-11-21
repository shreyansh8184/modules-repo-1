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

from telethon import functions, types
from userbot import (BOTLOG_CHATID)
logger = logging.getLogger("SnipsMod")


def register(cb):
    cb(Snips())


class Snips(loader.Module):
    """Saves some texts or medias to call on them literally anywhere and anytime"""

    def __init__(self):
        self.name = _("Snips")
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me()

    async def snipcmd(self, message):
        """Adds a snip into the list."""
        snipn = utils.get_args_raw(message)
        getr = await message.get_reply_message()
        if not getr:
            await message.reply("<code>Reply to a message first!</code>")
            return
        while snipn.strip() == (""):
            await message.edit("<code>Please type a name for the snip.</code>")
            return
        snipv = getr.text
        sniplist = self._db.get("SnipsMod", "sniplist", [])
        if sniplist:
            sniplist.update({snipn: snipv})
            pass
        else:
            sniplist = {}
        if getr.media:
            if BOTLOG_CHATID:
                try:
                    fwd = await self._client.send_message(BOTLOG_CHATID, getr.message, file=getr.media, link_preview=False)
                except:
                    fwd = await self._client.send_message(BOTLOG_CHATID, getr.message, file=None, link_preview=False)
                sniplist = {snipn: fwd.id}
                self._db.set("SnipsMod", "sniplist", sniplist)
            else:
                await message.edit("<code>Set your BOTLOG_CHATID first.</code>")
                return
            await message.edit("<code>Snip '" + snipn + "' successfully saved into the list. Type .getsnip " + snipn + " to call it.</code>"
                               "\n\n<code>Others can access it via $" + snipn + "</code>"
                               )
            return
        elif not snipv:
            await message.edit("<code>Please reply to a message to save as snip.</code>")
            return
        sniplist[snipn] = snipv
        self._db.set("SnipsMod", "sniplist", sniplist)
        await message.edit("<code>Snip '" + snipn + "' successfully saved into the list. Type .getsnip " + snipn + " to call it.</code>"
                           "\n\n<code>Others can access it via $" + snipn + "</code>"
                           )

    async def sniprmcmd(self, message):
        """Removes a snip from the list."""
        snipn = utils.get_args_raw(message)
        get = self._db.get("SnipsMod", "sniplist", [])
        while snipn.strip() == "" or not snipn:
            await message.edit("<code>Please specify the name of the snip.</code>")
            return
        if snipn in get:
            del get[snipn]
            self._db.get("SnipsMod", "sniplist", get)
            await message.edit("<code>Snip '" + snipn + "' successfully removed from the list.</code>")
        else:
            await message.edit("<code>Snip '" + snipn + "' not found in snips list</code>")

    async def snipsrmcmd(self, message):
        """Clears out the snip list."""
        get = self._db.get("SnipsMod", "sniplist", [])
        get.clear()
        self._db.set("SnipsMod", "sniplist", get)
        await message.edit("<code>All snips successfully removed from the list.</code>")

    async def snipscmd(self, message):
        """Shows saved snips."""
        snips = ""
        get = self._db.get("SnipsMod", "sniplist", [])
        i = 0
        try:
            for i in range(len(get)):
                snips += "-  <b>" + list(get.keys())[i] + "</b>\n"
                pass
        except BaseException:
            pass
        snipl = "<b>Snips that you saved: </b>\n\n" + snips
        if snips.strip() != "":
            await message.edit(snipl)
            return
        else:
            await message.edit('<code>No snip found in snips list.</code>')
            return

    async def getsnipcmd(self, message):
        """Calls for the saved snip."""
        snip = utils.get_args_raw(message)
        get = self._db.get("SnipsMod", "sniplist", [])
        val = get.get(snip)
        if isinstance(val, int):
            await message.delete()
            loggedsnip = await message.client.get_messages(entity=BOTLOG_CHATID, ids=int(val))
            await message.client.send_message(message.chat_id, loggedsnip.message, file=loggedsnip.media)
            return
        elif val:
            await message.edit(val)
            return
        else:
            await message.edit("<code>No snip found in that name.</code>")
            return

    async def otherscmd(self, message):
        """Turns on/off snips for others usage."""
        state = utils.get_args_raw(message)
        if state == "on":
        	self._db.set("snips", "others", "on")
        	await message.edit("<code>Snips are now open to use for anyone.</code>")
        	return
        elif state == "off":
        	self._db.set("snips", "others", "off")
        	await message.edit("<code>Snips are now turned off for others.</code>")
        	return

    async def watcher(self, message):
        get = self._db.get("SnipsMod", "sniplist", [])
        state = self._db.get("snips", "others")
        args = message.text
        argsraw = args.replace("$", "")
        if getattr(message.to_id, "user_id", None) != message.from_id and args.find("$") != -1 and state == "on":
            val = get.get(argsraw)
            if not get:
                return
            if isinstance(val, int):
                loggedsnip = await message.client.get_messages(entity=BOTLOG_CHATID, ids=int(val))
                try:
                    await message.client.send_message(message.chat_id, loggedsnip.message, reply_to=message.id, file=loggedsnip.media)
                except:
                    await message.client.send_message(message.chat_id, loggedsnip.message, reply_to=message.id, file=None)
                return
            else:
                await message.reply(val)
                return
