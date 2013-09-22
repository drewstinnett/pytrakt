class ConfigLoader:

    def __init__(
        self,
        rcfile='~/.trakttv.conf'
    ):
        import os
        import sys
        rcfile = os.path.expanduser(rcfile)

        if not os.path.exists(rcfile):
            sys.stderr.write("Missing rcfile: %s\n" % rcfile)
            sys.exit(2)

        import ConfigParser

        config = ConfigParser.RawConfigParser()
        config.read(rcfile)

        self.info = {
            'auth': {}
        }

        self.info['auth']['apikey'] = config.get('authentication', 'apikey')
        self.info['auth']['username'] = config.get('authentication',
                                                   'username')
        self.info['auth']['password'] = config.get('authentication',
                                                   'password')

    def __getitem__(self, item):
        return self.info[item]
