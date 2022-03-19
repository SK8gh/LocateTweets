import pandas as pd

# Path of the csv file containing the requested tweets
path_requested_tweets = "../requested_tweets.csv"

# Words in French
dictionary = pd.read_csv("../french_words.csv", delimiter=";", encoding='latin1')
