from .. import loader, utils

import logging
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

    async def savecmd(self, message):
        """Adds a note into the chat."""
        args = ((utils.get_args_raw(message)).strip()).split(",")
        chatid = message.chat_id
        notes = self._db.get("NotesModule", "notes", {})
        if args[0] == "":
            await message.edit(_("<b>Enter a name for the note first!</b>"))
            return
        name = args[0]
        if chatid not in notes:
            notes.setdefault(chatid, {})
        if not message.is_reply:
            if len(args) == 1:
                await message.edit(_("<b>Please reply to a message or enter a text to save as note.!</b>"))
                return
            else:
                value = args[1]
                msg_to_log = await self._db.store_asset(value)
        else:
            value = await message.get_reply_message()
            msg_to_log = await self._db.store_asset(value)
        notes[chatid][name] = msg_to_log
        self._db.set("NotesModule", "notes", notes)
        await message.edit(_("<b>Note ''{}'' has been successfully saved in this chat.</b>".format(name)))

    async def clearcmd(self, message):
        """Removes a note from the chat."""
        noten = utils.get_args_raw(message)
        notes = self._db.get("NotesModule", "notes")
        chatid = message.chat_id
        if not noten or not noten:
            await message.edit(_("<b>Please specify the name of the note.</b>"))
            return
        try:
            del notes[chatid][noten]
            await message.edit(_("<b>Note ''{}'' successfully removed from the list.</b>".format(noten)))
            self._db.set("NotesModule", "notes", notes)
        except KeyError:
            await message.edit(_("<b>Note ''{}'' not found in notes list</b>".format(noten)))

    async def clearallcmd(self, message):
        """Clears out the notes."""
        notes = self._db.get("NotesModule", "notes", {})
        chatid = message.chat_id
        try:
            del notes[chatid]
            self._db.set("NotesModule", "notes", notes)
            await message.edit(_("<b>All notes successfully removed from the list.</b>"))
        except KeyError:
            await message.edit(_("<b>There are no notes to clear out in this chat.</b>"))

    async def notescmd(self, message):
        """Shows saved notes."""
        notes = ""
        notet = self._db.get("NotesModule", "notes", {})
        chatid = message.chat_id
        try:
            for i in notet[chatid]:
                notes += "<b> -  " + str(i) + "</b>\n"
                pass
        except KeyError:
            pass
        notel = "<b>Notes that you saved in this chat: </b>\n\n" + notes
        if notes.strip() != "":
            await message.edit(_(notel))
        else:
            await message.edit(_('<b>No notes found in this chat.</b>'))

    async def notecmd(self, message):
        notes = self._db.get("NotesModule", "notes", {})
        chatid = message.chat_id
        args = utils.get_args_raw(message)
        current_prefix = self._db.get("friendly-telegram.main", "command_prefix", {})
        if not current_prefix:
            current_prefix = "."
        if chatid not in notes:
            await message.edit(_('<b>There are no notes in this chat.</b>'))
            return
        if args not in notes[chatid]:
            await message.edit(_('<b>No note found in that name.</b>'))
            return
        else:
            # This is to execute cmds
            exec = True
            for load in self.allloaders:
                if load.client is self._client:
                    break
            id = notes[chatid][args]
            value = await self._db.fetch_asset(id)
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
                    return
                else:
                    cmdspl = cmd.lower().split(" ")
                    respond = await message.reply(value)
                    try:
                        await load.dispatch(cmdspl[0], respond)
                    except ValueError:
                        pass
            else:
                await message.reply(value)
                return

    async def watcher(self, message):
        # This is to execute cmds
        exec = True
        for load in self.allloaders:
            if load.client is self._client:
                break
        args = str(message.text.lower())
        notes = self._db.get("NotesModule", "notes")
        chatid = message.chat_id
        current_prefix = self._db.get("friendly-telegram.main", "command_prefix", {})
        if not current_prefix:
            current_prefix = "."
        if notes and chatid in notes:
            for key in notes[chatid]:
                if key.lower() in args.lower():
                    id = notes[chatid][key]
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
                            await message.respond(value)
                        else:
                            cmdspl = cmd.lower().split(" ")
                            respond = message.respond(value)
                            try:
                                await load.dispatch(cmdspl[0], respond)
                            except Exception:
                                pass
                    else:
                        await message.respond(value)
                        return
