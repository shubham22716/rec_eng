

from neo4j import GraphDatabase

import os
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import string


movie_frame = pd.read_csv('filter_movies.csv')

"""    Utility functions    """
class Movie:
    def __init__(self, id, title, actor, director, overview, poster):
        self.id = id
        self.title = title
        self.actor = truncate(actor)
        self.director = truncate(director, 15)
        self.overview = truncate(overview, 2000)
        self.poster = poster

def set_movie(x):
    return Movie(x.id, x.Title, x.Actors, x.Directors, x.overview, x.Poster)

def truncate(data, n=100):
    data = str(data)
    return (data[:n] + '..') if len(data) > n+2 else data

def compare(smaller, bigger):
    smaller = str(smaller).translate(str.maketrans('', '', string.punctuation+" ")).lower()
    bigger = str(bigger).translate(str.maketrans('', '', string.punctuation+ " ")).lower()
    return smaller in bigger

def search_movies(search_type, search_key):
    print("Got params", search_type, search_key)
    cols = 'Title Actors Directors overview'.split()
    if search_type != 'All':
        mask = movie_frame[search_type].apply(lambda x: compare(search_key, x))
    else:
        mask = False
        for search_type in cols:
            mask = mask | np.array(movie_frame[search_type].apply(lambda x: compare(search_key, x)))
    
    movie_list = movie_frame[mask].apply(set_movie, axis=1)
    return movie_list[:6] if len(movie_list) > 6 else movie_list

"""Insert algorithms here"""
def recommendation_algo_one(key):
    return movie_frame.loc[[4,8,2,7,10,11]].apply(set_movie,axis=1)

def recommendation_algo_two(key):
    return movie_frame.loc[[94,68,62,96,97,99]].apply(set_movie, axis=1)

"""     Views   """
@csrf_exempt
def home(request):
    movie_list = list(movie_frame.head(6).apply(set_movie, axis=1))
    title = "Top 5 movies"
    search_type, search_key = 'All', ''
    if request.method == 'POST':
        search_type = request.POST['search_type']
        search_key = request.POST['search_key']
        if len(search_key) > 0:
            title = 'Search results for {} in category {}'.format(search_key, search_type)
            movie_list = search_movies(search_type, search_key)

    print("Showing {} results".format(len(movie_list)))
    context = {
        'movies':movie_list,
        'title':title,
        'search_key':search_key,
        'search_type':search_type,
        'radios': 'All Title Actors Directors'.split()
    }
    print(context)
    return render(request, 'neo4j/index.html', context)

@csrf_exempt
def detail(request, key):
    context = {
        'movie': set_movie(movie_frame.loc[key]),
        'algo_one': recommendation_algo_one(key),
        'algo_two': recommendation_algo_two(key),
        'search_key':"",
        'search_type': 'All',
        'radios': 'All Title Actors Directors'.split()
    }

    return render(request, 'neo4j/detail.html', context)
