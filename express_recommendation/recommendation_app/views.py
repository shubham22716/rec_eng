import os
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import string
import random
from neo4j import GraphDatabase
from manage import driver
from datetime import date 

today = str(date.today())
print(today)
currdate = '-'.join(today.split('-')[1:])
currmonth = '-'.join(today.split('-')[1:2])

print(currdate)
print(currmonth)
'''
username = 'devendra'
password = '6df126ff'
db = 'movies'
        
uri = []
uri.append("bolt://192.168.1.61:7687")
uri.append("bolt://192.168.1.62:7687")
uri.append("bolt://192.168.1.63:7687")
uri.append("bolt://192.168.1.64:7687")
uri.append("bolt://192.168.1.65:7687")
uri.append("bolt://192.168.1.66:7687")
uri.append("bolt://192.168.1.67:7687")





driver = [] 
count=0

for i in range(len(uri)):
    try:
        driver.append(GraphDatabase.driver(uri[i], auth=(username, password),database=db))
        count = count+1
        print(uri[i]+" is working")
    except:
        print(uri[i]+" is not working")
print(count)     
'''

#movie_frame = pd.read_csv('Modifiedmerged.csv')
#movie_frame = movie_frame.set_index('id_duplicate')
"""    Utility functions    """
class Movie:
    def __init__(self, id, imdb_id, title, actor, director, overview, poster):
        self.id = id
        self.imdb_id = imdb_id
        self.title = title
        self.actor = truncate(actor)
        self.director = truncate(director, 60)
        self.overview = truncate(overview, 2000)
        self.poster = poster

    def as_dict(self):
        return {'id': self.id, 'imdb_id': self.imdb_id, 'title': self.title, 'actor': self.actor, 
            'director': self.director, 'overview': self.overview, 'poster': self.poster}


def set_movie(x):
    return Movie(x.id, x.imdb_id, x.Title, x.Actors, x.Directors, x.overview, x.Poster)

def truncate(data, n=100):
    data = str(data)
    return (data[:n] + '..') if len(data) > n+2 else data

def compare(smaller, bigger):
    smaller = str(smaller).translate(str.maketrans('', '', string.punctuation+" ")).lower()
    bigger = str(bigger).translate(str.maketrans('', '', string.punctuation+ " ")).lower()
    return smaller in bigger

def search_movies(search_type, search_key):
    '''print("Got params", search_type, search_key)
    cols = 'Title Actors Directors overview'.split()
    if search_type != 'All':
        mask = movie_frame[search_type].apply(lambda x: compare(search_key, x))
    else:
        mask = False
        for search_type in cols:
            mask = mask | np.array(movie_frame[search_type].apply(lambda x: compare(search_key, x)))
    
    movie_list = movie_frame[mask].apply(set_movie, axis=1)'''
    if search_type == 'All':
        query = '''match(a)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d)
        where m.title contains "'''+str(search_key)+'''" or m.overview contains "'''+str(search_key)+'''" or a.name contains "'''+str(search_key)+'''" or d.name contains "'''+str(search_key)+'''" 
        or toLower(m.title) contains toLower("'''+str(search_key)+'''") or toLower(m.overview) contains toLower("'''+str(search_key)+'''") or toLower(a.name) contains toLower("'''+str(search_key)+'''") or toLower(d.name) contains toLower("'''+str(search_key)+'''")
        with m, collect(distinct a.name) as actors, collect(distinct d.name) as directors
        WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, m
        RETURN  toString(ID(m)) as id, m.imdb_id as imdb_id, m.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, m.overview as overview, m.Poster as Poster limit 6'''
    
    elif search_type == 'Title':
        query = '''match(a)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d)
        where m.title contains "'''+str(search_key)+'''" or toLower(m.title) contains toLower("'''+str(search_key)+'''") 
        with m, collect(distinct a.name) as actors, collect(distinct d.name) as directors
        WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, m
        RETURN  toString(ID(m)) as id, m.imdb_id as imdb_id, m.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, m.overview as overview, m.Poster as Poster limit 6'''
    
    elif search_type == 'Actors':
        query = '''match(a)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d)
        where a.name contains "'''+str(search_key)+'''" or toLower(a.name) contains toLower("'''+str(search_key)+'''") 
        with m, collect(distinct a.name) as actors, collect(distinct d.name) as directors
        WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, m
        RETURN  toString(ID(m)) as id, m.imdb_id as imdb_id, m.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, m.overview as overview, m.Poster as Poster limit 6'''

    elif search_type == 'Directors':
        query = '''match(a)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d)
        where d.name contains "'''+str(search_key)+'''" or toLower(d.name) contains toLower("'''+str(search_key)+'''") 
        with m, collect(distinct a.name) as actors, collect(distinct d.name) as directors
        WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, m
        RETURN  toString(ID(m)) as id, m.imdb_id as imdb_id, m.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, m.overview as overview, m.Poster as Poster limit 6'''

       
    try:
        movie_frame = pd.DataFrame(driver.session().run(query))
        movie_frame.columns = ['id', 'imdb_id' ,'Title', 'Actors','Directors','overview','Poster']
        movie_list = list(movie_frame.head(6).apply(set_movie, axis=1))
    
        print(movie_list)
        #print(mask)
        return movie_list
        #[:6] if len(movie_list) > 6 else movie_list
    except: 
        return []
