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

# to quote csv output
import csv

# networkx handles network data
import networkx as nx

# json handles reading and writing JSON data
import json

# To run queries against MediaWiki APIs
from wikitools import wiki, api

# to delay queries
from time import sleep

# to select pages
import re

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
# query example : https://en.wikipedia.org/w/api.php?action=query&generator=links&titles=Least_squares&prop=titles&redirects&gpllimit=500&gplnamespace=0
# generator : generate links from a specific page and then extract titles 
# Note : the 'redirects' option doesn't work with prop='links' : it redirects the principal page, not out links  
# With the wrong options we get titles of redirection pages, which is problematic because these titles are not in our selection of Statistics articles. Ex : "Principal components analysis" in get_page_links("Factor analysis of mixed data")

def get_page_links(page):
    query = {'action': 'query',
             'generator': 'links',
             'redirects': 'True',
             'prop': 'titles',
             'titles': page,
             'gpllimit': '500',
             'gplnamespace': '0'}
    results = wikipedia_query(query) # do the query
    
    if len(results['pages'].keys())>0: #sometimes there are no links
        outlist = [results['pages'][link_id]['title'] for link_id in results['pages'].keys()] # clean up outlinks
    else:
        outlist = [] # return empty list if no outlinks
    
    return outlist


###############################################
#        Extract pages about Statistics       #
###############################################

# 2 solutions founds : explore Category:Statistics or extract articles from "List of" articles

# 1) First solution 
# we explore the Category:Statistics in 3-steps

#subcats = get_subcategory_category("Category:Statistics")
#subcats2 = pd.DataFrame()
#for subcat in subcats :
#    temp = get_subcategory_category(subcat)
#    temp = pd.DataFrame(temp)
#    subcats2 = pd.concat([temp, subcats2], ignore_index=True)
#    sleep(0.5)

# we save the root category of each subcat in subcat_category
subcat_category = {}

# extract subcategories of "Category:Statistics"
# 1st step
subcats = get_subcategory_category("Category:Statistics") 

# 2nd step
subcats2 = []
for subcat in subcats :
    temp = get_subcategory_category(subcat)
    subcats2 = subcats2+temp 
    sleep(0.5)
    for subcat2 in temp:
        subcat_category[subcat2] = subcat # the subcategory is associated with the 1st step category 

# 3th step
subcats3 = []
for subcat in subcats2 :
    temp = get_subcategory_category(subcat)
    subcats3 = subcats3+temp
    sleep(0.5)
    for subcat3 in temp:
        if not subcat3 in subcat_category.keys():
            subcat_category[subcat3] = subcat_category[subcat] # the sub-subcategory is associated with the 1st step category of the subcategory 

# Root categories return them-self
for subcat in subcats :
    subcat_category[subcat] = subcat


# merge and keep unique
categories = subcats + subcats2 + subcats3
categories_unique = list(set(categories))
len(categories)
len(categories_unique)

## TODO : we can take only 2 steps
#categories = subcats + subcats2
#categories_unique = list(set(categories))
#len(categories_unique)

# save
df = pd.DataFrame(categories_unique)
df.to_csv('categories_unique.csv', quoting = csv.QUOTE_NONNUMERIC, quotechar='"',index=False, encoding='utf-8')


# root category of pages
pages_category = {}

# extract pages of subcategories
articles1 = get_pages_category("Category:Statistics")
for page in articles1: # save root category of pages
    pages_category[page] = "Category:Statistics"

articles2 = []
for subcat in categories_unique :
    temp = get_pages_category(subcat)
    articles2 = articles2+temp
    sleep(0.5)
    for page in temp:
        if not page in pages_category.keys():
            pages_category[page] = subcat_category[subcat]

# save
with open('pages_category.json','wb') as f:
    json.dump(pages_category,f)

# 2) Second solution 
# we extract pages related to statistics using these pages (featured in the Statistics portal : https://en.wikipedia.org/wiki/Portal:Statistics ) :
# - List_of_statistics_articles
# - Outline_of_statistics
# - https://en.wikipedia.org/wiki/List_of_statisticians (not yet) TODO : include this ?

# this solution adds 100 more pages to the first one 

