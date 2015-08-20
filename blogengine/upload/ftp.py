import ftplib
import os
from .. import getLogger

class FtpUpload(object):
    session = None
    remote_basepath = None

    def __init__(self, host, username, password, basepath = '/'):
        self.session = ftplib.FTP(host, username,password)
        self.remote_basepath = basepath

    def upload(self, src, dst = None):
        names = os.listdir(src)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(self.remote_basepath if not dst else dst, name)

            if os.path.isdir(srcname):
                getLogger().info("Create Dir %s" % (dstname))
                try:
                    self.session.mkd(dstname)
                except ftplib.error_perm:
                    pass
                self.upload(srcname, dstname)
            else:
                getLogger().info("Uploading %s to %s" % (srcname, dstname))
                #self.session.storlines("STOR " + dstname, open(srcname, 'r'))
                with open(srcname, 'rb') as ftpup:
                    self.session.storbinary('STOR ' + dstname, ftpup)