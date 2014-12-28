##########################################################################
#                                                                        #
#     Extract the graph of wikipedia articles related to Statistics      #
#                          using the MediaWiki API                       #
#                                                                        #
##########################################################################
#
# By Framartin - Under MIT License
#
# Freely inspired by the great brianckeegan's Wikipedia-Network-Analysis python notebook available on github under MIT license at : https://github.com/brianckeegan/Wikipedia-Network-Analysis 

# We use Python 2 because wikitools isn't compatible with Python3

# Please see Requirements in the README.md file

import numpy as np

# pandas handles tabular data
import pandas as pd
import csv

# networkx handles network data
import networkx as nx

# json handles reading and writing JSON data
import json

# To visualize webpages within this webpage
from IPython.display import HTML

# To run queries against MediaWiki APIs
from wikitools import wiki, api

# Some other helper functions
from collections import Counter
from operator import itemgetter

# to delay queries
from time import sleep

##########################
#        Fonctions       #
##########################

def wikipedia_query(query_params,site_url='http://en.wikipedia.org/w/api.php'):
    site = wiki.Wiki(url=site_url)
    request = api.APIRequest(site, query_params)
    result = request.query()
    return result[query_params['action']]


# extract subcategories of a category
def get_subcategory_category(category): 
    # options on http://www.mediawiki.org/wiki/API%3aCategorymembers
    query = {'action': 'query',
             'list': 'categorymembers',
             'cmtype': 'subcat', # only subcat
             'cmtitle': category, # must include Category: prefix
             'cmlimit': '500',
             'cmprop': 'title'}
    results = wikipedia_query(query) # do the query
    
    if not len(results['categorymembers'])==0:
        outlist = [subcat['title'] for subcat in results['categorymembers']] # clean up outlinks
    else:
        outlist = [] # return empty list if no outlinks
    
    return outlist

# test the function
#bc_out = get_subcategory_category("Category:Statistics")
#print "There are {0} subcats".format(len(bc_out))

# extract pages of a (sub)category
def get_pages_category(category):
    # options on http://www.mediawiki.org/wiki/API%3aCategorymembers
    query = {'action': 'query',
             'list': 'categorymembers',
             'cmtype': 'page', # only pages
             'cmtitle': category, # must include Category: prefix
             'cmlimit': '500',
             'cmnamespace': '0',
             'cmprop': 'title'}
    results = wikipedia_query(query) # do the query
    
    if not len(results['categorymembers'])==0:
        outlist = [subcat['title'] for subcat in results['categorymembers']] # clean up outlinks
    else:
        outlist = [] # return empty list if no outlinks
    
    return outlist

# test the function
#bc_out = get_pages_category("Category:Statistics")
#print "There are {0} subcat".format(len(bc_out))


# extract out links from a wikipedia page

# query example : https://en.wikipedia.org/w/api.php?action=query&generator=links&titles=Factor%20analysis%20of%20mixed%20data&prop=titles&redirects
# generator : generate links from a specific page and then extract titles 
# Note : the 'redirects' option doesn't work with prop='links' : it redirects the principal page, not out links  

def get_page_links(page):
    query = {'action': 'query',
             'generator': 'links',
             'redirects': 'True',
             'prop': 'titles',
             'titles': page,
             'pllimit': '500',
             'plnamespace': '0'}
    results = wikipedia_query(query) # do the query
    
    if len(results['pages'].keys())>0: #sometimes there are no links
        outlist = [results['pages'][link_id]['title'] for link_id in results['pages'].keys()] # clean up outlinks
    else:
        outlist = [] # return empty list if no outlinks
    
    return outlist


###############################################
#        Extract pages about Statistics       #
###############################################

# explorer jusquà une profondeur de 3 par exemple

#subcats = get_subcategory_category("Category:Statistics")
#subcats2 = pd.DataFrame()
#for subcat in subcats :
#    temp = get_subcategory_category(subcat)
#    temp = pd.DataFrame(temp)
#    subcats2 = pd.concat([temp, subcats2], ignore_index=True)
#    sleep(0.5)

# extraire les sous-catégories de "Category:Statistics"
# 1er niveau
subcats = get_subcategory_category("Category:Statistics") 
# 2eme niveau
subcats2 = []
for subcat in subcats :
    temp = get_subcategory_category(subcat)
    subcats2 = subcats2+temp
    sleep(0.5)

# 3eme niveau
subcats3 = []
for subcat in subcats2 :
    temp = get_subcategory_category(subcat)
    subcats3 = subcats3+temp
    sleep(0.5)

