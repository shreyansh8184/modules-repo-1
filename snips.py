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
    """Saves some texts to call on them literally anywhere and anytime"""

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
        snipn = (utils.get_args_raw(message)).strip()
        reply = await message.get_reply_message()
        sniplist = self._db.get("SnipsMod", "sniplist", [])
        if snipn != "":
            snipn = snipn.split(" ")
        else:
            await message.edit("<code>Please enter the name of your snip first.</code>")
            return
        if not sniplist:
            sniplist = {}
        if not reply:
            if str(snipn[0]).isspace():
                await message.edit("<code>Please enter the name of your snip first.</code>")
                return
            else:
                name = snipn[0]
            if len(snipn) is 1:
                await message.edit("<code>Please reply to a message or enter a text to save as snip.!</code>")
                return
            else:
                value = snipn[1]
        else:
            name = snipn[0]
            value = reply.text
        if reply and reply.media:
            if BOTLOG_CHATID:
                try:
                    fwd = await self._client.send_message(BOTLOG_CHATID, reply.message, file=reply.media, link_preview=False)
                except BaseException:
                    fwd = await self._client.send_message(BOTLOG_CHATID, reply.message, file=None, link_preview=False)
                sniplist[snipn] = fwd.id
                self._db.set("SnipsMod", "sniplist", sniplist)
            else:
                await message.edit("<code>Set your BOTLOG_CHATID first.</code>")
                return
            await message.edit("<code>Snip '" + snipn + "' successfully saved into the list. Type .getsnip " + snipn + " to call it.</code>"
                               "\n\n<code>Others can access it via $" + snipn + "</code>"
                               )
            return
        else:
            sniplist[name] = value
            self._db.set("SnipsMod", "sniplist", sniplist)
            await message.edit("<b>Snip '" + name + "' successfully saved into the list. Type .getsnip " + name + " to call it.</b>"
                               "\n\n<b>Others can access it via $" + name + "</b>"
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
            exec = True
            for load in self.allloaders:
                if load.client is self._client:
                    break
            if val.startswith(".") is True:
                arg = val[1::]
            if val.startswith("..") is True:
                arg = val[2::]
            if val.startswith(".") is False:
                exec = False
                arg = val
            ifcmd = await message.edit(arg)
            if exec is True:
                argspr = arg.split(" ")
                try:
                    await load.dispatch(argspr[0], ifcmd)
                except BaseException:
                    pass
                return
        else:
            await message.edit("<code>No snip found in that name.</code>")
            return

    async def otherscmd(self, message):
        """Turns on/off snips for others usage."""
        state = utils.get_args_raw(message)
        if state == "on":
            self._db.set("SnipsMod", "others", "on")
            await message.edit("<code>Snips are now open to use for anyone.</code>")
            return
        elif state == "off":
            self._db.set("SnipsMod", "others", "off")
            await message.edit("<code>Snips are now turned off for others.</code>")
            return

    async def watcher(self, message):
        get = self._db.get("SnipsMod", "sniplist", [])
        state = self._db.get("SnipsMod", "others")
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
                except BaseException:
                    await message.client.send_message(message.chat_id, loggedsnip.message, reply_to=message.id, file=None)
                return
            else:
                exec = True
                for load in self.allloaders:
                    if load.client is self._client:
                        break
                if val.startswith(".") is True:
                    arg = val[1::]
                if val.startswith("..") is True:
                    arg = val[2::]
                if val.startswith(".") is False:
                    exec = False
                    arg = val
                ifcmd = await message.reply(arg)
                if exec is True:
                    argspr = arg.split(" ")
                    try:
                        await load.dispatch(argspr[0], ifcmd)
                    except BaseException:
                        pass
                    return
                return
