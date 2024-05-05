"""Allows user to search for movies by title using the TMDB API."""

import streamlit

import dbpedia_movie_util
from unique_movie_list import MovieList, MovieListComplete, Movie

my_unique_movie_list = MovieList("tom_zielund_unique_movies")
my_complete_movie_list = MovieListComplete("tom_zielund_complete_movies")

streamlit.sidebar.header(f"My Movie List {len(my_unique_movie_list.get_movies())}")
sorted_movies = list(my_unique_movie_list.get_movies())
sorted_movies.sort(key=lambda x: x.title)
for movie in sorted_movies:
    streamlit.sidebar.markdown(f"[{movie.title}]({movie.uri})")

selected_cast = None
selected_cast_role = None

used_directors = my_unique_movie_list.get_used_directors()
show_directors = streamlit.sidebar.checkbox(f"Used Directors ({len(used_directors)})")
if show_directors:
    for director in used_directors:
        director_link = dbpedia_movie_util.dbpedia_markdown_link(director)
        d_movie_link = dbpedia_movie_util.dbpedia_markdown_link(used_directors[director])
        director_check = streamlit.sidebar.checkbox(f"{director_link}: {d_movie_link}", disabled=selected_cast is not None)
        if director_check:
            selected_cast = director
            selected_cast_role = "director"

used_writers = my_unique_movie_list.get_used_writers()
show_writers = streamlit.sidebar.checkbox(f"Used Writers ({len(used_writers)})")
if show_writers:
    for writer in used_writers:
        writer_link = dbpedia_movie_util.dbpedia_markdown_link(writer)
        w_movie_link = dbpedia_movie_util.dbpedia_markdown_link(used_writers[writer])
        writer_check = streamlit.sidebar.checkbox(f"{writer_link}: {w_movie_link}", disabled=selected_cast is not None)
        if writer_check:
            selected_cast = writer
            selected_cast_role = "writer"

used_actors = my_unique_movie_list.get_used_actors()
show_actors = streamlit.sidebar.checkbox(f"Used Actors ({len(used_actors)})")
if show_actors:
    for actor in used_actors:
        actor_link = dbpedia_movie_util.dbpedia_markdown_link(actor)
        a_movie_link = dbpedia_movie_util.dbpedia_markdown_link(used_actors[actor])
        actor_check = streamlit.sidebar.checkbox(f"{actor_link}: {a_movie_link}", disabled=selected_cast is not None)
        if actor_check:
            selected_cast = actor
            selected_cast_role = "actor"

if selected_cast:
    # Search for movies with the selected cast member
    streamlit.header(f"Movies with {selected_cast_role} {selected_cast}")
    cast_movies = dbpedia_movie_util.find_movies_by_cast(selected_cast, selected_cast_role).get("movies", [])
    for movie in cast_movies:
        movie_link = dbpedia_movie_util.dbpedia_markdown_link(movie)
        streamlit.write(f"* {movie_link}")
    streamlit.stop()

streamlit.title("Search for a movie to add to your list")

how_to_search = streamlit.selectbox("How to search", ["Pick from list", "Search by title"])

if how_to_search == "Search by title":
    streamlit.header("Search for a movie to add to your list")

    search_term = streamlit.text_input("Enter a movie title")
    if search_term:
        dbpedia_search = dbpedia_movie_util.search_for_movies_by_title(search_term)
        # streamlit.json(dbpedia_search)
        if dbpedia_search:
            for (movie_uri,movie_title) in dbpedia_search:
                # Show a radio button for each result
                fetch_details = streamlit.checkbox(f"{movie_title} ({movie_uri})")
                if not fetch_details:
                    continue
                streamlit.write("DBPedia details:")
                dbpedia_details = dbpedia_movie_util.get_movie_data(movie_uri, movie_title)
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

                # Check if it's already in the unique movie list:
                if my_unique_movie_list.has_movie_by_uri(movie_uri):
                    streamlit.write("Movie already in your list")
                    continue

                # Check if it could be added to the unique movie list
                reasons_for_failure = my_unique_movie_list.cannot_add_complete(dbpedia_details)
                if reasons_for_failure:
                    streamlit.write("Cannot add to your list")
                    for reason in reasons_for_failure:
                        credit_type = reason[0]
                        credited_person_link = dbpedia_movie_util.dbpedia_markdown_link(reason[1])
                        credited_movie_link = dbpedia_movie_util.dbpedia_markdown_link(reason[2])
                        streamlit.write(f"{credit_type} {credited_person_link} already used in {credited_movie_link}")
                    add_anyway = streamlit.button("Add anyway and replace these?")
                    if add_anyway:
                        my_unique_movie_list.add_movie_from_dict(dbpedia_details, replace_if_needed=True)
                        my_unique_movie_list.write()
                        streamlit.write("Added to your list")
                        acknowledge = streamlit.button("OK")
                        if acknowledge:
                            streamlit.experimental_rerun()
                        else:
                            streamlit.stop()
                    else:
                        continue
                else: # no reasons for failure
                    add_to_my_list = streamlit.checkbox("Add to my list")
                    if add_to_my_list:
                        result = my_unique_movie_list.add_movie_from_dict(dbpedia_details)
                        if not result:
                            streamlit.write("Failed to add to your list")
                            streamlit.stop()
                        else:
                            my_unique_movie_list.write()
                            streamlit.write("Added to your list")
                            acknowledge = streamlit.button("OK")
                            if acknowledge:
                                streamlit.experimental_rerun()
                            else:
                                streamlit.stop()

