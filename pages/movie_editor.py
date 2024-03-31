"""Allows user to edit the stars, writers, and directors of a movie for their own unique movie list."""

import streamlit
import unique_movie_list
import dbpedia_movie_util

my_unique_movie_list = unique_movie_list.MovieList("tom_zielund_unique_movies")

streamlit.sidebar.header("My Movie List")
selected_movie_uri = None
selected_movie_title = None
movie_list_plus_none = my_unique_movie_list.get_movies().copy()
movie_list_plus_none.append(None)
movie_selected_object = streamlit.sidebar.radio("Select a movie to edit", options=movie_list_plus_none,
                                                format_func=lambda x: f"[{x.title}]({x.uri})")

if movie_selected_object:
    selected_movie_uri = movie_selected_object.uri
    selected_movie_title = movie_selected_object.title

if not selected_movie_uri:
    streamlit.write("Search for a movie to edit")
    search_term = streamlit.text_input("Enter a movie title")
    if not search_term:
        streamlit.stop()
    dbpedia_search = dbpedia_movie_util.search_for_movies_by_title(search_term)
    # streamlit.json(dbpedia_search)
    if dbpedia_search:
        for (found_movie_uri,found_movie_title) in dbpedia_search:
            # Show a radio button for each result
            movie_selected = streamlit.checkbox(f"{found_movie_title} ({found_movie_uri})")
            if movie_selected:
                selected_movie_uri = found_movie_uri
                selected_movie_title = found_movie_title

if not selected_movie_uri:
    streamlit.write("Select a movie to edit")
    streamlit.stop()

streamlit.write(f"Editing {selected_movie_title}")
dbpedia_details = dbpedia_movie_util.get_movie_data(selected_movie_uri, selected_movie_title)
# Write out the details nicely
streamlit.write("Directors:")
for director in dbpedia_details["directors"]:
    d_link = dbpedia_movie_util.dbpedia_markdown_link(director)
    streamlit.markdown(f"* {d_link}")
streamlit.write("Writers:")
for writer in dbpedia_details["writers"]:
    w_link = dbpedia_movie_util.dbpedia_markdown_link(writer)
    streamlit.markdown(f"* {w_link}")
streamlit.write("Actors:")
for actor in dbpedia_details["actors"]:
    a_link = dbpedia_movie_util.dbpedia_markdown_link(actor)
    streamlit.markdown(f"* {a_link}")
add_an_actor_search = streamlit.text_input("Add an actor (searches for names)")
add_an_actor_button = streamlit.button("Add actor")
if add_an_actor_button and add_an_actor_search:
    actor_search_results = dbpedia_movie_util.search_for_person_in_wikipedia(add_an_actor_search)
    if actor_search_results:
        streamlit.json(actor_search_results)
        for actor_uri,actor_name in actor_search_results:
            actor_check = streamlit.checkbox(f"{actor_name} ({actor_uri})")
            if actor_check:
                # Add actor to the movie
                pass

