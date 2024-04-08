"""Allows user to search for movies by title using the TMDB API."""

import streamlit

import dbpedia_movie_util
from unique_movie_list import MovieListComplete

my_complete_movie_list = MovieListComplete("tom_zielund_complete_movies")
unrated_movies = my_complete_movie_list.get_unrated_movies()

streamlit.sidebar.write(f"Total movies: {len(my_complete_movie_list.get_movies())}")
streamlit.sidebar.write(f"Unrated movies: {len(unrated_movies)}")
streamlit.sidebar.write(f"Rated movies: {len(my_complete_movie_list.ratings)}")

if unrated_movies:

    streamlit.header("Rate Movies")
    movie = streamlit.selectbox("Select a movie to rate", unrated_movies,
                                format_func=lambda movie: movie.split("/")[-1])
    movie_title = movie.split("/")[-1]
    movie_link = dbpedia_movie_util.dbpedia_markdown_link(movie)
    streamlit.write(f"Selected movie: {movie_link}")
    rate_5 = streamlit.button("5 - Loved it!")
    rate_4 = streamlit.button("4 - Would watch again")
    rate_3 = streamlit.button("3 - Enjoyed it")
    rate_2 = streamlit.button("2 - It was okay")
    rate_1 = streamlit.button("1 - Not my favorite")
    rate_not = streamlit.button("Not a movie")
    if rate_5:
        rating = 5
    elif rate_4:
        rating = 4
    elif rate_3:
        rating = 3
    elif rate_2:
        rating = 2
    elif rate_1:
        rating = 1
    elif rate_not:
        rating = -1
    else:
        rating = 0
    if rating:
        my_complete_movie_list.rate_movie(movie, rating)
        my_complete_movie_list.write()
        streamlit.experimental_rerun()

else:
    streamlit.header("All movies rated!")
    streamlit.write("Change ratings by selecting a movie from the sidebar.")

    selected_movie = streamlit.sidebar.radio("Select a movie to change rating",
                                             list(my_complete_movie_list.get_movies().keys()),
                                                format_func=lambda movie: movie.split("/")[-1])

    if selected_movie:
        selected_movie_title = selected_movie.split("/")[-1]
        selected_movie_link = dbpedia_movie_util.dbpedia_markdown_link(selected_movie)
        streamlit.write(f"Selected movie: {selected_movie_link}")
        current_rating = my_complete_movie_list.ratings[selected_movie]
        streamlit.write(f"Current rating: {current_rating}")
        rate_5 = streamlit.button("5 - Loved it!")
        rate_4 = streamlit.button("4 - Would watch again")
        rate_3 = streamlit.button("3 - Enjoyed it")
        rate_2 = streamlit.button("2 - It was okay")
        rate_1 = streamlit.button("1 - Not my favorite")
        rate_not = streamlit.button("Not a movie")
        if rate_5:
            rating = 5
        elif rate_4:
            rating = 4
        elif rate_3:
            rating = 3
        elif rate_2:
            rating = 2
        elif rate_1:
            rating = 1
        elif rate_not:
            rating = -1
        else:
            rating = 0
        if rating:
            my_complete_movie_list.rate_movie(selected_movie, rating)
            my_complete_movie_list.write()
            streamlit.experimental_rerun()

