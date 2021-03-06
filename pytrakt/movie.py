class Movie:

    def __init__(
            self,
            trakt_api,
            imdbid=None,
            movie_json=None,
    ):
        if not imdbid and not movie_json:
            import sys
            sys.stderr.write("You need either an imdb id or json\n")
            sys.exit(2)

        self.t = trakt_api

        ## TODO:  normalize these options, right now they're going to
        ## different spots
        if movie_json:
            self.info = movie_json
        elif imdbid:
            self.info = self.t.get_results(
                '/movie/summary.json/APIKEY/%s' % (imdbid)
            )

    def get_summary(self):
        import json
        pydata = {
            'username': self.t.username,
            'password': self.t.password,
        }
        jsondata = json.dumps(pydata)
        clen = len(jsondata)

        import urllib2
        req = urllib2.Request(
            "%s/movie/summary.json/%s/%s" % (self.t.url_api, self.t.apikey,
                                             self['imdb_id']),
            jsondata, {
                'Content-Type': 'application/json',
                'Content-Length': clen
            }
        )
        f = urllib2.urlopen(req)
        response = json.load(f)
        f.close()
        self.info['summary'] = response

    def __getitem__(self, item):
        return self.info[item]

    def __repr__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding("latin-1")
        return ("%s (%s)" % (self.info['title'], self.info['year']))
