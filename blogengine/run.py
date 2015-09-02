import os
import argparse
import ConfigParser

from . import BlogEngine, getLogger
import source
import output
from upload import FtpUpload
from entity import Site


# setup logger
import logging
import sys

root = getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def main():
    default_config = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config', 'config.conf'))

    parser = argparse.ArgumentParser(description='Connects to an Evernote account and creates a blog out of the marked posts')
    parser.add_argument('--config', '-c', dest='configfile', action='store',default=default_config,
                       help='Config file to use. Uses %s as default' % default_config)
    #parser.add_argument('-v', '--verbose', action='count', dest="verbosity", default=0)
    parser.add_argument('-s', '--source', action='store', dest="source", default='evernote')
    parser.add_argument('-o', '--output', action='store', dest="output", default='website')
    parser.add_argument('-w', '--webserver', action='store_true', dest="webserver", default=False)
    parser.add_argument('-f', '--ftp', action='store_true', dest="ftp", default=False)
    parser.add_argument('-r', '--rss', action='store_true', dest="rss", default=False)

    parser.add_argument('-O', '--output-dir', action='store', dest='output_dir', default='./output')
    args = parser.parse_args()

    # Set up the environment
    if not os.path.exists(args.configfile):
        sys.stderr.write("Configfile %s could not be found" % args.configfile)
        sys.exit(1)

    config = ConfigParser.RawConfigParser()
    config.read(args.configfile)

    # Create Source and Output Objects
    sourceObj = getattr(source, '%sSource' % args.source.title())(**{x[0]: x[1] for x in config.items(args.source)})
    outputObj = getattr(output, '%sOutput' % args.output.title())(**{x[0]: x[1] for x in config.items(args.output)})
    site = Site(**{x[0]: x[1] for x in config.items('site')})

    # Building and running the site
    engine = BlogEngine(site=site, source=sourceObj, output=outputObj, basedir=args.output_dir)
    engine.build(rss=args.rss)

    # upload the build if needed
    if args.ftp:
        ftp = FtpUpload(**{x[0]: x[1] for x in config.items('ftp')})
        ftp.upload(args.output_dir)

    # run the buildin webserver to serve the page
    if args.webserver:
        engine.runHttp()

if __name__ == "__main__":
    main()