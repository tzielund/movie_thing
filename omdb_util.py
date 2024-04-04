# Search and lookup movie details using the OMDB API.

import json
import os
import requests

OMDB_CACHE = "omdb_cache"
os.makedirs(OMDB_CACHE, exist_ok=True)

# Get the OMDB API key from the config file or the environment
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")
if not OMDB_API_KEY:
    with open(".environment.json") as IN:
        config = json.load(IN)
        OMDB_API_KEY = config["OMDB_API_KEY"]

def get_cached_movie_details(movie_title):
    """Get the movie details from the OMDB API, caching the results."""
    cache_file = f"{OMDB_CACHE}/{movie_title}.json"
    if os.path.exists(cache_file):
        with open(cache_file) as IN:
            return json.load(IN)
    # Otherwise call the API and cache the results
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"
    result = requests.get(url)
    if result.status_code != 200:
        return None
    movie = result.json()
    with open(cache_file, "w") as OUT:
        OUT.write(json.dumps(movie, indent=2))
    return movie

def search_for_movie(search_term):
    """Search for a movie by title using the OMDB API."""
    print("Searching for movie with omdb")
    search_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={search_term}"
    response = requests.get(search_url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return response.json()

