class Source(object):

    def __init__(self, config):
        pass

    def getPosts(self, tags=[]):
        raise NotImplementedError()


from evernotesource import EvernoteSource