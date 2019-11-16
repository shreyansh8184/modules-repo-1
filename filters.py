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
from userbot import BOTLOG_CHATID
logger = logging.getLogger(__name__)

def register(cb):
    cb(Filters())

class Filters(loader.Module):
    """Provides a message saying that you are unavailable (out of office)"""
    def __init__(self):
        self.name = _("Filters")
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me()
        
    async def filtercmd(self, message):
        """ADDS A FILTER INTO THE LIST"""
        filtern = utils.get_args_raw(message)
        getr = await message.get_reply_message()
        chatid = message.chat_id
        filters = self._db.get(__name__, "filters")
        if not filters or str(list(filters)).find(str(chatid)) == -1:
        	filters = {chatid: {}}
        if not getr:
        	await message.reply("<code>Reply to a message first!</code>")
        	return
        while filtern.strip() == (""):
        	await message.edit("<code>Please type a name for the filter.</code>")
        	return
        filterv = getr.text
        if getr.media:
        	if BOTLOG_CHATID:
        		fwd = await self._client.forward_messages(BOTLOG_CHATID, getr, message.chat_id, silent=True)
        		filters[chatid][filtern] = fwd.id
        		self._db.set(__name__, "filters", filters)
        	else:
        		filters[chatid][filtern] = getr.id
        		self._db.set(__name__, "filters", filters)
        	await message.edit("<code>Filter '" + filtern + "' successfully saved into the list.</code>")	
        	return
        elif not filterv:
        	await message.edit("<code>Please reply to a message to save as filter.</code>")
        	return
        filters[chatid][filtern] = filterv
        self._db.set(__name__, "filters", filters)
        await message.edit("<code>Filter '" + filtern + "' successfully added into filters.</code>")
        	
    async def stopcmd(self, message):
        """REMOVES A FILTER FROM THE LIST"""
        filtern = utils.get_args_raw(message)
        filters = self._db.get(__name__, "filters")
        chatid = message.chat_id
        while filtern.strip() == "" or not filtern:
        	await message.edit("<code>Please specify the name of the filter.</code>")
        	return
        try:
        	del filters[chatid][filtern]
        	await message.edit("<code>Filter '" + filtern + "' successfully removed from the list.</code>")
        	self._db.set(__name__, "filters", filters)
        except:
        	await message.edit("<code>Filter '" + filtern + "' not found in filters list</code>")
        
    async def stopallcmd(self, message):
        """CLEARS OUT THE FILTER LIST"""
        filters = self._db.get(__name__, "filters")
        chatid = message.chat_id
        try:
        	del filters[chatid]
        	self._db.set(__name__, "filters", filters)
        	await message.edit("<code>All filters successfully removed from the list.</code>")
        except:
        	await message.edit("<code>Filters couldn't be cleared out</code>")
        	    	
    async def filterscmd(self, message):
        """SHOWS SAVED FILTERs"""
        filters = ""
        filt = self._db.get(__name__, "filters")
        chatid = message.chat_id
        try:
        	for i in filt[chatid]:
        		filters += "  »  <b>" + str(i) + "</b>\n"
        		pass
        except: pass
        filterl = "<code>Filters that you saved in this chat: </code>\n\n" + filters
        if filters.strip() != "":
        	await message.edit(filterl)
        else:
        	await message.edit('<code>No filters found in this chat.</code>')
        	
    async def watcher(self, message):
    	args = message.text
    	filters = self._db.get(__name__, "filters")
    	if getattr(message.to_id, "user_id", None) != message.from_id and filters:
    		chatid = message.chat_id
    		for i in range(len(filters)):
    			if str(list(filters)[0]).find(str(chatid)) != -1 and args.find(str(list(filters[chatid])[i])) != -1:
    				val = filters[chatid][list(filters[chatid])[i]]
    				try:
    					if BOTLOG_CHATID:
    						await self._client.forward_messages(chatid, val, BOTLOG_CHATID, silent=True)
    					else:
    						await self._client.forward_messages(chatid, val, chatid, silent=True)
    				except:
    					await message.reply(val)
    				return