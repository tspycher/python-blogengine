import os, sys
import time
import pytz
from output import Output
from . import getLogger
from feedgen.feed import FeedGenerator

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

    def build(self, rss=False):
        if rss:
            self.site.rss_url = '/rss.xml'
            fg = FeedGenerator()
            fg.title(self.site.name)
            fg.author({'name': self.site.author})
            fg.link(href=self.site.base_url, rel='alternate')
            fg.subtitle(self.site.description)

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
            if rss:
                fe = fg.add_entry()
                fe.id("%s/%s" % (self.site.base_url,p.permalink))
                fe.title(p.title)
                fe.published(p.created_at.replace(tzinfo=pytz.timezone(self.site.timezone)))
                category = []
                for t in p.tags:
                    category.append({'term': t})
                fe.category(category)
                fe.content(p.content)

            Output.storeData(os.path.join(self.basedir, p.permalink), self.output.render(self.site, post=p))
            getLogger().debug("Adding Post \"%s\" (%s)", p.title, p.slug)

        posts = sorted(posts, key=lambda k: k.created_at, reverse=True)
        Output.storeData(os.path.join(self.basedir, 'index.html'), self.output.render(self.site, posts=posts, post=None, is_home=True, pagination=None))

        if rss:
            Output.storeData(os.path.join(self.basedir, 'rss.xml'), fg.rss_str(pretty=True))
            getLogger().debug("You awesome RSS feed has been generated")


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