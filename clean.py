import codecs
from functools import partial

import json
import string

from pyproj import Proj, transform as transform_proj
from streaming import locations

p1 = Proj(proj='latlong')
p2 = Proj(proj='utm')
transform = partial(transform_proj, p1, p2)

lx, ly, rx, ry = map(float, locations['berlin'].split(','))
mlx, mly = transform(lx, ly)
mrx, mry = transform(rx, ry)


def normalize(tweet_geo):
    geo_y, geo_x = tweet_geo['coordinates']
    tweet_x, tweet_y = transform(geo_x, geo_y)
    norm_tweet_x = (tweet_x - mlx) / (mrx - mlx)
    norm_tweet_y = (tweet_y - mly) / (mry - mly)
    return (norm_tweet_x, norm_tweet_y)


def is_geolocated_tweet(tweet):
    return tweet['geo'] is not None and tweet['geo']['type'] == 'Point'


def is_in_bounding_box(tweet_geo):
    norm_x, norm_y = normalize(tweet_geo)
    in_bounding_box = (
            norm_x <= 1. and
            norm_x >= 0. and
            norm_y <= 1. and
            norm_y >= 0.)
    return (in_bounding_box, norm_x, norm_y)


def attach_normalized_coordinates(tweet):
    """
    Check if tweet is in bounding box of Berlin.
    Tweet lat/lng gets transformed to mercator and then normalized to 0.0, 1.1
    """
    geo = tweet['geo']
    in_bounding_box, norm_x, norm_y = is_in_bounding_box(geo)
    if in_bounding_box:
        print '+ %s' % geo
        tweet['geo_normalized'] = {'x': norm_x, 'y': norm_y}
    else:
        print '- %s' % geo

    return tweet


def filter_for_bounding_box(tweet):
    if is_geolocated_tweet(tweet):
        processed_tweet = attach_normalized_coordinates(tweet)
        return processed_tweet
    return ''


if __name__ == '__main__':
    tweets = map(json.loads,
            map(string.strip, open('data/berlin.json').readlines()))

    filtered_tweets = filter(len, map(filter_for_bounding_box, tweets))

    geolocated_tweets = map(json.dumps, filtered_tweets)
    with codecs.open('data/geo_tweets.json', 'wa', 'utf-8') as output_file:
        for tweet in geolocated_tweets:
            output_file.write(tweet)
            output_file.write('\n')
