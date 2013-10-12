class TraktAPI:

    def __init__(self, apikey, username=None, password=None):
        import hashlib
        self.apikey = apikey
        self.username = username
        self.password = hashlib.sha1(password).hexdigest()
        self.url_api = 'https://api.trakt.tv/'

        self.rating_system = {
            1: 'Weak Sauce :(',
            2: 'Terrible',
            3: 'Bad',
            4: 'Poor',
            5: 'Meh',
            6: 'Fair',
            7: 'Good',
            8: 'Great',
            9: 'Superb',
            10: 'Totally Ninja!',
        }

    def clear_terminal(self):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def valid_ratings(self):
        return self.rating_system.keys()

    def get_rating_help(self):
        keys = self.rating_system.keys()
        keys.sort()
        print
        print "Rating values"
        for k in keys:
            print "%-3s %s" % (k, self.rating_system[k])
        print

    def add_movie_watchlist(self, movie):
        print "Adding %s to watchlist" % movie
        response = self.get_results(
            "/movie/watchlist/APIKEY",
            authenticate=True,
            params={'movies': [{'imdb_id': movie['imdb_id']}]}
        )

        if response['status'] != 'success':
            import sys
            sys.stderr.write("Failed\n")
            sys.exit(2)

        return True

    def mark_movie_seen(self, movie):
        import json
        pydata = {
            'username': self.username,
            'password': self.password,
            'movies': [
                {
                    'imdb_id': movie['imdb_id']
                }
            ]
        }
        jsondata = json.dumps(pydata)
        clen = len(jsondata)

        import urllib2
        req = urllib2.Request(
            self.url_api + "/movie/seen/" + self.apikey,
            jsondata, {
                'Content-Type': 'application/json',
                'Content-Length': clen
            }
        )
        f = urllib2.urlopen(req)
        response = json.load(f)
        f.close()

        if response['status'] != 'success':
            import sys
            sys.stderr.write("Failed\n")
            sys.exit(2)

        return True

    def rate_movie(self, movie, rating):
        try:
            rating = int(rating)
        except:
            return None
        print "Rating %s a %s" % (movie, rating)

        import json
        pydata = {
            'username': self.username,
            'password': self.password,
            'imdb_id': movie['imdb_id'],
            'rating': rating
        }
        jsondata = json.dumps(pydata)
        clen = len(jsondata)

        import urllib2
        req = urllib2.Request(
            self.url_api + "/rate/movie/" + self.apikey,
            jsondata, {
                'Content-Type': 'application/json',
                'Content-Length': clen
            }
        )
        f = urllib2.urlopen(req)
        response = json.load(f)
        f.close()

        if response['status'] != 'success':
            import sys
            sys.stderr.write("Failed\n")
            sys.exit(2)

        ## Go ahead and mark as seen too
        self.mark_movie_seen(movie)

        return True

    def dismiss_movie_recommendation(self, movie):
        print "Dismissing %s" % movie

        response = self.get_results(
            '/recommendations/movies/dismiss/APIKEY',
            authenticate=True,
            params={'imdb_id': movie['imdb_id']}
        )

        if response['status'] != 'success':
            import sys
            sys.stderr.write("Failed\n")
            sys.exit(2)

        return True

    def get_genre_slugs(self):
        response = self.get_results(
            '/genres/movies.json/APIKEY',
        )

        return [x['slug'] for x in response]

    def get_rated_movies(self):
        movies = []
        response = self.get_results(
            '/activity/user.json/APIKEY/USERNAME/movie/rating/0',
            authenticate=True,
        )
        for movie in [x['movie'] for x in response['activity']]:
            movies.append(movie)

        return movies

    def get_trending_movies(self, ignore_seen=True):
        movies = []
        response = self.get_results(
            '/movies/trending.json/APIKEY/',
            authenticate=None,
        )
        for movie in response:
            from pytrakt.movie import Movie
            m = Movie(self, movie_json=movie)

            add_movie = True
            if ignore_seen:
                try:
                    if self.is_movie_seen(movie):
                        add_movie = None
                except:
                    pass

            if add_movie:
                movies.append(m)

        return movies

    def is_movie_seen(self, movie):
        #print movie
        response = self.get_results(
            '/activity/user/movies.json/APIKEY/USERNAME/%s/seen' % (
                movie['imdb_id']),
            authenticate=True
        )
        try:
            activity_length = len(response['activity'])
        except:
            activity_length = 0

        if activity_length > 0:
            return True
        else:
            return None

    def get_movie_recommendations(
        self,
        genre=None,
        start_year=None,
        end_year=None
    ):
        print "Getting movie recommendations"

        params = {
            'hide_collected': True,
            'hide_watchlisted': True
        }

        ## Filter
        if genre:
            params['genre'] = genre
        if start_year:
            params['start_year'] = start_year
        if end_year:
            params['end_year'] = end_year

        response = self.get_results(
            '/recommendations/movies/APIKEY',
            authenticate=True,
            params=params
        )
        movies = []

        for movie_json in response:
            from pytrakt.movie import Movie
            m = Movie(self, movie_json=movie_json)
            movies.append(m)

        return movies

    def get_results(
        self,
        url,
        authenticate=None,
        params={}
    ):
        ## Replace some shortcuts
        url = url.replace('APIKEY', self.apikey)
        url = url.replace('USERNAME', self.username)

        post_data = {}
        if authenticate:
            post_data['username'] = self.username
            post_data['password'] = self.password

        ## Do extra params here
        for k, v in params.iteritems():
            post_data[k] = v

        import json
        jsondata = json.dumps(post_data)
        clen = len(jsondata)

        full_url = "%s%s" % (self.url_api, url)

        import urllib2
        req = urllib2.Request(
            full_url,
            jsondata, {
                'Content-Type': 'application/json',
                'Content-Length': clen
            }
        )
        f = urllib2.urlopen(req)
        response = json.load(f)
        f.close()

        return response
