#!/usr/bin/env python
import sys
from pytrakt import TraktAPI, ConfigLoader

import argparse


cl = ConfigLoader()

t = TraktAPI(
    apikey=cl['auth']['apikey'],
    username=cl['auth']['username'],
    password=cl['auth']['password']
)

loader = []
skipped_movies = []
all_genres = t.get_genre_slugs()

parser = argparse.ArgumentParser(description='Rate some movies on trakt.tv')
parser.add_argument('-g', '--genre', help='Genre slug to limit results to',
                    choices=all_genres)
parser.add_argument('-s', '--start-year', help='Start year for results',
                    type=int)
parser.add_argument('-e', '--end-year', help='End year for results',
                    type=int)
args = parser.parse_args()
genre = args.genre
start_year = args.start_year
end_year = args.end_year

while True:
    ## Make sure the loader always has movies
    while (len(loader) == 0):
        loader = []
        for movie in t.get_movie_recommendations(
                genre=genre, start_year=start_year, end_year=end_year):
            if movie['imdb_id'] not in [x['imdb_id'] for x in skipped_movies]:
                loader.append(movie)
        loader.reverse()

    movie = loader.pop()

    valid_rating = None
    ## TODO:  Do we really need a help option?
    show_help = None

    while not valid_rating:
        t.clear_terminal()
        print "?: help"
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

        if show_help:
            print "Additional options:"
            print "d: dismiss recommendation"
            print "a: add to watchlist"
            print

        rating = raw_input("Rating (1-10): ")
        rating = rating.strip()

        if rating in ['q', 'quit', 'exit']:
            sys.exit(0)

        if rating == '?':
            show_help = True
            continue

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
