import ConfigParser


class Config(object):
    """description of class"""

    class Feed(object):
        def __init__(self, config, section_name):
            self.config = config
            self.section_name = section_name
            pass

        def load(self):
            self.title = self.config.get(self.section_name, 'title')
            self.url = self.config.get(self.section_name, 'url')

        def save(self):
            self.config.set(self.section_name, 'title', self.title)
            self.config.set(self.section_name, 'url', self.url)


    def __init__(self, configfilething):
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfilething)
        pass

    def feed(self, feed_name):
        section_name = 'feed ' + feed_name
        x = self.config.options(section_name)
        if x is None:
            return None
        feedobj = Config.Feed(self.config, section_name)
        feedobj.load()
        return feedobj

    def add_feed(self, title, url):
        section_name = 'feed ' + title
        self.config.add_section(section_name)
        feedobj = Config.Feed(self.config, section_name)
        feedobj.title = title
        feedobj.url = url
        feedobj.save()
        
