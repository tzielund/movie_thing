"""Allows user to review which frequent cast members in the complete movie list are covered in the unique list."""

import streamlit

import dbpedia_movie_util
from unique_movie_list import MovieList, MovieListComplete, Movie

my_unique_movie_list = MovieList("tom_zielund_unique_movies")
my_complete_movie_list = MovieListComplete("tom_zielund_complete_movies")

show_known_cast = streamlit.sidebar.checkbox("Show known cast")
show_unaddable_movies = streamlit.sidebar.checkbox("Show unaddable movies")
show_unseen_movies = streamlit.sidebar.checkbox("Show unseen movies")
check_ahead_if_options_are_available = streamlit.sidebar.checkbox("Check ahead if options are available")

frequent_cast = dict()
for movie in my_complete_movie_list.get_movies():
    movie_title = movie.split("/")[-1]
    dbpedia_details = dbpedia_movie_util.get_movie_data(movie, movie_title)
    for director in dbpedia_details["directors"]:
        if director not in frequent_cast:
            frequent_cast[director] = 0
        frequent_cast[director] += 1
    for writer in dbpedia_details["writers"]:
        if writer not in frequent_cast:
            frequent_cast[writer] = 0
        frequent_cast[writer] += 1
    for actor in dbpedia_details["actors"]:
        if actor not in frequent_cast:
            frequent_cast[actor] = 0
        frequent_cast[actor] += 1
# Sort by frequency, desc)
frequent_cast = sorted(frequent_cast.items(), key=lambda x: x[1], reverse=True)

covered_cast = dict()
for movie in my_unique_movie_list.get_movies():
    movie_title = movie.title
    dbpedia_details = dbpedia_movie_util.get_movie_data(movie.uri, movie_title)
    for director in dbpedia_details["directors"]:
        covered_cast[director] = movie
    for writer in dbpedia_details["writers"]:
        covered_cast[writer] = movie
    for actor in dbpedia_details["actors"]:
        covered_cast[actor] = movie

streamlit.title("Frequent Cast Members")
for cast_member, film_count in frequent_cast:
    cast_link = dbpedia_movie_util.dbpedia_markdown_link(cast_member)
    if cast_member in covered_cast:
        if show_known_cast:
            covered_movie = covered_cast[cast_member]
            covered_movie_link = dbpedia_movie_util.dbpedia_markdown_link(covered_movie.uri)
            streamlit.markdown (f"- [x] {cast_link} ({covered_movie_link})")
    else:
        look_closer = streamlit.checkbox(f"{cast_link}: {film_count}")
        if look_closer or check_ahead_if_options_are_available:
            # List out the filmography
            streamlit.write(f"**{cast_link}**")
            filmography_search_results = dbpedia_movie_util.find_movies_by_cast(cast_member, 'all')
            if "thumbnail" not in filmography_search_results:
                filmography_search_results = dbpedia_movie_util.find_movies_by_cast(cast_member, 'all', ignore_cache=True)
            thumbnail = filmography_search_results.get("thumbnail")
            if thumbnail:
                streamlit.image(thumbnail)
            # streamlit.json(filmography_search_results)
            filmography_movie_set = set()
            for movie in filmography_search_results["director"]["movies"]:
                filmography_movie_set.add(movie)
            for movie in filmography_search_results["writer"]["movies"]:
                filmography_movie_set.add(movie)
            for movie in filmography_search_results["actor"]["movies"]:
                filmography_movie_set.add(movie)

            for movie in filmography_movie_set:
                if movie not in my_complete_movie_list.movies:
                    if show_unseen_movies:
                        streamlit.write(f" -- {dbpedia_movie_util.dbpedia_markdown_link(movie)} (unseen)")
                    continue
                # Check if this could be added to the unique list
                movie_data = dbpedia_movie_util.get_movie_data(movie, movie.split("/")[-1])
                movie_link = dbpedia_movie_util.dbpedia_markdown_link(movie)
                cannot_add_reasons = my_unique_movie_list.cannot_add_complete(movie_data)
                if cannot_add_reasons:
                    if show_unaddable_movies:
                        streamlit.write(f" -- {movie_link} (cannot add)")
                        for (reason, who, what) in cannot_add_reasons:
                            who_name = who.split("/")[-1]
                            what_name = what.split("/")[-1]
                            streamlit.write(f"    - {reason} {who_name} {what_name}")
                else:
                    add_it = streamlit.checkbox(f" -- {movie_link} ", key=movie + f"_director {cast_link}")
                    if add_it:
                        movie_cast = dbpedia_movie_util.get_movie_data(movie, movie.split("/")[-1])
                        for director in movie_cast["directors"]:
                            streamlit.write(f" -- Director: {dbpedia_movie_util.dbpedia_markdown_link(director)}")
                        for writer in movie_cast["writers"]:
                            streamlit.write(f" -- Writer: {dbpedia_movie_util.dbpedia_markdown_link(writer)}")
                        for actor in movie_cast["actors"]:
                            streamlit.write(f" -- Actor: {dbpedia_movie_util.dbpedia_markdown_link(actor)}")
                        confirm_add = streamlit.checkbox("Add this movie?")
                        if confirm_add:
                            my_unique_movie_list.add_movie_from_dict(movie_data)
                            my_unique_movie_list.write()
                            streamlit.write("Added")
            if look_closer:
                streamlit.stop()
