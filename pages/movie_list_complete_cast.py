"""Allows user to search for movies by title using the TMDB API."""

import streamlit

import dbpedia_movie_util
from unique_movie_list import MovieListComplete

my_complete_movie_list = MovieListComplete("tom_zielund_complete_movies")
my_complete_cast_film_count = dict()
for movie in my_complete_movie_list.get_movies():
    movie_title = movie.split("/")[-1]
    dbpedia_details = dbpedia_movie_util.get_movie_data(movie, movie_title)
    for director in dbpedia_details["directors"]:
        if director not in my_complete_cast_film_count:
            my_complete_cast_film_count[director] = 0
        my_complete_cast_film_count[director] += 1
    for writer in dbpedia_details["writers"]:
        if writer not in my_complete_cast_film_count:
            my_complete_cast_film_count[writer] = 0
        my_complete_cast_film_count[writer] += 1
    for actor in dbpedia_details["actors"]:
        if actor not in my_complete_cast_film_count:
            my_complete_cast_film_count[actor] = 0
        my_complete_cast_film_count[actor] += 1

# sort cast by number of films
sorted_cast = sorted(my_complete_cast_film_count.items(), key=lambda x: x[1], reverse=True)

streamlit.sidebar.header(f"My Movie Cast ({len(my_complete_movie_list.get_movies())})")
default_cast_member = ""
for cast_member, film_count in sorted_cast:
    cast_link = dbpedia_movie_util.dbpedia_markdown_link(cast_member)
    acknowledged = my_complete_movie_list.is_cast_member_acknowledged(cast_member)
    if acknowledged:
        cast_link += " (ack)"
    check_cast = streamlit.sidebar.checkbox(f"{cast_link} ({film_count})", key=f"check_cast_{cast_member}",
                                           value=not acknowledged and not default_cast_member)
    if check_cast:
        default_cast_member = cast_member

if default_cast_member:
    default_cast_member_uri = default_cast_member
    default_cast_member = default_cast_member.replace("http://dbpedia.org/resource/", "")
    default_cast_member = default_cast_member.replace("_", " ")
search_term = streamlit.text_input("Enter a contributor name", value=default_cast_member)
if search_term:
    name_list = dbpedia_movie_util.search_for_person_in_wikipedia(search_term)
    # streamlit.json(name_list)
    filmography_picker = streamlit.selectbox("Pick a person to see thier filmography", options = name_list,
                                             format_func=lambda x: x['title'])
    if not filmography_picker:
        streamlit.stop()

    chosen_dbpedia_uri = f"http://dbpedia.org/resource/{filmography_picker['title']}"
    chosen_dbpedia_uri = chosen_dbpedia_uri.replace(" ", "_")
    streamlit.write(chosen_dbpedia_uri)
    filmography_search_results = dbpedia_movie_util.find_movies_by_cast(chosen_dbpedia_uri, 'all')
    filmography_film_set = set()
    filmography_film_set.update(filmography_search_results["actor"]["movies"])
    filmography_film_set.update(filmography_search_results["director"]["movies"])
    filmography_film_set.update(filmography_search_results["writer"]["movies"])
    movies_to_add = set()
    movies_not_to_add = set()

    # Go thru the filmography and show a checkbox for each movie
    # Go thru twice.  First show the movies that are already in the list
    # Then show the movies that are not in the list
    for movie_uri in filmography_film_set:
        movie_link = dbpedia_movie_util.dbpedia_markdown_link(movie_uri)
        is_in_my_list = my_complete_movie_list.has(movie_uri)
        if is_in_my_list:
            streamlit.markdown(f"- [x] {movie_link} (in my list)")
    for movie_uri in filmography_film_set:
        movie_link = dbpedia_movie_util.dbpedia_markdown_link(movie_uri)
        is_in_my_list = my_complete_movie_list.has(movie_uri)
        if is_in_my_list:
            pass
        else:
            if my_complete_movie_list.is_ignored(movie_uri):
                add_it = streamlit.checkbox(f" *** {movie_link} (seen it)")
            else:
                add_it = streamlit.checkbox(f"{movie_link}")
            if add_it:
                movies_to_add.add(movie_uri)
            else:
                movies_not_to_add.add(movie_uri)
    patch_cast_uri = streamlit.text_input(f"Patch {chosen_dbpedia_uri}", value=default_cast_member_uri)
    if movies_to_add:
        do_it = streamlit.button("Add selected movies to my list")
        if do_it:
            for movie_uri in movies_to_add:
                my_complete_movie_list.add_movie(movie_uri)
            for movie_uri in movies_not_to_add:
                my_complete_movie_list.ignore_movie(movie_uri)
            my_complete_movie_list.acknowledge_cast_member(chosen_dbpedia_uri)
            if patch_cast_uri != chosen_dbpedia_uri:
                my_complete_movie_list.acknowledge_cast_member(patch_cast_uri)
            my_complete_movie_list.write()
            streamlit.write("Added to list")
            streamlit.experimental_rerun()
    # streamlit.json(filmography_search_results)

    else:
        streamlit.write("No movies selected")
        acknowledge_cast_member = streamlit.button(f"Acknowledge {chosen_dbpedia_uri}")
        if acknowledge_cast_member:
            for movie_uri in movies_not_to_add:
                my_complete_movie_list.ignore_movie(movie_uri)
            my_complete_movie_list.acknowledge_cast_member(chosen_dbpedia_uri)
            if patch_cast_uri != chosen_dbpedia_uri:
                my_complete_movie_list.acknowledge_cast_member(patch_cast_uri)
            my_complete_movie_list.write()
            streamlit.experimental_rerun()


# While waiting, cache as many cast members as possible
do_background = streamlit.checkbox("Cache filmographies in background")
if do_background:
    for movie in my_complete_movie_list.get_movies():
        movie_title = movie.split("/")[-1]
        dbpedia_details = dbpedia_movie_util.get_movie_data(movie, movie_title)
        for director in dbpedia_details["directors"]:
            filmography_cache_results = dbpedia_movie_util.find_movies_by_cast(director, 'all')
            print(f"Cached {director}")
        for writer in dbpedia_details["writers"]:
            filmography_cache_results = dbpedia_movie_util.find_movies_by_cast(writer, 'all')
            print(f"Cached {writer}")
        for actor in dbpedia_details["actors"]:
            filmography_cache_results = dbpedia_movie_util.find_movies_by_cast(actor, 'all')
            print(f"Cached {actor}")
