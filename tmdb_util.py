# Utilities for working with TMDB movie api

import json
import os
import requests

TMDB_CACHE = "tmdb_cache"
os.makedirs(TMDB_CACHE, exist_ok=True)

# Get the TMDB API key from the config file or the environment
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    with open(".environment.json") as IN:
        config = json.load(IN)
        TMDB_API_KEY = config["TMDB_API_KEY"]

def get_cached_movie_details(movie_id):
    """Get the movie details from the TMDB API, caching the results."""
    cache_file = f"{TMDB_CACHE}/movie_{movie_id}.json"
    if os.path.exists(cache_file):
        with open(cache_file) as IN:
            return json.load(IN)
    # Otherwise call the API and cache the results
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    result = requests.get(url)
    if result.status_code != 200:
        return None
    movie = result.json()
    # Add the credits details from the API
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
    credits_result = requests.get(credits_url)
    if credits_result.status_code == 200:
        movie["credits"] = credits_result.json()
    with open(cache_file, "w") as OUT:
        OUT.write(json.dumps(movie, indent=2))
    return movie

def set_top_cast_and_crew(movie_id, top_cast_and_crew_dict0):
    """Add the top cast and crew to the movie details."""
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
    credits_result = requests.get(credits_url)
    if credits_result.status_code == 200:
        movie_details["credits"] = credits_result.json()
    return movie_details

def search_for_movie(search_term):
    """Search for a movie by title using the TMDB API."""
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={search_term}"
    response = requests.get(search_url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return response.json()