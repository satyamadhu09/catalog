from flask import Flask, render_template, jsonify
from flask import redirect, url_for, request, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, GameGenre, ListGame, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import random
import string
import json
import requests
import os
import json
from flask import make_response
from login import login_required
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Game World"


engine = create_engine('sqlite:///gamelist.db',
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# creating login session
@app.route('/login')
def showlogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# creating gconnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        ''' Upgrade the authorization code into a credentials object'''
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps('''Failed to upgrade the
                                            authorization code.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Check that the access token is valid.'''
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    ''' If there was an error in the access token info, abort.'''
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Verify that the access token is used for the intended user.'''
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("""Token's user ID doesn't
                                            match given user ID."""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Verify that the access token is valid for this app.'''
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("""Token's client ID does
                                            not match app's."""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user is
                                            already connected.'''), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    ''' Store the access token in the session for later use.'''
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    ''' Get user info'''
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    login_session['provider'] = 'google'

    ''' See if a user exists, if it doesn't make a new one'''
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createNewUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createNewUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# disconnect from connected user
@app.route("/glogout")
def gdisconnect():
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(json.dumps('''Current user not
                                            connected.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        ''' Reset the user's sesson. '''
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully Logged Out!!!')
        return redirect(url_for('showGames'))
    else:
        ''' For whatever reason, the given token was invalid. '''
        response = make_response(json.dumps('''Failed to revoke token
                                            for given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/games/<int:game_id>/menu/JSON')
def gameMenuJSON(game_id):
    game = session.query(GameGenre).filter_by(id=game_id).one()
    list = session.query(ListGame).filter_by(game_id=game_id).all()
    return jsonify(ListGame=[i.serialize for i in list])


# ADD JSON ENDPOINT HERE
@app.route('/games/<int:game_id>/menu/<int:list_id>/JSON')
def gameListJSON(game_id, list_id):
    gameList = session.query(ListGame).filter_by(id=list_id).one()
    return jsonify(ListGame=gameList.serialize)


@app.route('/restaurants/JSON')
def gameJSON():
    game = session.query(GameGenre).all()
    return jsonify(game=[r.serialize for r in game])


@app.route('/')
@app.route('/games/')
def showGames():
    game = session.query(GameGenre).all()
    if 'username' not in login_session:
        return render_template('games.html', game=game)
    return render_template('showgame.html', game=game)


@app.route('/games/new/', methods=['GET', 'POST'])
@login_required
def newGame():

    game = session.query(GameGenre)
    # admin = getUserInfo(GameGenre.user_id)

    if 'username' not in login_session:
        return render_template('showgame.html', game=game)
    if request.method == 'POST':
        newGame = GameGenre(name=request.form['name'],
                            user_id=login_session['user_id'])
        session.add(newGame)
        session.commit()
        flash("A new game is created!")
        return redirect(url_for('showGames'))
    else:
        return render_template('newGame.html', game=game)


@app.route('/games/<int:game_id>/edit/', methods=['GET', 'POST'])
@login_required
def modGame(game_id):
    modGame = session.query(GameGenre).filter_by(id=game_id).one()
    game = session.query(GameGenre).filter_by(id=game_id).one()
    mad = getUserInfo(modGame.user_id)

    if 'username' not in login_session:
        flash(" Not permitted, this belongs to admin")
        return redirect(url_for('showGames'))

    if request.method == 'POST':
        if request.form['name']:
            modGame.name = request.form['name']
        session.add(modGame)
        session.commit()
        flash("A new Game is edited")
        return redirect(url_for('showGames'))

    elif mad.id != login_session['user_id']:
        flash('permission denied, Contact Admin !! ')
        return redirect(url_for('showGames'))
    else:
        return render_template('modGame.html', game=modGame, game_id=game_id)


@app.route('/games/<int:game_id>/del/', methods=['GET', 'POST'])
@login_required
def delGame(game_id):
    gameToDel = session.query(GameGenre).filter_by(id=game_id).one()
    mad = getUserInfo(gameToDel.user_id)
    user = getUserInfo(login_session['user_id'])

    if 'username' not in login_session:
        flash(" This belongs to admin!!")
        return redirect(url_for('showGames'))

    if request.method == 'POST':
        session.delete(gameToDel)
        session.commit()
        flash('A game is deleted !')
        return redirect(url_for('showGames'))
    elif mad.id != login_session['user_id']:
        flash('permission denied, Contact Admin')
        return redirect(url_for('showGames'))
    else:
        return render_template('delGame.html', game=gameToDel)


@app.route('/games/<int:game_id>/')
def game_Menu(game_id):
    game = session.query(GameGenre).filter_by(id=game_id).one()
    list = session.query(ListGame).filter_by(game_id=game.id)
    return render_template('menu.html', game=game, list=list)


@app.route('/games/<int:game_id>/new/', methods=['GET', 'POST'])
@login_required
def createGameList(game_id):
    game = session.query(GameGenre).filter_by(id=game_id).one()
    user = getUserInfo(game.user_id)
    if 'username' not in login_session:
        return redirect(url_for('game_Menu', game_id=game_id))
    if request.method == 'POST':
        nuList = ListGame(name=request.form['name'],
                          description=request.form['Description'],
                          price=request.form['Price'], game_id=game_id,
                          user_id=login_session['user_id'])
        session.add(nuList)
        session.commit()
        flash("New Game has been added!!")
        return redirect(url_for('game_Menu', game_id=game_id))
    elif user.id != login_session['user_id']:
        flash('permission denied, contact admin')
        return redirect(url_for('game_Menu', game_id=game_id))
    else:
        return render_template('nugamelist.html', game_id=game_id)


@app.route('/games/<int:game_id>/<int:list_id>/edit/', methods=['GET', 'POST'])
@login_required
def editGameList(game_id, list_id):
    editList = session.query(ListGame).filter_by(id=list_id).one()
    mad = getUserInfo(editList.user_id)
    user = getUserInfo(login_session['user_id'])

    if 'username' not in login_session:
        return redirect('game_Menu', game_id=game_id)
    if request.method == 'POST':
        if request.form['name']:
            editList.name = request.form['name']
        if request.form['description']:
            editList.description = request.form['description']
        if request.form['price']:
            editList.price = request.form['price']
        session.add(editList)
        session.commit()
        flash("Menu item has been modified")
        return redirect(url_for('game_Menu', game_id=game_id))

    elif mad.id != login_session['user_id']:
        flash('permission denied, Contact Admin')
        return redirect(url_for('game_Menu', game_id=game_id))
    else:
        return render_template('chggamelist.html', game_id=game_id,
                               list_id=list_id, list=editList)


@app.route('/games/<int:game_id>/<int:list_id>/del/', methods=['GET', 'POST'])
@login_required
def delGameList(game_id, list_id):

    dellist = session.query(ListGame).filter_by(id=list_id).one()
    mad = getUserInfo(dellist.user_id)
    user = getUserInfo(login_session['user_id'])
    if 'username' not in login_session:
        return redirect(url_for('game_Menu', game_id=game_id))
    if request.method == 'POST':
        session.delete(dellist)
        session.commit()
        flash("Menu item deleted")
        return redirect(url_for('game_Menu', game_id=game_id))
    elif mad.id != login_session['user_id']:
        flash('permission denied contact admin')
        return redirect(url_for('game_Menu', game_id=game_id))
    else:
        return render_template('dellist.html', list=dellist)

if __name__ == '__main__':
    app.secret_key = 'super-secret'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
