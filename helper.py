from datetime import date,  datetime, timedelta
import pandas as pd


def filter_movies_by_genre(df,genres):
    dff = df[df['genres'].str.contains(r'\b(?:{})\b'.format('|'.join(genres)))]
    return dff 


def filter_movies_by_ratings(df, ratings):
    dff = df[df['MPAA'].isin(ratings)]
    return dff