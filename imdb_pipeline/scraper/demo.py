"""
Bundled demo movies used when live scraping is unavailable.

Add entries here for any title you want to support offline.
Keys are IMDb title IDs (e.g. ``tt0111161``).
"""

from ..models import MovieData

DEMO_MOVIES: dict[str, MovieData] = {
    "tt0111161": MovieData(
        title="The Shawshank Redemption",
        year="1994",
        rating="9.3",
        votes="2,900,000",
        genre=["Drama"],
        duration="2h 22m",
        director="Frank Darabont",
        cast=["Tim Robbins", "Morgan Freeman", "Bob Gunton",
              "William Sadler", "Clancy Brown", "James Whitmore"],
        plot=(
            "Banker Andy Dufresne is sentenced to life in Shawshank State "
            "Penitentiary for the murder of his wife and her lover, despite "
            "his claims of innocence. Over two decades he befriends Red, "
            "an inmate and contraband smuggler, while the corrupt warden "
            "exploits his financial expertise. Andy never abandons hope — "
            "and his quiet defiance will change everything."
        ),
        tagline="Fear can hold you prisoner. Hope can set you free.",
        imdb_url="https://www.imdb.com/title/tt0111161/",
        pg_rating="R",
        awards="Nominated for 7 Academy Awards",
        trivia=[
            "Considered one of the greatest films ever made",
            "Based on Stephen King's novella 'Rita Hayworth and Shawshank Redemption'",
            "Was a box-office disappointment on release but became a cult classic",
            "Morgan Freeman improvised many of Red's monologues on set",
            "Filmed at the historic Mansfield Reformatory in Ohio",
            "Spent years at #1 on the IMDb Top 250 chart",
        ],
    ),
    "tt0068646": MovieData(
        title="The Godfather",
        year="1972",
        rating="9.2",
        votes="2,000,000",
        genre=["Crime", "Drama"],
        duration="2h 55m",
        director="Francis Ford Coppola",
        cast=["Marlon Brando", "Al Pacino", "James Caan",
              "Richard Castellano", "Robert Duvall", "Diane Keaton"],
        plot=(
            "The aging patriarch of an organized crime dynasty transfers control "
            "of his clandestine empire to his reluctant youngest son Michael. "
            "A sweeping saga of family, loyalty, power, and betrayal that "
            "redefined American cinema forever."
        ),
        tagline="An offer you can't refuse.",
        imdb_url="https://www.imdb.com/title/tt0068646/",
        pg_rating="R",
        awards="Won 3 Academy Awards including Best Picture",
        trivia=[
            "Marlon Brando stuffed his cheeks with cotton for the iconic role",
            "Al Pacino almost didn't get the part of Michael Corleone",
            "The horse's head used in the bed scene was real",
            "Francis Ford Coppola nearly got fired during production",
            "Considered one of the defining films of the gangster genre",
            "Spawned two sequels, completing one of cinema's great trilogies",
        ],
    ),
    "tt0071562": MovieData(
        title="The Godfather Part II",
        year="1974",
        rating="9.0",
        votes="1,300,000",
        genre=["Crime", "Drama"],
        duration="3h 22m",
        director="Francis Ford Coppola",
        cast=["Al Pacino", "Robert De Niro", "Robert Duvall",
              "Diane Keaton", "Lee Strasberg", "Michael V. Gazzo"],
        plot=(
            "The early life and career of Vito Corleone in 1920s New York City "
            "is portrayed, while his son Michael expands and tightens his grip "
            "on the family crime syndicate. A rare sequel that matches — and "
            "arguably surpasses — its predecessor."
        ),
        tagline="I know it was you, Fredo.",
        imdb_url="https://www.imdb.com/title/tt0071562/",
        pg_rating="R",
        awards="Won 6 Academy Awards including Best Picture",
        trivia=[
            "One of the few sequels to win Best Picture at the Oscars",
            "Robert De Niro won Best Supporting Actor for playing young Vito",
            "Shot simultaneously in the US, Italy, and the Dominican Republic",
            "Al Pacino was nominated for Best Actor but did not win",
        ],
    ),
}
