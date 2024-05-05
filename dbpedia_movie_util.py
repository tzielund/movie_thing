# Fetch movie data using dbpedia sparql query

import requests
import json
import os

import streamlit

dbpedia_cache = "dbpedia_cache"
os.makedirs(dbpedia_cache, exist_ok=True)

def search_for_movies_by_title(title):
    title = title.lower()
    """Search for movies by title using a dbpedia sparql query and full text search."""
    """Return a list of tuples containing the movie uri and title."""
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?movie, ?title
    WHERE {{
        ?movie a dbo:Film ;
            rdfs:label ?title .
        FILTER (lang(?title) = 'en')
        FILTER (contains(lcase(?title), "{title}"))
    }}
    """
    url = "http://dbpedia.org/sparql"
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    movie_data = response.json()
    movies = list()
    for movie in movie_data["results"]["bindings"]:
        movies.append((movie["movie"]["value"], movie["title"]["value"]))
    return movies

def get_movie_data(movie_uri, movie_title, ignore_cache=False):
    """Get movie data from dbpedia using a sparql query."""
    print("Looking up movie data for", movie_uri)
    # Make a filename-safe version of the movie uri
    # take off the http://dbpedia.org/resource/ part
    filename_safe_movie_id = movie_uri.replace("http://dbpedia.org/resource/", "")
    filename_safe_movie_uri = filename_safe_movie_id.replace("/", "_")
    cache_file = f"{dbpedia_cache}/{filename_safe_movie_uri}.json"
    if not ignore_cache and os.path.exists(cache_file):
        # streamlit.write("Fetching movie data from cache")
        with open(cache_file) as IN:
            structure = json.load(IN)
            # Check that structure contains all of the required keys: directors, actors, writers, release_date and gross_revenue
            if "directors" in structure and "actors" in structure and "writers" in structure:
                if "release_date" in structure and "gross_revenue" in structure:
                    return structure
            # Otherwise continue to fetch the data from dbpedia
    # streamlit.write("Fetching movie data from dbpedia")
    movie_struct = dict()
    movie_struct["uri"] = movie_uri
    movie_struct["title"] = movie_title
    url = "http://dbpedia.org/sparql"

    # This query gets the directors
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?director
    WHERE {{
        <{movie_uri}> dbo:director ?director .
    }}
    """
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    director_data = response.json()
    # streamlit.write("Directors query results")
    # streamlit.json(json.dumps(director_data, indent=2))
    directors = list()
    for director in director_data["results"]["bindings"]:
        directors.append(director["director"]["value"])
    movie_struct["directors"] = directors

    # Next query gets the writers
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?writer
    WHERE {{
        <{movie_uri}> dbo:writer ?writer .
    }}
    """
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    writer_data = response.json()
    # streamlit.write("Writers query results")
    # streamlit.json(json.dumps(writer_data, indent=2))
    writers = list()
    for writer in writer_data["results"]["bindings"]:
        writers.append(writer["writer"]["value"])
    movie_struct["writers"] = writers

    # Next query gets the actors
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?actor
    WHERE {{
        <{movie_uri}> dbo:starring ?actor .
    }}
    """
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    actor_data = response.json()
    # streamlit.write("Actors query results")
    # streamlit.json(json.dumps(actor_data, indent=2))
    actors = list()
    for actor in actor_data["results"]["bindings"]:
        actors.append(actor["actor"]["value"])
    movie_struct["actors"] = actors

    # Next gets the release date and gross revenue
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    select ?release_date ?gross
    where {{
        <{movie_uri}> dbp:released ?release_date .
        <{movie_uri}> dbp:gross ?gross .
    }}
    """
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    revenue_data = response.json()
    # streamlit.write("Revenue query results")
    # streamlit.json(json.dumps(revenue_data, indent=2))
    # Safely attempt to set release_date and gross_revenue
    bindings = revenue_data["results"]["bindings"]
    if len(bindings) == 0:
        movie_struct["release_date"] = "Unknown"
        movie_struct["gross_revenue"] = "Unknown"
    else:
        movie_struct["release_date"] = bindings[0]["release_date"]["value"]
        movie_struct["gross_revenue"] = bindings[0]["gross"]["value"]

    # Check for an override file in cache
    override_file = f"{dbpedia_cache}/overrides/{filename_safe_movie_uri}.json"
    if os.path.exists(override_file):
        with open(override_file) as IN:
            overrides = json.load(IN)
            for key in overrides:
                movie_struct[key] = overrides[key]

    with open(cache_file, "w") as OUT:
        OUT.write(json.dumps(movie_struct, indent=2))
    return movie_struct

def update_movie_data(movie_uri, new_data):
    """Replace movie data in the cache with new data."""
    filename_safe_movie_id = movie_uri.replace("http://dbpedia.org/resource/", "")
    filename_safe_movie_uri = filename_safe_movie_id.replace("/", "_")
    cache_file = f"{dbpedia_cache}/{filename_safe_movie_uri}.json"
    with open(cache_file, "w") as OUT:
        OUT.write(json.dumps(new_data, indent=2))

def get_person_thumbnail(person_uri):
    """Get the thumbnail image for a person."""
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?thumbnail
    WHERE {{
        <{person_uri}> dbo:thumbnail ?thumbnail .
    }}
    """
    url = "http://dbpedia.org/sparql"
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    thumbnail_data = response.json()
    if len(thumbnail_data["results"]["bindings"]) == 0:
        return None
    return thumbnail_data["results"]["bindings"][0]["thumbnail"]["value"]

