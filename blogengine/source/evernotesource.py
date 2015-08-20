import base64
import hashlib
import re

from evernote.api.client import EvernoteClient, NoteStore
from blogengine.entity import Post
from . import Source

class EvernoteSource(Source):
    _token = None
    _client = None
    sandbox = False
    tag = None
    tag_published = None

    def __init__(self, token, sandbox = None, tag='blog', tag_published='published'):
        self._token = token
        self.sandbox = True if sandbox else False
        self.tag = tag
        self.tag_published = tag_published

    @property
    def client(self):
        if self._client:
            return self._client
        self._client = EvernoteClient(token=self.token, sandbox=self.sandbox)
        return self._client

    @property
    def token(self):
        if self._token:
            return self._token
        else:
            # Todo: is there an alternative to get the token?
            return ""

    def getPosts(self):
        for n in self.getNotes():
            yield Post.createFromNote(n)

    def getNotes(self):
        words = ",".join(map(lambda x: "tag:%s" % str(x), [self.tag]))

        noteStore = self.client.get_note_store()

        result_notes = noteStore.findNotesMetadata(self.token, NoteStore.NoteFilter(words=words),0,99999,NoteStore.NotesMetadataResultSpec())
        for note in result_notes.notes:
            notedata = noteStore.getNote(self.token, note.guid, True, False, False, False)

            # get resources of the note
            if notedata.resources:
                for r in notedata.resources:
                    resource = noteStore.getResource(r.guid, True, False, True, False)
                    md5 = hashlib.md5(resource.data.body).hexdigest()
                    html = '<img src="data:%(file_type)s;base64,%(file_content)s" alt="embedded image from evernote" />' % {
                        'file_content': base64.b64encode(resource.data.body),
                        'file_type': resource.mime
                    }
                    notedata.content = re.sub("(?=<en-media).*%s.*/>" % md5, html, notedata.content)

            notedata.active = False
            notedata.tagNames = []
            for tagguid in notedata.tagGuids:
                tagobject = noteStore.getTag(self.token, tagguid)
                if tagobject.name.lower() == self.tag.lower():
                    continue
                if tagobject.name.lower() == self.tag_published.lower():
                    notedata.active = True
                    continue
                notedata.tagNames.append(tagobject)
            yield notedata