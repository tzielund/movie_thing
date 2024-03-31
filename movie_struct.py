
class Movie:
    """Represents a movie with basic metadata."""

    def __init__(self, id, title, release_date, directors, writers, cast):
        """Initializes a new Movie object with the given details."""
        self.id = id
        self.title = title
        self.release_date = release_date
        self.directors = directors
        self.writers = writers
        self.cast = cast

