import common

class HttpProxyer(object):
    """A class that act as a http proxy"""

    def log(self, level, *args):
        common.trace(level, self.app_name, ': ', args)


