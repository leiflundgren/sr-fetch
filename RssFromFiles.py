import common

class RssFromFiles(object):
    """description of class"""

    extensions = ['.mp3', '.m4a']

    def __init__(self, *dirs):
        files = getAllFiles(dirs)
        fileInfos = [self.getFileInfo(f) for f in files]
        pass

    def trace(self, lvl, *args):
        common.trace(lvl, 'RssFromFiles: ', args)

    def getAllFiles(self, dirs):
        self.trace(6, 'Looking in dirs ' + dirs)
        res = []

        for d in dirs:
            for root, dirnames, filenames in os.walk(d):
              for filename in filenames:
                  if filename.lower().endswith(extensions):
                    res.append(os.path.join(root, filename))

        self.trace(8, 'Got files: ', res)
        return res

    def getFileInfo(self, file):
        pass

    def buildRss(self):
        pass

    @property
    def rss(self):
        return self.rss

if __name__ == '__main__':
    common.tracelevel = 8
    print RssFromFiles('C:\Users\llundgren\Downloads').rss

