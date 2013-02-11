import json
from functools import partial
import string
import numpy as np
import matplotlib.pyplot as plt
from clean import p1, p2, mlx, mly, mrx, mry, lx, ly, rx, ry
from pyproj import transform as transform_proj

transform = partial(transform_proj, p2, p1)


if __name__ == '__main__':
    lines = map(string.strip, open('data/geo_test_tweets.json').readlines())
    tweets = filter(lambda x: 'geo_normalized' in x.keys(), map(json.loads, lines))

    x = np.ndarray(len(tweets))
    y = np.ndarray(len(tweets))
    for idx, tweet in enumerate(tweets):
        x[idx] = tweet['geo_normalized']['x']
        y[idx] = tweet['geo_normalized']['y']

    histogram, xedges, yedges = np.histogram2d(x, y, bins=50)
    max_x, max_y = np.unravel_index(histogram.argmax(), histogram.shape)
    max_x_utm = (max_x / (histogram.shape[0] + 0.5)) * (mrx - mlx) + mlx
    max_y_utm = (max_y / (histogram.shape[0] + 0.5)) * (mry - mly) + mly
    max_lng, max_lat= transform(max_x_utm, max_y_utm)

    import ipdb; ipdb.set_trace() ### XXX BREAKPOINT
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    plt.clf()
    plt.imshow(histogram, origin='lower', extent=extent)
    plt.colorbar()
    plt.show()
    # plt.imsave('heatmap.png', heatmap)
