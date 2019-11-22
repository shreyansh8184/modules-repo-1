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
        #BOTLOG_CHATID CHECK
        try:
        	await self._client.get_entity(BOTLOG_CHATID)
        	botlog = True
        except:botlog = False
        filtern = utils.get_args_raw(message)
        getr = await message.get_reply_message()
        chatid = str(message.chat_id)
        filters = self._db.get("FilterModule", "filters")
        if filtern.strip() == (""):
        	await message.edit("<code>Please type a name for the filter.</code>")
        	return
        else:
            filtern = filtern.split(" ")
        if not filters:
        	filters = {}
        	filters.setdefault(chatid, {})
        	pass
        if str(list(filters)).find(chatid) == -1:
        	filters.setdefault(chatid, {})
        	pass
        if not getr:
            if str(filtern[0]).isspace():
                await message.edit("<code>Please enter the name of your filter first.</code>")
                return
            else:
                name = filtern[0]
            if len(filtern) == 1:
                await message.edit("<code>Please reply to a message or enter a text to save as filter.!</code>")
                return
            else:
                value = filtern[1]
        else:
            name = filtern[0]
            value = getr.text.lower()
        if getr and getr.media:
        	if botlog:
        		logfilter = await message.client.get_messages(entity=message.chat_id, ids=getr.id)
        		try:fwd = await self._client.send_message(BOTLOG_CHATID, logfilter.text, file=logfilter.media, link_preview=False)
        		except:fwd = await self._client.send_message(BOTLOG_CHATID, logfilter.text, file=None, link_preview=False)
        		filters[chatid][filtern[0]] = str(fwd.id)
        	else:
        		filters[chatid][filtern[0]] = str(getr.id)
        	self._db.set("FilterModule", "filters", filters)
        	await message.edit("<code>Filter '" + filtern[0] + "' successfully saved into the list.</code>")	
        	return
        else:
            filters[chatid][name] = value
            self._db.set("FilterModule", "filters", filters)
            await message.edit("<code>Filter '" + filtern[0] + "' successfully added into filters.</code>")
        	
    async def stopcmd(self, message):
        """Removes a filter from the list."""
        filtern = str(utils.get_args_raw(message))
        filters = self._db.get("FilterModule", "filters")
        chatid = str(message.chat_id)
        while filtern.strip() == "" or not filtern:
        	await message.edit("<code>Please specify the name of the filter.</code>")
        	return
        try:
        	del filters[chatid][filtern]
        	await message.edit("<code>Filter '" + filtern + "' successfully removed from the list.</code>")
        	self._db.set("FilterModule", "filters", filters)
        except:
        	await message.edit("<code>Filter '" + filtern + "' not found in filters list</code>")
        
    async def stopallcmd(self, message):
        """Clears out the filter list."""
        filters = self._db.get("FilterModule", "filters")
        chatid = str(message.chat_id)
        try:
        	del filters[chatid]
        	self._db.set("FilterModule", "filters", filters)
        	await message.edit("<code>All filters successfully removed from the list.</code>")
        except:
        	await message.edit("<code>There are no filters to clear out in this chat.</code>")
        	    	
    async def filterscmd(self, message):
        """Shows saved filters."""
        filters = ""
        filt = self._db.get("FilterModule", "filters")
        chatid = str(message.chat_id)
        try:
        	for i in filt[chatid]:
        		filters += "-  <b>" + str(i) + "</b>\n"
        		pass
        except: pass
        filterl = "<b>Filters that you saved in this chat: </b>\n\n" + filters
        if filters.strip() != "":
        	await message.edit(filterl)
        else:
        	await message.edit('<code>No filters found in this chat.</code>')
        	
    async def watcher(self, message):
    	#BOTLOG_CHATID CHECK
    	try:
    		await self._client.get_entity(BOTLOG_CHATID)
    		botlog = True
    	except:botlog = False
    	args = str(message.text.lower())
    	filters = self._db.get("FilterModule", "filters")
    	chatid = str(message.chat_id)
    	if str(filters).find(chatid) != -1 and filters:
    		for key in filters[chatid]:
    			val = filters[chatid][str(key)]
    			if args.find(str(key)) != -1:
    				try:
    					if botlog:
    						loggedfilter = await message.client.get_messages(entity=BOTLOG_CHATID, ids=int(val))
    					else:
    						loggedfilter = await message.client.get_messages(entity=message.chat_id, ids=int(val))
    					if loggedfilter.media:
    						try:
    							await message.client.send_message(message.chat_id, loggedfilter.message, reply_to=message.id, file=loggedfilter.media)
    							return
    						except:await message.client.send_message(message.chat_id, loggedfilter.message, reply_to=message.id, file=None)
    					return
    				except:
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
    							argspr= arg.split(" ")
    							try:await load.dispatch(argspr[0], ifcmd)
    							except:pass
    						return
    			pass		