def find_actor_by_uri(dbpedia_uri):
    """Find an actor by their dbpedia uri."""
    result = dict()
    # First query verifies the given uri and gets the label (name)
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?actor, ?label
    WHERE {{
        <{dbpedia_uri}> rdfs:label ?label .
        FILTER (lang(?label) = 'en')
    }}
    """
    url = "http://dbpedia.org/sparql"
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    actor_data_with_bindings = response.json()
    result["uri"] = dbpedia_uri
    result["label"] = actor_data_with_bindings["results"]["bindings"][0]["label"]["value"]
    # Second query gets movies they are in
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?movie
    WHERE {{
        ?movie dbo:starring <{dbpedia_uri}> .
    }}
    """
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    movie_data_with_bindings = response.json()
    movies = list()
    for movie in movie_data_with_bindings["results"]["bindings"]:
        movies.append(movie["movie"]["value"])
    result["movies"] = movies
    return result

def find_director_by_uri(dbpedia_uri):
    """Find a director by their dbpedia uri."""
    result = dict()
    # First query verifies the given uri and gets the label (name)
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?director, ?label
    WHERE {{
        <{dbpedia_uri}> rdfs:label ?label .
        FILTER (lang(?label) = 'en')
    }}
    """
    url = "http://dbpedia.org/sparql"
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    director_data_with_bindings = response.json()
    result["uri"] = dbpedia_uri
    result["label"] = director_data_with_bindings["results"]["bindings"][0]["label"]["value"]
    # Second query gets movies they directed
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?movie
    WHERE {{
        ?movie dbo:director <{dbpedia_uri}> .
    }}
    """
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    movie_data_with_bindings = response.json()
    movies = list()
    for movie in movie_data_with_bindings["results"]["bindings"]:
        movies.append(movie["movie"]["value"])
    result["movies"] = movies
    return result

def find_writer_by_uri(dbpedia_uri):
    """Find a writer by their dbpedia uri."""
    result = dict()
    # First query verifies the given uri and gets the label (name)
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?writer, ?label
    WHERE {{
        <{dbpedia_uri}> rdfs:label ?label .
        FILTER (lang(?label) = 'en')
    }}
    """
    url = "http://dbpedia.org/sparql"
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    writer_data_with_bindings = response.json()
    result["uri"] = dbpedia_uri
    result["label"] = writer_data_with_bindings["results"]["bindings"][0]["label"]["value"]
    # Second query gets movies they wrote
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?movie
    WHERE {{
        ?movie dbo:writer <{dbpedia_uri}> .
    }}
    """
    response = requests.get(url, params={"format": "json", "query": query})
    if response.status_code != 200:
        return None
    movie_data_with_bindings = response.json()
    movies = list()
    for movie in movie_data_with_bindings["results"]["bindings"]:
        movies.append(movie["movie"]["value"])
    result["movies"] = movies
    return result

def dbpedia_markdown_link(uri, label = None):
    """Return a markdown link for the given uri and label."""
    if label is None:
        label = uri.split("/")[-1]
    return f"[{label}]({uri})"


def find_movies_by_cast(selected_cast, selected_cast_role, ignore_cache=False):
    """Find movies by cast member."""
    if selected_cast_role == "director":
        return find_director_by_uri(selected_cast)
    elif selected_cast_role == "writer":
        return find_writer_by_uri(selected_cast)
    elif selected_cast_role == "actor":
        return find_actor_by_uri(selected_cast)
    elif selected_cast_role == "all":
        cast_name = selected_cast.split("/")[-1]
        cache_filename = f"{dbpedia_cache}/_CAST_{cast_name}.json"
        if not ignore_cache and os.path.exists(cache_filename):
            with open(cache_filename) as IN:
                return json.load(IN)
        wrapper = dict()
        wrapper["actor"] = find_actor_by_uri(selected_cast)
        wrapper["director"] = find_director_by_uri(selected_cast)
        wrapper["writer"] = find_writer_by_uri(selected_cast)
        wrapper["thumbnail"] = get_person_thumbnail(selected_cast)
        with open(cache_filename, "w") as OUT:
            OUT.write(json.dumps(wrapper, indent=2))
        return wrapper
    else:
        return {}

def search_for_person_in_wikipedia(search_term):
    """Search for a person in wikipedia."""
    search_term = search_term.replace(" ", "_")
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={search_term}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json().get("query",{}).get("search",[])
