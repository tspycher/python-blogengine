from . import BaseEntity

class Site(BaseEntity):
    type = 'unknown'

    disqus = None
    base_url = None
    author = None
    name = None
    analytics = None
    cover_photo = None
    twitter = None
    facebook = None
    googleplus = None
    linkedin = None
    atom_url = None
    avatar = None

    def __init__(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])
