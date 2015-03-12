__author__ = 'pesua'
from aqt.browser import Browser
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
import sqlite3 as lite
import sys

from anki.importing.noteimp import NoteImporter, ForeignNote

desk = "Test"
cardType = "Basic (and reversed card)-1e33a"

def findDB():
    searchDir = "/media"
    for root, dirs, files in os.walk(searchDir):
        if ("vocab.db" in files) and root.endswith("system/vocabulary"):
            return os.path.join(root, "vocab.db")

def importCards():
    did = mw.col.decks.id(desk)
    mw.col.decks.select(did)
    # set note type for deck
    model = mw.col.models.byName(cardType)
    deck = mw.col.decks.get(did)
    deck['mid'] = model['id']
    mw.col.decks.save(deck)

    model['did'] = did
    mw.col.models.save(model)

    # import into the collection
    db = findDB()
    if db:
        importer = KindleImporter(mw.col, db)
        importer.initMapping()
        importer.run()

        showInfo("Import log: \n" + '\n'.join(importer.log))

        # display imported cards
        browser = Browser(mw)
        browser.form.searchEdit.setEditText("added:1 tag:kindle mid:" + `model['id']`)
        browser.form.searchEdit.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.KeyboardModifierMask))
    else:
        showInfo("Can't find kindle")


action = QAction("Import new words from Kindle", mw)
mw.connect(action, SIGNAL("triggered()"), importCards)
mw.form.menuTools.addAction(action)

class KindleImporter(NoteImporter):
    importMode = 1

    def __init__(self, *args):
        NoteImporter.__init__(self, *args)
        self.dbFile = args[1]
        self.log.append("Importing words from file " + self.dbFile + " to desk " + desk)

    def readWords(self):
        con = None
        try:
            con = lite.connect(self.dbFile)
            cur = con.cursor()
            cur.execute('SELECT w.stem, l.usage FROM WORDS as w join LOOKUPS as l on w.id = l.word_key where w.category = 0 ORDER BY w.timestamp ASC;')
            rows = cur.fetchall()
            return rows
        except lite.Error, e:
            sys.stderr.write("Error %s:\n" % e.args[0])
            raise IOError("can't read kindle DB")
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
        note.fields.extend([fields[0],'', fields[1]])
        note.tags.extend(['kindle'])
        return note

    def fields(self):
        "The number of fields."
        return 3
