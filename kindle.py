__author__ = 'acher'
# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
import sqlite3 as lite
import sys

from anki.importing.noteimp import NoteImporter, ForeignNote

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.
desc = "Test"
cardType = "Basic (and reversed card)-1e33a"

def testFunction():
    # showInfo("Card count: %d" % cardCount)

    did = mw.col.decks.id(desc)
    mw.col.decks.select(did)
    # set note type for deck
    model = mw.col.models.byName(cardType)
    deck = mw.col.decks.get(did)
    deck['mid'] = model['id']
    mw.col.decks.save(deck)

    model['did'] = did
    mw.col.models.save(model)

    # import into the collection
    importer = KindleImporter(mw.col, "ololofile")
    importer.initMapping()
    importer.run()
    showInfo("Imported \n" + '\n'.join(importer.log))

# create a new menu item, "test"
action = QAction("Import new words from Kindle", mw)
# set it to call testFunction when it's clicked
mw.connect(action, SIGNAL("triggered()"), testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

class KindleImporter(NoteImporter):
    imported = 0
    importMode = 1

    def __init__(self, *args):
        NoteImporter.__init__(self, *args)

    def readWords(self):
        con = None
        try:
            con = lite.connect('/home/acher/Documents/Anki/addons/vocab.db')
            cur = con.cursor()
            cur.execute('SELECT w.stem, l.usage FROM WORDS as w join LOOKUPS as l on w.id = l.word_key ORDER BY w.timestamp ASC;')
            rows = cur.fetchall()
            return rows
        except lite.Error, e:
            sys.stderr.write("Error %s:\n" % e.args[0])
            raise IOError("can't read DB")
        finally:
            if con:
                con.close()

    def foreignNotes(self):
        self.open()
        notes = []
        words = self.readWords()
        self.imported = len(words)
        for row in words:
            note = self.noteFromFields(row)
            notes.append(note)
        return notes

    def noteFromFields(self, fields):
        note = ForeignNote()
        note.fields.extend([x for x in fields])
        note.tags.extend(['kindle'])
        return note

    def fields(self):
        "The number of fields."
        return 2
