import uuid
import datetime
from slugify import slugify
from . import BaseEntity
from xml.dom import minidom

class Post(BaseEntity):
    id = None

    title = None
    created_at = None
    published = False
    author = None
    tags = None
    content = None
    slug = None

    def __init__(self):
        self.id = str(uuid.uuid4())

    @property
    def permalink(self):
        return "%s.html" % self.slug

    @classmethod
    def createFromNote(cls, note):
        p = cls()
        p.title = note.title
        p.tags = map(lambda x: x.name, note.tagNames)
        p.published = True if note.active else False
        p.created_at = datetime.datetime.fromtimestamp(note.created/1000)
        p.slug = slugify(p.title)
        p.author = note.attributes.author
        p.content = p.parseContent(note.content)
        return p

    def parseContent(self, content):
        xmldoc = minidom.parseString(content)
        x = []
        for c in xmldoc.getElementsByTagName('en-note')[0].childNodes:
            x.append(c.toprettyxml(indent="  ", encoding='utf-8'))
        x = "".join(x)
        return unicode(x, 'utf-8')
