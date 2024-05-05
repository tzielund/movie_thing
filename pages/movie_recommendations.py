"""Given the complete movie list, recommend movies based on the cast members of the movies in the list."""

import json
import os
import streamlit
import unique_movie_list
import dbpedia_movie_util

movie_list_unique = unique_movie_list.MovieList("tom_zielund_unique_movies")
movie_list_complete = unique_movie_list.MovieListComplete("tom_zielund_complete_movies")

# Get the list of cast members from the complete movie list
complete_cast_film_count = dict()
for movie in movie_list_complete.get_movies():
    movie_title = movie.split("/")[-1]
    dbpedia_details = dbpedia_movie_util.get_movie_data(movie, movie_title)
    for director in dbpedia_details["directors"]:
        if director not in complete_cast_film_count:
            complete_cast_film_count[director] = 0
        complete_cast_film_count[director] += 1
    for writer in dbpedia_details["writers"]:
        if writer not in complete_cast_film_count:
            complete_cast_film_count[writer] = 0
        complete_cast_film_count[writer] += 1
    for actor in dbpedia_details["actors"]:
        if actor not in complete_cast_film_count:
            complete_cast_film_count[actor] = 0
        complete_cast_film_count[actor] += 1

# Sort cast by number of films
sorted_cast = sorted(complete_cast_film_count.items(), key=lambda x: x[1], reverse=True)

# # Now go thru the unseen movies and recommend based on the cast
# unseen_movies = movie_list_complete.not_movies
# recommended_movies = dict()
# size = len(unseen_movies)
# count = 0
# for unseen_movie in unseen_movies:
#     print (f"Processing {count} of {size}")
#     count += 1
#     unseen_movie_title = unseen_movie.split("/")[-1]
#     dbpedia_details = dbpedia_movie_util.get_movie_data(unseen_movie, unseen_movie_title)
#     recommended_movies[unseen_movie] = 0 # Initialize the count
#     for director in dbpedia_details["directors"]:
#         if director in complete_cast_film_count:
#             recommended_movies[unseen_movie] += complete_cast_film_count[director]
#     for writer in dbpedia_details["writers"]:
#         if writer in complete_cast_film_count:
#             recommended_movies[unseen_movie] += complete_cast_film_count[writer]
#     for actor in dbpedia_details["actors"]:
#         if actor in complete_cast_film_count:
#             recommended_movies[unseen_movie] += complete_cast_film_count[actor]
#
# # Sort the recommended movies
# sorted_recommended_movies = sorted(recommended_movies.items(), key=lambda x: x[1], reverse=True)
#
# # Start displaying the results
# streamlit.title("Movie Recommendations")
# streamlit.write("Recommendations based on the cast members of the movies in your list.")
# for recommended_movie, score in sorted_recommended_movies:
#     recommended_movie_title = recommended_movie.split("/")[-1]
#     dbpedia_details = dbpedia_movie_util.get_movie_data(recommended_movie, recommended_movie_title)
#     streamlit.write(f"**{dbpedia_details['title']}**")
#     streamlit.write(f"Score: {score}")
#     streamlit.write(f"Directors: {dbpedia_details['directors']}")
#     streamlit.write(f"Writers: {dbpedia_details['writers']}")
#     streamlit.write(f"Actors: {dbpedia_details['actors']}")