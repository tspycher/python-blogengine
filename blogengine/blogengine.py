import os, sys
import time
from output import Output
from . import getLogger

class BlogEngine(object):
    source = None
    output = None
    site = None
    basedir = None

    def __init__(self, site, source, output, basedir):
        self.site = site
        self.source = source
        self.output = output
        self.basedir = basedir

    def build(self):
        start = time.time()
        getLogger().info("Copy Assets")
        self.output.copyAssets(self.basedir)

        getLogger().info("Start Build of static content")
        posts = []
        for p in self.source.getPosts():
            if not p.published:
                getLogger().info("Ingnoring draft Post %s (%s)", p.title, p.slug)
                continue

            posts.append(p)
            Output.storeData(os.path.join(self.basedir, p.permalink), self.output.render(self.site, post=p))
            getLogger().debug("Adding Post \"%s\" (%s)", p.title, p.slug)

        posts = sorted(posts, key=lambda k: k.created_at, reverse=True)
        Output.storeData(os.path.join(self.basedir, 'index.html'), self.output.render(self.site, posts=posts, post=None, is_home=True, pagination=None))

        getLogger().info("It took %d seconds to generate your awesome blog" % (time.time() - start))

    def runHttp(self, port=8080):
        try:
            import tornado.ioloop
            import tornado.web
        except:
            getLogger().critical("please install tornado by invoking 'pip install tornado' in order to run the optional webserver")
            sys.exit(9)

        getLogger().info("Running Tornado Webserver at http://localhost:%d" % port)
        handlers = [(r'/(.*)', tornado.web.StaticFileHandler, {'path': self.basedir, "default_filename": "index.html"})]
        application = tornado.web.Application(handlers, debug=True)
        application.listen(port)
        try:
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            getLogger().info("Server terminated by keystroke, byebye")