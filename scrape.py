import pandas as pd
import snscrape.modules.twitter as st
import itertools
import numpy as np
import time
import configuration as config
import threading
import matplotlib.pyplot as plt
import json


class GetTweets:
    def __init__(self):
        self._request_number = 2000
        self._words = config.dictionary["language:"].iloc[2:].dropna()
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
            word = self._words.iloc[i]
            t = threading.Thread(target=self._thread_request, args=[word], daemon=True)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.requested_tweets.to_csv(config.path_requested_tweets)


class Mapping:
    def __init__(self):
        self.dots = pd.read_csv(config.path_requested_tweets)[["retweetCount", "coordinates"]]
        self.dots_dis = pd.DataFrame()

    def _treat_dots(self):
        """
        Changing the distribution of dots (retweet count)
        """
        # Getting the number of tweets with 0 retweets
        dots_no_rt = self.dots[self.dots["retweetCount"] == 0]
        keep_dots_no_rt = dots_no_rt.iloc[:int(0.04 * len(dots_no_rt))]

        self.dots_dis = self.dots_dis.append(keep_dots_no_rt)
        self.dots_dis = self.dots_dis.append(self.dots[self.dots["retweetCount"] > 0])
        self.dots_dis = self.dots_dis.drop_duplicates()

        del self.dots
        return self

    def plot_dots(self):
        fig, ax = plt.subplots()

        print(f"number of dots : {len(self.dots_dis)}")

        for k, df_line in enumerate(self.dots_dis.itertuples()):
            rt_count, coordinates = int(np.around(df_line.retweetCount)), df_line.coordinates

            coordinates = coordinates.replace("\'", "\"")
            coordinates = json.loads(coordinates)

            longitude, latitude = coordinates.values()
            if (rt_count / 15) > 1:
                plt.scatter(longitude, latitude, c='red')
                continue

            plt.scatter(longitude, latitude, c=str(rt_count / 255.))

        plt.show()


Mapping()._treat_dots().plot_dots()