"""Insert algorithms here"""
def recommendation_algo_one(key):
    query = '''MATCH (m:Movie) WHERE m.imdb_id = "'''+str(key)+'''"
    MATCH (m)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(rec:Movie)

    WITH m, rec, COUNT(*) AS gs

    OPTIONAL MATCH (m)<-[:HAS_MOVIES]-(pc:productionCompany)-[: HAS_MOVIES ]->(rec)
    WITH m, rec, gs, COUNT(pc) AS PC

    OPTIONAL MATCH (m)<-[: HAS_MOVIES ]-(cn:collectionName)-[: HAS_MOVIES ]->(rec)
    WITH m, rec, gs, COUNT(cn) AS CN, PC
    with rec, (gs)+(3*PC)+(3*CN) AS score
    ORDER BY score DESC 
    match(a)-[:ACTED_IN]->(rec:Movie)<-[:DIRECTED]-(d)
    with rec, collect(distinct a.name) as actors, collect(distinct d.name) as directors
    WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, rec
    RETURN  toString(ID(rec)) as id, rec.imdb_id as imdb_id, rec.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, rec.overview as overview, rec.Poster as Poster limit 6'''
        
    #print(mask)
    
    movie_frame = pd.DataFrame(driver.session().run(query))
    print('8888888888888888888888888888888888888888888888888888888888888888888888888888888888')
    print(len(movie_frame))

    #movie_frame = pd.DataFrame(driver.session().run(query))
    if(len(movie_frame) == 0):
        return('Empty')
    movie_frame.columns = ['id', 'imdb_id' ,'Title', 'Actors','Directors','overview','Poster']
    movie_list = list(movie_frame.head(6).apply(set_movie, axis=1))
    
    return movie_list
    

def recommendation_algo_two(key):
    query = '''MATCH (m:Movie)
    WHERE m.imdb_id = "'''+str(key)+'''"
    WITH m, split(m.AdvancedRecommendations, ' | ') AS wsa
    unwind wsa as w1
    with w1
    match(a)-[:ACTED_IN]->(rec:Movie{title: w1})<-[:DIRECTED]-(d)

    with distinct rec, collect(distinct a.name) as actors, collect(distinct d.name) as directors
    WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, rec
    RETURN  toString(ID(rec)) as id, rec.imdb_id as imdb_id, rec.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, rec.overview as overview, rec.Poster as Poster limit 6'''


    #print(mask)
   
    movie_frame = pd.DataFrame(driver.session().run(query))
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(len(movie_frame))
    
    if(len(movie_frame) == 0):
        return('Empty')
    #movie_frame = pd.DataFrame(driver.session().run(query))
    movie_frame.columns = ['id', 'imdb_id' ,'Title', 'Actors','Directors','overview','Poster']
    movie_list = list(movie_frame.head(6).apply(set_movie, axis=1))
    return movie_list
   

def recommendation_algo_three(key):

    query = '''MATCH (m:Movie)
    WHERE m.imdb_id = "'''+str(key)+'''"
    WITH m, split(m.rec_item, ' | ') AS wsa
  
    unwind wsa[1..] as w1
    with w1
    match(a )-[:ACTED_IN]->(rec:Movie{title: w1})<-[:DIRECTED]-(d )

    with distinct rec, collect(distinct a.name) as actors, collect(distinct d.name) as directors
    WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, rec
    RETURN  toString(ID(rec)) as id, rec.imdb_id as imdb_id, rec.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, rec.overview as overview, rec.Poster as Poster limit 6'''


    #print(mask)
    
    movie_frame = pd.DataFrame(driver.session().run(query))
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(len(movie_frame))
    if(len(movie_frame) == 0):
        return('Empty')
    #movie_frame = pd.DataFrame(driver.session().run(query))
    movie_frame.columns = ['id', 'imdb_id' ,'Title', 'Actors','Directors','overview','Poster']
    movie_list = list(movie_frame.head(6).apply(set_movie, axis=1))
    return movie_list


