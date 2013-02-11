import codecs
import re
import json
import string

if __name__ == '__main__':
    tweets = map(json.loads, map(string.strip, codecs.open('data/geo_tweets.json', 'r', 'utf-8').readlines()))
    sources = [tweet['source'] for tweet in tweets]
    with codecs.open('data/sources.txt', 'w', 'utf-8') as sources_output:
        for source in sources:
            sources_output.write(source)
            sources_output.write('\n')
