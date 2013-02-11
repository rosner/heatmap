import os
from collections import Counter
import re
import codecs
import sys
from traceback import print_exc
import json
import requests
from requests_oauthlib import OAuth1

locations = {
    'berlin': '13.0882097323,52.3418234221,13.7606105539,52.6697240587',
    'sf': '-122.75,36.8,-121.75,37.8',
    'ny': '-74,40,-73,41'
}

counter = Counter()


def write_tweet(line, output_file):
    try:
        tweet = json.loads(re.sub(r'\s+', ' ', line, flags=re.UNICODE))
        # retweeted tweets don't contain coordinates, according to the API doc
        # print u'"RT: {0}" {1} - {2}'.format(tweet['retweeted'],
        #                                 tweet['coordinates'],
        #                                 tweet['text'])
        output_file.write(json.dumps(tweet))
        output_file.write('\n')
        output_file.flush()
        counter.update(tweet=1)
        if counter.get('tweet') % 10 == 0:
            print '+ %s tweets' % counter.get('tweet')
    except ValueError:
        print '----> "%s"' % line
        print_exc()

client_key = os.environ['TWITTER_CONSUMER_KEY']
client_secret = os.environ['TWITTER_CONSUMER_SECRET']
resource_owner_key = os.environ['APP_ACCESS_TOKEN']
resource_owner_secret = os.environ['APP_ACCESS_SECRET']

oauth = OAuth1(client_key,
               client_secret=client_secret,
               resource_owner_key=resource_owner_key,
               resource_owner_secret=resource_owner_secret)

twitter = requests.Session()
twitter.auth = oauth


if __name__ == '__main__':
    locations = ','.join((locations[key] for key in sys.argv[1:]))
    data = {
        'locations': locations
    }

    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    response = twitter.post(url, data=data, stream=True)

    try:
        response.raise_for_status()
    except requests.HTTPError:
        import ipdb; ipdb.set_trace() ### XXX BREAKPOINT
    else:
        print 'Connection aquired... waiting for tweets'

        output_file_name = 'data/%s' % sys.argv[1]
        with codecs.open(output_file_name, 'aw', 'utf-8') as output_file:
            try:
                for line in response.iter_lines(chunk_size=56):
                    cleaned_line = line.strip()
                    if cleaned_line:
                        write_tweet(cleaned_line, output_file)
            except KeyboardInterrupt:
                sys.exit()