"""     Views   """
@csrf_exempt
def home(request):
    q = '''match(m:Movie) where m.release_date contains "'''+str(currdate)+'''" return count(m)'''
    n = pd.DataFrame(driver.session().run(q))[0][0]
    print(n)
    if n>0 and n<=6:
        b = 0
    elif n>6:
        a = range(0, n-6)
        b = random.choice(a)
    else:
        c = 1000
        a = range(0, c-6)
        b = random.choice(a)
    query = '''match(m:Movie) where m.release_date contains "'''+str(currdate)+'''" with m skip '''+str(b)+''' limit 6
match(a)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d) with m, collect(distinct a.name) as actors, collect(distinct d.name) as directors
WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, m
RETURN  toString(ID(m)) as id, m.imdb_id as imdb_id, m.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, m.overview as overview, m.Poster as Poster'''
    movie_frame = pd.DataFrame(driver.session().run(query))
    movie_frame.columns = ['id', 'imdb_id' ,'Title', 'Actors','Directors','overview','Poster']
    movie_list = list(movie_frame.head(6).apply(set_movie, axis=1))
    print(movie_list)
    title = "Top 5 movies"
    search_type, search_key = 'All', ''
    if request.method == 'POST':
        search_type = request.POST['search_type']
        search_key = request.POST['search_key']
        if len(search_key) > 0:
            title = 'Search results for {} in category {}'.format(search_key, search_type)
            movie_list = search_movies(search_type, search_key)
            
        context = {
        'movies':movie_list,
        'title':title,
        'search_key':search_key,
        'search_type':search_type,
        'radios': 'All Title Actors Directors'.split()
        }
        return render(request, 'neo4j/search.html', context)
    #print("Showing {} results".format(len(movie_list)))
    context = {
        'movies':movie_list,
        'title':title,
        'search_key':search_key,
        'search_type':search_type,
        'radios': 'All Title Actors Directors'.split()
    }
    #print(context)
    return render(request, 'neo4j/index.html', context)


@csrf_exempt
def detail(request, key):
    query = '''match(m:Movie) where m.imdb_id = "'''+str(key)+'''"
match(a)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d) with m, collect(distinct a.name) as actors, collect(distinct d.name) as directors
WITH REDUCE(mergedString = "",word IN actors | mergedString+word+',') as actorsString, REDUCE(mergedString = "",word IN directors | mergedString+word+',') as directorsString, m
RETURN  toString(ID(m)) as id, m.imdb_id as imdb_id, m.title as Title, LEFT(actorsString,SIZE(actorsString)-1) as Actors, LEFT(directorsString,SIZE(directorsString)-1) as Directors, m.overview as overview, m.Poster as Poster'''
    movie_frame = pd.DataFrame(driver.session().run(query))
    movie_frame.columns = ['id', 'imdb_id' ,'Title', 'Actors','Directors','overview','Poster']
    print("#########################################################################")
    print(len(movie_frame))
    print(movie_frame)
    movie_frame.index = [0]
    
    
    
    context = {
        'movie': set_movie(movie_frame.loc[0]),
        'algo_one': recommendation_algo_one(key),
        'algo_two': recommendation_algo_two(key),
        'algo_three': recommendation_algo_three(key),
        'search_key':"",
        'search_type': 'All',
        'radios': 'All Title Actors Directors'.split()
        
    }
    
    context['PAGE_NAME'] = context['movie'].title
    
    if context['algo_one']=='Empty' and context['algo_two']!='Empty' and context['algo_three']!='Empty':
        return render(request, 'neo4j/genreerror.html', context)
    
    if context['algo_two']=='Empty' and context['algo_one']!='Empty' and context['algo_three']!='Empty':
        return render(request, 'neo4j/nlperror.html', context)
    
    if context['algo_three']=='Empty' and context['algo_one']!='Empty' and context['algo_two']!='Empty':
        return render(request, 'neo4j/itemerror.html', context)
        
    if context['algo_one']=='Empty' and context['algo_two']=='Empty' and context['algo_three']!='Empty':
        return render(request, 'neo4j/genrenlperror.html', context)
        
    if context['algo_one']=='Empty' and context['algo_two']!='Empty' and context['algo_three']=='Empty':
        return render(request, 'neo4j/genreitemerror.html', context)
        
    if context['algo_one']!='Empty' and context['algo_two']=='Empty' and context['algo_three']=='Empty':
        return render(request, 'neo4j/nlpitemerror.html', context)
    
    if context['algo_one'] == 'Empty' and context['algo_two']=='Empty' and context['algo_three']=='Empty':
        return render(request, 'neo4j/all.html', context)
        
    return render(request, 'neo4j/detail.html', context)