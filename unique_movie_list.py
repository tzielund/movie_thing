# Manage a unique movie list
# THis is a list of movies in which no actor, director, or writer appears more than once.
import json
import os
from typing import List, Union

# The list is managed by the MovieList class, which has the following methods:
# - add_movie(movie: Movie) -> None: Adds a movie to the list.
# - remove_movie(movie: Movie) -> None: Removes a movie from the list.
# - get_movies() -> List[Movie]: Returns a list of all movies in the list.
# - get_movies_by_actor(actor: str) -> List[Movie]: Returns a list of movies in which the given actor appears.
# - get_movies_by_director(director: str) -> List[Movie]: Returns a list of movies directed by the given director.
# - get_movies_by_writer(writer: str) -> List[Movie]: Returns a list of movies written by the given writer.

# The Movie class has the following attributes:
# "uri", eg: "http://dbpedia.org/resource/Fargo_(1996_film)",
# "title", eg: "Fargo (1996 film)",
# "director", eg: "http://dbpedia.org/resource/Coen_brothers",
# "writer", eg: "http://dbpedia.org/resource/Coen_brothers",
# "actors", eg: [
# "http://dbpedia.org/resource/Peter_Stormare",
# "http://dbpedia.org/resource/Steve_Buscemi",
# "http://dbpedia.org/resource/William_H._Macy",
# "http://dbpedia.org/resource/Frances_McDormand",
# "http://dbpedia.org/resource/Harve_Presnell"
# ]

MOVIE_LIST_CACHE_DIR = "movie_list_cache/"
os.makedirs(MOVIE_LIST_CACHE_DIR, exist_ok=True)

class Movie:

    def __init__(self, metadata):
        self.uri = metadata["uri"]
        self.title = metadata["title"]
        self.directors = metadata["directors"]
        self.writers = metadata["writers"]
        self.actors = metadata["actors"]

class MovieListComplete:
    """List of movies with an eye for completeness across given contributors."""

    def __init__(self, list_title: str):
        self.list_title = list_title
        self.movies = dict()
        self.not_movies = dict()
        self.cast_covered = dict()
        self.cache_file = f"{MOVIE_LIST_CACHE_DIR}complete_{list_title}.json"
        if os.path.exists(self.cache_file):
            with open(self.cache_file) as IN:
                package = json.load(IN)
                self.movies = dict()
                for movie in package["movies"]:
                    self.add_movie(movie)
                if "not_movies" in package:
                    for movie in package["not_movies"]:
                        self.ignore_movie(movie)
                self.cast_covered = package["cast_covered"]

    def write(self):
        with open (self.cache_file, 'w') as OUT:
            package = dict()
            package["movies"] = list(self.movies.keys())
            package["cast_covered"] = self.cast_covered
            package["not_movies"] = list(self.not_movies.keys())
            OUT.write(json.dumps(package, indent=2))

    def add_movie(self, movie_id, movie_title = None):
        self.dont_ignore_movie(movie_id)
        if not movie_title:
            movie_title = movie_id.split("/")[-1]
        self.movies[movie_id] = movie_title

    def ignore_movie(self, movie_id, movie_title = None):
        self.remove_movie(movie_id)
        if not movie_title:
            movie_title = movie_id.split("/")[-1]
        self.not_movies[movie_id] = movie_title

    def dont_ignore_movie(self, movie_id):
        if movie_id in self.not_movies:
            del self.not_movies[movie_id]

    def remove_movie(self, movie_id):
        if movie_id in self.movies:
            del self.movies[movie_id]

    def has(self, movie_id):
        return movie_id in self.movies

    def is_ignored(self, movie_id):
        return movie_id in self.not_movies

    def get_movies(self):
        return self.movies

    def acknowledge_cast_member(self, cast_member_uri):
        self.cast_covered[cast_member_uri] = True

    def is_cast_member_acknowledged(self, cast_member_uri):
        return cast_member_uri in self.cast_covered

