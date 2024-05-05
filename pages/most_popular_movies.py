# This script pulls out all identifiable english language movies from DBPedia and sorts them by gross revenue.


import json
import os
from typing import List

import requests
import streamlit

def get_all_dbpedia_movies():
    """Return all identifiable movies along with their titles and gross revenue."""
    # This query will need to be paginated to get everything
    cache_file = "dbpedia_movies.json"
    if os.path.exists(cache_file):
        with open(cache_file) as IN:
            return json.load(IN)
    url = "https://dbpedia.org/sparql"
    all_movies = list()
    done = False
    offset = 0
    while not done:
        streamlit.write(f"Fetching movies ({len(all_movies)} so far)")
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        SELECT ?title ?gross
        WHERE {{
            ?movie a dbo:Film ;
                dbp:gross ?gross ;
                dbp:name ?title .
        }}
        LIMIT 100
        OFFSET {offset}
        """
        response = requests.post(url, data={"query": query})
        response_json = response.json()
        movies = response_json["results"]["bindings"]
        all_movies.extend(movies)
        if len(movies) < 100:
            done = True
        offset += 100
        with open(cache_file, "w") as OUT:
            json.dump(all_movies, OUT, indent=2)
    return all_movies

streamlit.title("Most Popular Movies")
movies = get_all_dbpedia_movies()
# for movie in movies[:5000]:
#     streamlit.write(f"{movie['title']['value']} made {movie['gross']['value']}")

streamlit.write(f"Found {len(movies)} movies.")
streamlit.json(movies[:5000])