else:
    streamlit.header("Pick a movie from your complete list")
    complete_movie_set = set(my_complete_movie_list.movies.keys())
    unique_movie_set = set(my_unique_movie_list.movies.keys())
    complete_movie_minus_unique = complete_movie_set - unique_movie_set
    # sort the list by rating, descending
    complete_movie_minus_unique = sorted(complete_movie_minus_unique,
                                         key=lambda x: my_complete_movie_list.ratings.get(x, 0), reverse=True)
    streamlit.write(f"Movies in your complete list that are not in your unique list: {len(complete_movie_minus_unique)}")
    show_impossible = streamlit.checkbox("Show movies that cannot be added")
    search_term = streamlit.text_input("Enter a movie title")
    for movie_uri in complete_movie_minus_unique:
        if search_term and search_term.lower() not in movie_uri.lower():
            continue
        movie = dbpedia_movie_util.get_movie_data(movie_uri, movie_uri)
        movie_link = dbpedia_movie_util.dbpedia_markdown_link(movie_uri)
        reason_cannot_add = my_unique_movie_list.cannot_add_complete(movie)
        if reason_cannot_add:
            if not show_impossible:
                continue
            add_it_anyway = streamlit.checkbox(f"{movie_link} (cannot add)")
            for (reason, person, film) in reason_cannot_add:
                person_name = person.split("/")[-1]
                film_name = film.split("/")[-1]
                streamlit.write(f"--* {reason} {person_name} already used in {film_name}")
            # streamlit.write(f"* {movie_link} ({reason_cannot_add})")
            if add_it_anyway:
                do_it = streamlit.button("Add anyway")
                if do_it:
                    my_unique_movie_list.add_movie_from_dict(movie, replace_if_needed=True)
                    my_unique_movie_list.write()
                    streamlit.experimental_rerun()
                else:
                    streamlit.stop()
        else:
            add_it = streamlit.checkbox(f"* {movie_link} (available)")
            if add_it:
                movie_data = dbpedia_movie_util.get_movie_data(movie_uri, movie_uri)
                for director in movie_data["directors"]:
                    d_link = dbpedia_movie_util.dbpedia_markdown_link(director)
                    streamlit.markdown(f"* {d_link} (director)")
                for writer in movie_data["writers"]:
                    w_link = dbpedia_movie_util.dbpedia_markdown_link(writer)
                    streamlit.markdown(f"* {w_link} (writer)")
                for actor in movie_data["actors"]:
                    a_link = dbpedia_movie_util.dbpedia_markdown_link(actor)
                    streamlit.markdown(f"* {a_link} (actor)")
                do_it = streamlit.button("Add to my list")
                remove_it = streamlit.button("Remove from my list")
                not_a_movie = streamlit.button("Not a movie")
                if do_it:
                    my_unique_movie_list.add_movie_from_dict(movie)
                    my_unique_movie_list.write()
                    streamlit.experimental_rerun()
                elif remove_it:
                    my_complete_movie_list.remove_movie(movie_uri)
                    my_complete_movie_list.write()
                    streamlit.experimental_rerun()
                elif not_a_movie:
                    my_complete_movie_list.ratings[movie_uri] = -1
                    my_complete_movie_list.write()
                    streamlit.experimental_rerun()
                else:
                    streamlit.stop()
    streamlit.write("No more movies to add")

# streamlit.header("Search for an actor")
# actor_search_term = streamlit.text_input("Enter an actor's dbpedia uri")
# if not actor_search_term:
#     streamlit.stop()
# actor_search_results = dbpedia_movie_util.find_actor_by_uri(actor_search_term)
# for movie_uri in actor_search_results["movies"]:
#     movie_link = dbpedia_movie_util.dbpedia_markdown_link(movie_uri)
#     streamlit.write(f"* {movie_link}")
# streamlit.json(actor_search_results)