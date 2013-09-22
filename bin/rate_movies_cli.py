#!/usr/bin/env python
import sys

from pytrakt import TraktAPI, ConfigLoader

cl = ConfigLoader()

t = TraktAPI(
    apikey=cl['auth']['apikey'],
    username=cl['auth']['username'],
    password=cl['auth']['password']
)

loader = []
skipped_movies = []

while True:
    ## Make sure the loader always has movies
    while (len(loader) == 0):
        loader = []
        for movie in t.get_movie_recommendations():
            if movie['imdb_id'] not in [x['imdb_id'] for x in skipped_movies]:
                loader.append(movie)
        loader.reverse()

    movie = loader.pop()

    valid_rating = None

    t.clear_terminal()

    while not valid_rating:
        print "?: help, d: dismiss, a: add to watchlist, i: info"
        t.get_rating_help()
        print "Rate %s:" % movie
        print
        print "%s (%s) %s%%" % (movie['title'], movie['year'],
                                movie['ratings']['percentage'])
        print movie['overview']
        print

        movie.get_summary()
        print
        print "Director: %s" % (", ".join(
            [x['name'] for x in movie['summary']['people']['directors']]))
        print "Actors: %s" % (", ".join(
            [x['name'] for x in movie['summary']['people']['actors']]))
        print

        rating = raw_input("Rating (0-10): ")
        rating = rating.strip()

        if rating in ['q', 'quit', 'exit']:
            sys.exit(0)

        if rating == '?':
            pass

        ## Skip here
        if rating in ['s', 'skip']:
            skipped_movies.append(movie)
            valid_rating = True
            continue

        if rating in ['a', 'add']:
            t.add_movie_watchlist(movie)
            valid_rating = True
            continue

        if rating in ['d', 'dismiss']:
            if t.dismiss_movie_recommendation(movie):
                valid_rating = True
                continue

        try:
            rating = int(rating)
        except:
            pass

        if t.rate_movie(movie, rating):
            valid_rating = True
            continue