# generate alls links in namespace 0 of these articles
articles3 = get_page_links("List_of_statistics_articles|Outline_of_statistics")


# 3) choose the solution

#     - First one only :
pages = articles1 + articles2
pages_unique = list(set(pages))
len(pages_unique)

#     - Second one only :
pages = articles3
pages_unique = list(set(pages))
len(pages_unique)

#     - Both :
pages = articles1 + articles2 + articles3
pages_unique = list(set(pages))
len(pages)
len(pages_unique)



# we exlude the 2 pages used for the generation (to not lead to a biais) 
del pages_unique[pages_unique.index('List of statistics articles')] 
del pages_unique[pages_unique.index('Outline of statistics')] 

# we exlude page begining by "List of"
r = re.compile(r'List of')
pages_list_of = filter(r.match, pages_unique)
for page_del in pages_list_of:
    del pages_unique[pages_unique.index(page_del)] 


# save
df = pd.DataFrame(pages_unique)
df.to_csv('pages_unique.csv',quoting = csv.QUOTE_NONNUMERIC,quotechar='"',index=False, encoding='utf-8')


##################################
#        Extract out links       #
##################################


# TODO : delete links of templates from https://en.wikipedia.org/w/api.php?action=query&generator=links&titles=Template:Least_squares_and_regression_analysis&prop=titles&redirects&gpllimit=500&gplnamespace=0 
# get templates of a page : 
error_pages = []
pages_links = {}
for page in pages_unique:
    try :
        links = get_page_links(page)
        links_sel = [] # we keep only links in the pages selection (pages_unique)
        for link in links:
            if link in pages_unique:
                links_sel.append(link)
        pages_links[page] = links_sel # key = page 'from', value = page 'to'
#        sleep(0.5)
    except : # error if the page is deleted for example
        error_pages = error_pages + [page]

# save dict in JSON
with open('statistics_links_data.json','wb') as f:
    json.dump(pages_links,f)

# save edges in CSV (one line = one link)
edges = []
for orig in pages_links.keys():
    for dest in pages_links[orig]:
        if dest in pages_links.keys() & dest!=orig: # we make sure that links are in our pages selection and that we have not loop-link (self-link) which can append due to templates
            edges = edges + [{ "from":orig, "to":dest }]

df = pd.DataFrame(edges)
df.to_csv('edges.csv',quoting = csv.QUOTE_NONNUMERIC, quotechar='"',index=False, encoding='utf-8')


# for the first solution we save the category of vertices :
vertex = []
for orig in pages_links.keys():
    vertex = vertex + [{ "name":orig, "category": pages_category[orig] }]


###############################
#        Auxiliary code       #
###############################


# load JSON if needed

#f = open('statistics_links_data.json') 
#data = json.load(f) 
#f.close()


#df = pd.DataFrame(edges)
#df.to_csv('edges.csv',quoting = csv.QUOTE_NONNUMERIC, quotechar='"',index=False, encoding='utf-8')



# Make a network using NetworkX library

graph = nx.DiGraph() # directed graph

for orig in pages_links.keys():
    for dest in pages_links[orig]:
        graph.add_edge(orig,dest)

graph.number_of_edges()
graph.number_of_nodes()

reciprocal_edges = list()
for (i,j) in graph.edges():
    if graph.has_edge(j,i) and (j,i) not in reciprocal_edges:
        reciprocal_edges.append((i,j))

reciprocation_fraction = round(float(len(reciprocal_edges))/graph.number_of_edges(),3)
print "There are {0} reciprocated edges out of {1} edges in the network, giving a reciprocation fraction of {2}.".format(len(reciprocal_edges),graph.number_of_edges(),reciprocation_fraction)
# There are 41021 reciprocated edges out of 151917 edges in the network, giving a reciprocation fraction of 0.27.

import matplotlib.pyplot as plt

nx.draw(graph)
plt.savefig("path.png")
nx.draw_networkx(graph, node_size = 80, alpha=0.5, linewidths=0.2, width=0.2, font_size=5)
plt.savefig("path_ok.png")
nx.draw_random(graph)
plt.savefig("path_random.png")
nx.draw_circular(graph)
plt.savefig("path_circular.png")
nx.draw_spectral(graph)
plt.savefig("path_spectral.png")