class MovieList:
    def __init__(self, list_title: str):
        self.list_title = list_title
        self.movies = dict()
        self.actor_index = dict()
        self.director_index = dict()
        self.writer_index = dict()
        self.cache_file = f"{MOVIE_LIST_CACHE_DIR}{list_title}.json"
        # Load from cache file if present
        if os.path.exists(self.cache_file):
            with open(self.cache_file) as IN:
                movie_structs = json.load(IN)
                for movie_struct in movie_structs:
                    self.add_movie_from_dict(movie_struct)
            return

    def write(self):
        with open(self.cache_file, "w") as OUT:
            movie_structs = [movie.__dict__ for movie in self.movies.values()]
            OUT.write(json.dumps(movie_structs, indent=2))

    def add_movie_from_dict(self, movie_struct: dict, replace_if_needed: bool = False) -> bool:
        movie = Movie(movie_struct)
        return self.add_movie(movie, replace_if_needed=replace_if_needed)

    def add_movie(self, movie: Movie, replace_if_needed: bool = False) -> bool:
        if self.can_add(movie):
            self.movies[movie.uri] = movie
            self._update_indexes_for_add(movie)
            return True
        if replace_if_needed:
            # identify movies that need to be removed
            to_remove = set()
            reasons = self.cannot_add_complete(movie)
            for reason in reasons:
                to_remove.add(reason[2])
            # to_remove is a list of URIs of movies that need to be removed
            # remove them-- but avoid the modified list while iterating
            for movie_to_remove in to_remove:
                self.remove_movie_by_uri(movie_to_remove)
            self.add_movie(movie)
            return True
        return False

    def _update_indexes_for_add(self, movie: Movie) -> None:
        for director in movie.directors:
            self.director_index[director] = movie.uri
        for writer in movie.writers:
            self.writer_index[writer] = movie.uri
        for actor in movie.actors:
            self.actor_index[actor] = movie.uri

    def _update_indexes_for_remove(self, movie: Movie) -> None:
        for director in movie.directors:
            if director in self.director_index:
                del self.director_index[director]
        for writer in movie.writers:
            if writer in self.writer_index:
                del self.writer_index[writer]
        for actor in movie.actors:
            if actor in self.actor_index:
                del self.actor_index[actor]

    def can_add(self, movie: Movie) -> bool:
        return not self.cannot_add(movie)

    def cannot_add(self, movie: Movie) -> Union[str, bool]:
        # Check if we have a dictionary of actors, directors, and writers
        # If so, convert to a Movie and try again
        if isinstance(movie, dict):
            movie = Movie(movie)
        for director in movie.directors:
            if director in self.director_index:
                return f"Director {director} already used in {self.director_index[director]}"
        for writer in movie.writers:
            if writer in self.writer_index:
                return f"Writer {writer} already used in {self.writer_index[writer]}"
        for actor in movie.actors:
            if actor in self.actor_index:
                return f"Actor {actor} already used in {self.actor_index[actor]}"
        return False

    def cannot_add_complete(self, movie: Movie) -> List[tuple]:
        # Check if we have a dictionary of actors, directors, and writers
        # If so, convert to a Movie and try again
        if isinstance(movie, dict):
            movie = Movie(movie)
        let_me_count_the_ways = list()
        for director in movie.directors:
            if director in self.director_index:
                let_me_count_the_ways.append(("Director", director, self.director_index[director]))
        for writer in movie.writers:
            if writer in self.writer_index:
                let_me_count_the_ways.append(("Writer", writer, self.writer_index[writer]))
        for actor in movie.actors:
            if actor in self.actor_index:
                let_me_count_the_ways.append(("Actor", actor, self.actor_index[actor]))
        return let_me_count_the_ways

    def remove_movie(self, movie: Movie) -> None:
        # Check if we have a dictionary of actors, directors, and writers
        # If so, convert to a Movie and try again
        if isinstance(movie, dict):
            movie = Movie(movie)
        del (self.movies[movie.uri])
        self._update_indexes_for_remove(movie)

    def remove_movie_by_uri(self, uri: str) -> None:
        # find the movie in the list
        del (self.movies[uri])

    def get_movies(self) -> List[Movie]:
        return list(self.movies.values())

    def get_used_actors(self) -> dict:
        return self.actor_index

    def get_used_directors(self) -> dict:
        return self.director_index

    def get_used_writers(self) -> dict:
        return self.writer_index

    def has_movie_by_uri(self, movie_uri):
        return movie_uri in self.movies
