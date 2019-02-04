from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import GameGenre, Base, ListGame, User

engine = create_engine('sqlite:///gamelist.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


firstuser = User(name="admin", email="satyamadhu0109@gmail.com")
session.add(firstuser)
session.commit()

# Menu for UrbanBurger
game1 = GameGenre(name="Action", user_id=1)
session.add(game1)
session.commit()

listgame1 = ListGame(name="DmC Devil May Cry",
                     description="allow the player to tweak gameplay"
                     "to suit their own style ",
                     price='$30', games=game1, user_id=1)
session.add(listgame1)
session.commit()


listgame2 = ListGame(name="Grand Theft Auto 5",
                     description="The definitive version of"
                     "Rockstar's biggest world to date.", price='$40',
                     games=game1, user_id=1)
session.add(listgame2)
session.commit()

listgame3 = ListGame(name="Bloodborne",
                     description="A superb, intelligent"
                     "evolution of the series. ", price='$35',
                     games=game1, user_id=1)
session.add(listgame3)
session.commit()


# Menu for Super Stir Fry
game2 = GameGenre(name="Adventure", user_id=1)
session.add(game2)
session.commit()


listgame1 = ListGame(name="The Walking Dead",
                     description="A House Divided doesn't just put plonk"
                     "them in harm's way but also tests your loyalties in"
                     "some really underhanded ways", price='$32', games=game2,
                     user_id=1)
session.add(listgame1)
session.commit()

listgame2 = ListGame(name="Firewatch",
                     description="Firewatch is a game about escape,"
                     "loneliness, friendship and facing reality, told in a"
                     "tightly controlled explorable world", price='$33',
                     games=game2, user_id=1)
session.add(listgame2)
session.commit()

listgame3 = ListGame(name="Batman: Arkham VR",
                     description="A short but stunning 90-minute"
                     "experience that truly lets you 'Be the Batman'."
                     "Batman: Arkham VR is an incredible experience",
                     price='$35', games=game2, user_id=1)
session.add(listgame3)
session.commit()

# Menu for Panda Garden
game3 = GameGenre(name="Racing", user_id=1)
session.add(game3)
session.commit()

listgame1 = ListGame(name="GTR Evolution",
                     description="the rest of the game is all"
                     " you could ask from a racing sim", price='$40',
                     games=game3, user_id=1)
session.add(listgame1)
session.commit()

listgame2 = ListGame(name="Need for Speed Hot Pursuit",
                     description="Story is nowhere to be seen, meaning you're"
                     "thrown straight into the action via the game's map",
                     price='$38', games=game3, user_id=1)
session.add(listgame2)
session.commit()

listgame3 = ListGame(name="Driver: San Francisco",
                     description="Driver San Francisco could have been a"
                     "one-trick pony but it has managed to use that trick in a"
                     "variety of clever and interesting ways, ensuring the"
                     "driving gameplay never becomes tiresome or generic.",
                     price='$50', games=game3, user_id=1)
session.add(listgame3)
session.commit()


# Menu for Thyme for that
game4 = GameGenre(name="Shooting", user_id=1)
session.add(game4)
session.commit()

listgame1 = ListGame(name="Call of Duty: Black Ops II",
                     description="Pushing the boundaries of what fans "
                     "have come to expect from the record-setting"
                     "entertainment franchise, Call of Duty: Black Ops"
                     "II propels players into a"
                     "near future",
                     price='$55', games=game4, user_id=1)
session.add(listgame1)
session.commit()

listgame2 = ListGame(name="Left 4 Dead 2", description="Left 4 Dead 2 is"
                     "set at roughly the same time as the original -"
                     "just after the outbreak that turned most of the"
                     "population into various zombie mutants",
                     price='$25',
                     games=game4, user_id=1)
session.add(listgame2)
session.commit()

listgame3 = ListGame(name="Max Payne 3", description="For Max Payne,"
                     "the tragedies that took his loved ones years"
                     "ago are wounds that refuse to heal", price='$30',
                     games=game4, user_id=1)
session.add(listgame3)
session.commit()


# Menu for Tony's Bistro
game5 = GameGenre(name="Sports", user_id=1)
session.add(game5)
session.commit()


listgame1 = ListGame(name="PES 2018", description="Lobster,"
                     "shrimp, sea snails, crawfish, stacked into a"
                     "delicious tower",
                     price='$35', games=game5, user_id=1)
session.add(listgame1)
session.commit()

listgame2 = ListGame(name="EA Sports 2018 FIFA World Cup Brazil",
                     description="An enjoyable stopgap which bodes"
                     "well for the series future.", price='$55',
                     games=game5, user_id=1)
session.add(listgame2)
session.commit()

listgame3 = ListGame(name="NBA 2K18", description="NBA 2K11 is a"
                     "seriously slick production, featuring superb"
                     "presentation throughout, from the detailed characters",
                     price='$45',
                     games=game5, user_id=1)
session.add(listgame3)
session.commit()

# Menu for Andala's
game6 = GameGenre(name="Puzzle", user_id=1)
session.add(game6)
session.commit()


listgame1 = ListGame(name="Pac-Man", description="The hungry little"
                     "three-quarters of a pie-chart is up to his"
                     "same old tricks - wolfing down stuff like fruit,"
                     "keys and enemy ghosts", price='$15',
                     games=game6, user_id=1)
session.add(listgame1)
session.commit()

listgame2 = ListGame(name="FEZ", description="Fez's ornate world,"
                     "sumptuous audiovisual presentation, and cryptic"
                     "machinations make us feel like an adrift archaeologist"
                     "filled with wonder", price='$18',
                     games=game6, user_id=1)
session.add(listgame2)
session.commit()

listgame3 = ListGame(name="Limbo", description="Limbo is a puzzle game that"
                     "is littered with ideas and an artistic eye, but more"
                     "importantly it understands the frustrations of"
                     "repetition and makes failure enjoyable", price='$16',
                     games=game6, user_id=1)
session.add(listgame3)
session.commit()

print "added menu items!"
