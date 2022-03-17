import pandas as pd
import snscrape.modules.twitter as st
import itertools
import numpy as np
import time
from tqdm import tqdm
import configuration as config
import threading
import matplotlib.pyplot as plt
import json


class GetTweets:
    def __init__(self):
        self._request_number = 2000
        self._words = config.dictionary
        self._loc = '48.8565, 2.3524, 0.1km'
        self._df_columns = ["date", "content", "retweetCount", "coordinates"]

        self.requested_tweets = pd.DataFrame(columns=self._df_columns)

    def _thread_request(self, word):
        time.sleep(0.1)
        df_coord = pd.DataFrame(itertools.islice(st.TwitterSearchScraper(
            '{} geocode:"{}"'.format(word, self._loc)).get_items(), self._request_number))

        if not df_coord.empty:
            df_coord = df_coord[self._df_columns]
            df_coord = df_coord[df_coord['coordinates'].notna()]
            self.requested_tweets = self.requested_tweets.append(df_coord)

    def run_threads(self):
        threads = []
        for i in range(len(self._words)):
            word = self._words[i+1]
            t = threading.Thread(target=self._thread_request, args=[word], daemon=True)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.requested_tweets.to_csv(config.path_requested_tweets)


class Mapping:
    def __init__(self):
        self.dots = pd.read_csv(config.path_requested_tweets)

    def _treat_dots(self):
        pass

    def plot_dots(self):
        dots = self.dots[["retweetCount", "coordinates"]].dropna()
        fig, ax = plt.subplots()

        for k, df_line in enumerate(dots.itertuples()):
            rt_count, coordinates = int(np.around(df_line.retweetCount)), df_line.coordinates

            coordinates = coordinates.replace("\'", "\"")
            coordinates = json.loads(coordinates)

            longitude, latitude = coordinates.values()

            plt.scatter(longitude, latitude, color='purple')

            if k > 1000:
                break

        plt.show()

        #for i in range(len_values):
            #    ax.scatter(x[i], y[i], color='purple')

Mapping().plot_dots()
