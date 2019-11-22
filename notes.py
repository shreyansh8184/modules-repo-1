import telethon
import ast
import itertools
import inspect
from .. import loader, utils

import logging
from telethon import functions, types
from userbot import BOTLOG_CHATID
logger = logging.getLogger("NotesModule")


def register(cb):
    cb(Notes())


class Notes(loader.Module):
    """Saves some texts or media to access them anytime you want"""

    def __init__(self):
        self.name = _("Notes")
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me()

    async def notecmd(self, message):
        """Adds a note into the list."""
        # BOTLOG_CHATID CHECK
        try:
            await self._client.get_entity(BOTLOG_CHATID)
            botlog = True
        except BaseException:
            botlog = False
        noten = utils.get_args_raw(message)
        getr = await message.get_reply_message()
        chatid = message.chat_id
        notes = self._db.get("NotesModule", "notes")
        if noten.strip() == (""):
            await message.edit("<code>Please type a name for the note.</code>")
            return
        else:
            noten = noten.split(" ")
        if not notes:
            notes = {}
            notes.setdefault(str(chatid), {})
            pass
        if str(notes).find(str(chatid)) == -1:
            notes.setdefault(str(chatid), {})
            pass
        if not getr:
            if str(noten[0]).isspace():
                await message.edit("<code>Please enter the name of your note first.</code>")
                return
            else:
                name = noten[0]
            if len(noten) is 1:
                await message.edit("<code>Please reply to a message or enter a text to save as note.!</code>")
                return
            else:
                value = noten[1]
        else:
            name = noten[0]
            value = getr.text
        if getr and getr.media:
            if botlog:
                lognote = await message.client.get_messages(entity=message.chat_id, ids=getr.id)
                try:
                    fwd = await self._client.send_message(BOTLOG_CHATID, lognote.text, file=lognote.media, link_preview=False)
                except BaseException:
                    fwd = await self._client.send_message(BOTLOG_CHATID, lognote.text, file=None, link_preview=False)
                notes[str(chatid)][noten[0]] = str(fwd.id)
            else:
                notes[str(chatid)][noten[0]] = str(getr.id)
            self._db.set("NotesModule", "notes", notes)
            await message.edit("<code>Note '" + noten[0] + "' successfully saved into the list.</code>")
            return
        else:
            notes[str(chatid)][str(name)] = str(value)
            self._db.set("NotesModule", "notes", notes)
            await message.edit("<code>Note '" + noten[0] + "' successfully added into notes.</code>")
            return
        

    async def notermcmd(self, message):
        """Removes a note from the list."""
        noten = utils.get_args_raw(message)
        notes = self._db.get("NotesModule", "notes")
        chatid = message.chat_id
        while noten.strip() == "" or not noten:
            await message.edit("<code>Please specify the name of the note.</code>")
            return
        try:
            del notes[str(chatid)][str(noten)]
            await message.edit("<code>Note '" + noten + "' successfully removed from the list.</code>")
            self._db.set("NotesModule", "notes", notes)
        except BaseException:
            await message.edit("<code>Note '" + noten + "' not found in notes list</code>")

    async def notesrmcmd(self, message):
        """Clears out the note list."""
        notes = self._db.get("NotesModule", "notes")
        chatid = message.chat_id
        try:
            del notes[str(chatid)]
            self._db.set("NotesModule", "notes", notes)
            await message.edit("<code>All notes successfully removed from the list.</code>")
        except BaseException:
            await message.edit("<code>There are no notes to clear out in this chat.</code>")

    async def notescmd(self, message):
        """Shows saved notes."""
        notes = ""
        notet = self._db.get("NotesModule", "notes")
        chatid = message.chat_id
        try:
            for i in notet[str(chatid)]:
                notes += "-  <b>" + str(i) + "</b>\n"
                pass
        except BaseException:
            pass
        notel = "<b>Notes that you saved in this chat: </b>\n\n" + notes
        if notes.strip() != "":
            await message.edit(notel)
        else:
            await message.edit('<code>No notes found in this chat.</code>')
            
    async def getnotecmd(self, message):
        """Gets the saved note."""
        # BOTLOG_CHATID CHECK
        try:
            await self._client.get_entity(BOTLOG_CHATID)
            botlog = True
        except BaseException:
            botlog = False
        notes = self._db.get("NotesModule", "notes")
        chatid = str(message.chat_id)
        args = utils.get_args_raw(message)
        if not notes or str(notes).find(str(chatid)) == -1:
            await message.edit('<code>There are no notes in this chat.</code>')
            return
        if str(notes[chatid]).find(str(args)) == -1:
            await message.edit('<code>No note found in that name.</code>')
        else:
            val = notes[str(chatid)][str(args)]
            try:
                if botlog:
                    loggednote = await message.client.get_messages(entity=BOTLOG_CHATID, ids=int(val))
                else:
                    loggednote = await message.client.get_messages(entity=message.chat_id, ids=int(val))
                await message.client.send_message(message.chat_id, loggednote.message, reply_to=message.id, file=loggednote.media)
                return
            except BaseException:
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
                    argspr= arg.split(" ")
                    ifcmd = await message.reply(arg)
                    if exec is True:
                        try:
                            await load.dispatch(argspr[0], ifcmd)
                        except BaseException:
                            pass
                    return

    async def watcher(self, message):
        argsraw = message.text
        notes = self._db.get("NotesModule", "notes")
        # BOTLOG_CHATID CHECK
        try:
            await self._client.get_entity(BOTLOG_CHATID)
            botlog = True
        except BaseException:
            botlog = False
        if argsraw.find("#") == 0 and notes:
            chatid = str(message.chat_id)
            args = argsraw.replace("#", "")
            if str(list(notes)).find(str(chatid)) == -1 or not notes:
                return
            for key in notes[chatid]:
                if args == str(key):
                    val = notes[chatid][str(key)]
                    try:
                        if botlog:
                            loggednote = await message.client.get_messages(entity=BOTLOG_CHATID, ids=int(val))
                        else:
                            loggednote = await message.client.get_messages(entity=message.chat_id, ids=int(val))
                            try:
                                await message.client.send_message(message.chat_id, loggednote.message, reply_to=message.id, file=loggednote.media)
                            except BaseException:
                                await message.client.send_message(message.chat_id, loggednote.message, reply_to=message.id, file=None)
                        await message.client.send_message(message.chat_id, loggednote.message, reply_to=message.id, file=loggednote.media)
                        return
                    except BaseException:
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
                                argspr= arg.split(" ")
                                ifcmd = await message.reply(arg)
                                if exec is True:
                                    try:
                                        await load.dispatch(argspr[0], ifcmd)
                                    except BaseException:
                                        pass
                                return
                pass