# combiner de manière unique
categories = subcats + subcats2 + subcats3
categories_unique = list(set(categories))
len(categories)
len(categories_unique)

## TODO : ou se limiter à deux étapes
categories = subcats + subcats2
categories_unique = list(set(categories))
len(categories_unique)

# enregistrer
df = pd.DataFrame(categories_unique)
df.to_csv('categories_unique.csv',quotechar='"',index=False, encoding='utf-8')

# extraire les pages des sous-catégories extraites
articles1 = get_pages_category("Category:Statistics")
articles2 = []
for subcat in categories_unique :
    temp = get_pages_category(subcat)
    articles2 = articles2+temp
    sleep(0.5)
# et celles de cette liste (ajoute 100 pages pertinentes)
# generate alls links in namespace 0 of these articles
# articles mis en valeurs par le portail Statistics : https://en.wikipedia.org/wiki/Portal:Statistics
articles3 = get_page_links("List_of_statistics_articles|Outline_of_statistics")
articles3 = articles3 + ["List of statistics articles","Outline of statistics"]
# TODO : inclure : https://en.wikipedia.org/wiki/List_of_statisticians ??

# concaténation et unicité des pages extraites
pages = articles1 + articles2 + articles3
pages_unique = list(set(pages))
len(pages)
len(pages_unique)

# enregistrement
df = pd.DataFrame(pages_unique)
df.to_csv('pages_unique.csv',quotechar='"',index=False, encoding='utf-8')

# TO DO : exclure "List of" ?
r = re.compile(r'List of')
pages_list_of = filter(r.match, pages_unique)
# ou se limiter qu'à deux sous-catégories

###### TODO : pour les tests on se réduit à articles3
pages = articles3
pages_unique = list(set(pages))

del pages_unique[pages_unique.index('Cumulative frequency analysis')] # we remove deleted pages which generates errors

pages_links = {}
for page in pages_unique:
    links = get_page_links(page)
    links_sel = [] # we keep only links in the pages selection
    for link in links:
        if link in pages_unique:
            links_sel.append(link)
    pages_links[page] = links_sel
    sleep(0.5)


# TODO : BUG : on résupère les liens vers les pages de redirection, qui ne sont donc pas dans pages_uniques. Ex : "Principal components analysis" dans get_page_links("Factor analysis of mixed data")

# sauvegarde
with open('statistics_links_data.json','wb') as f:
    json.dump(pages_links,f)

edges = []
for orig in pages_links.keys():
    for dest in pages_links[orig]:
        edges = edges + [{ "from":orig, "to":dest }]

df = pd.DataFrame(edges)
df.to_csv('edges.csv',quoting = csv.QUOTE_NONNUMERIC, quotechar='"',index=False, encoding='utf-8')


# en cas de besoin

#f = open('statistics_links_data.json') 
#data = json.load(f) 
#f.close()

# nettoyage du précédant articles3
#edges = []
#for orig in pages_links.keys():
#    for dest in pages_links[orig]:
#        if dest in pages_links.keys():
#            edges = edges + [{ "from":orig, "to":dest }]
#
#df = pd.DataFrame(edges)
#df.to_csv('edges.csv',quoting = csv.QUOTE_NONNUMERIC, quotechar='"',index=False, encoding='utf-8')


# Make a network using NetworkX library

hrc_g = nx.DiGraph() # directed graph

for orig in pages_links.keys():
    for dest in pages_links[orig]:
        hrc_g.add_edge(orig,dest)

hrc_g.number_of_edges()
hrc_g.number_of_nodes()

reciprocal_edges = list()
for (i,j) in hrc_g.edges():
    if hrc_g.has_edge(j,i) and (j,i) not in reciprocal_edges:
        reciprocal_edges.append((i,j))

reciprocation_fraction = round(float(len(reciprocal_edges))/hrc_g.number_of_edges(),3)
print "There are {0} reciprocated edges out of {1} edges in the network, giving a reciprocation fraction of {2}.".format(len(reciprocal_edges),hrc_g.number_of_edges(),reciprocation_fraction)
# There are 41021 reciprocated edges out of 151917 edges in the network, giving a reciprocation fraction of 0.27.

import matplotlib.pyplot as plt

nx.draw(hrc_g)
plt.savefig("path.png")
nx.draw_networkx(hrc_g, node_size = 80, alpha=0.5, linewidths=0.2, width=0.2, font_size=5)
plt.savefig("path_ok.png")
nx.draw_random(hrc_g)
plt.savefig("path_random.png")
nx.draw_circular(hrc_g)
plt.savefig("path_circular.png")
nx.draw_spectral(hrc_g)
plt.savefig("path_spectral.png")

