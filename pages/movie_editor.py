"""Allows user to edit the stars, writers, and directors of a movie for their own unique movie list."""

import streamlit
import unique_movie_list
import dbpedia_movie_util

my_unique_movie_list = unique_movie_list.MovieList("tom_zielund_unique_movies")
my_complete_movie_list = unique_movie_list.MovieListComplete("tom_zielund_complete_movies")

streamlit.sidebar.header("My Movie List")
streamlit.write(f"Unique: {len(my_unique_movie_list.get_movies())}")
streamlit.write(f"Complete: {len(my_complete_movie_list.get_movies())}")
complete_or_unique = streamlit.sidebar.radio("View", ["Complete", "Unique"])
selected_movie_uri = None
selected_movie_title = None
if complete_or_unique == "Complete":
    movie_list_plus_none = my_complete_movie_list.get_movies()
else:
    movie_list_plus_none = my_unique_movie_list.get_movie_uri_list().copy()
# movie_list_plus_none.append(None)

movie_list_as_dict = dict()
for movie in movie_list_plus_none:
    movie_title = movie.split("/")[-1]
    movie_list_as_dict[movie] = movie_title

selected_movie_uri = streamlit.sidebar.selectbox("Select a movie to edit", options=movie_list_as_dict.keys(),
                                                format_func=lambda x: f"{movie_list_as_dict[x]}")

movie_selected_object = None
if selected_movie_uri:
    movie_selected_object = my_complete_movie_list.movies.get(selected_movie_uri)
    selected_movie_title = movie_selected_object.title()

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

refresh_cached_movie = streamlit.button("Refresh")

streamlit.write(f"Editing [{selected_movie_title}]({selected_movie_uri})")
dbpedia_details = dbpedia_movie_util.get_movie_data(selected_movie_uri, selected_movie_title, ignore_cache=refresh_cached_movie)
# Write out the details nicely
streamlit.write("Directors:")
for director in dbpedia_details["directors"]:
    d_link = dbpedia_movie_util.dbpedia_markdown_link(director)
    remove_director = streamlit.checkbox(f"* {d_link}", key=f"remove_director_{director}")
    if remove_director:
        confirm = streamlit.checkbox(f"Confirm removal of {d_link}")
        if confirm:
            # Remove director from the movie
            dbpedia_details["directors"].remove(director)
            dbpedia_movie_util.update_movie_data(selected_movie_uri, dbpedia_details)
            streamlit.experimental_rerun()
streamlit.write("Writers:")
for writer in dbpedia_details["writers"]:
    w_link = dbpedia_movie_util.dbpedia_markdown_link(writer)
    remove_writer = streamlit.checkbox(f"* {w_link}", key=f"remove_writer_{writer}")
    if remove_writer:
        confirm = streamlit.checkbox(f"Confirm removal of {w_link}")
        if confirm:
            # Remove writer from the movie
            dbpedia_details["writers"].remove(writer)
            dbpedia_movie_util.update_movie_data(selected_movie_uri, dbpedia_details)
            streamlit.experimental_rerun()
streamlit.write("Actors:")
for actor in dbpedia_details["actors"]:
    a_link = dbpedia_movie_util.dbpedia_markdown_link(actor)
    remove_actor = streamlit.checkbox(f"* {a_link}", key=f"remove_actor_{actor}")
    if remove_actor:
        confirm = streamlit.checkbox(f"Confirm removal of {a_link}")
        if confirm:
            # Remove actor from the movie
            dbpedia_details["actors"].remove(actor)
            dbpedia_movie_util.update_movie_data(selected_movie_uri, dbpedia_details)
            streamlit.experimental_rerun()
add_an_actor_search = streamlit.text_input("Find someone")
if add_an_actor_search:
    name_list = dbpedia_movie_util.search_for_person_in_wikipedia(add_an_actor_search)
    # streamlit.json(name_list)
    filmography_picker = streamlit.selectbox("Pick a matching person", options = name_list,
                                             format_func=lambda x: x['title'])
    if not filmography_picker:
        streamlit.stop()
    # streamlit.json(filmography_picker)
    chosen_dbpedia_uri = f"http://dbpedia.org/resource/{filmography_picker['title']}"
    chosen_dbpedia_uri = chosen_dbpedia_uri.replace(" ", "_")
    streamlit.write(chosen_dbpedia_uri)

    add_actor = streamlit.button("Add as an actor")
    if add_actor:
        dbpedia_details["actors"].append(chosen_dbpedia_uri)
        dbpedia_movie_util.update_movie_data(selected_movie_uri, dbpedia_details)
        streamlit.experimental_rerun()
    add_writer = streamlit.button("Add as a writer")
    if add_writer:
        dbpedia_details["writers"].append(chosen_dbpedia_uri)
        dbpedia_movie_util.update_movie_data(selected_movie_uri, dbpedia_details)
        streamlit.experimental_rerun()
    add_director = streamlit.button("Add as a director")
    if add_director:
        dbpedia_details["directors"].append(chosen_dbpedia_uri)
        dbpedia_movie_util.update_movie_data(selected_movie_uri, dbpedia_details)
        streamlit.experimental_rerun()

# Show release date and gross revenue
streamlit.write("Now for something completely different")
streamlit.write(f"Release date: {dbpedia_details['release_date']}")
streamlit.write(f"Gross revenue: {dbpedia_details['gross_revenue']}")
