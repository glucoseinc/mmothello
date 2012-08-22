from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, jsonify, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from contextlib import closing

import json
import board_class
import conf

import hashlib
import base64
import urllib
import hmac
import urlparse
import random

from crontab import CronTab
import datetime
import time
import threading


"""
Structure

# CONFIGURATION BLOCK #
This block consists of constants used throughout the code.

# DATABASE CLASSES #
These are the classes for the SQLAlchemy Database. Currently we have:
- Boards
- Users
- Votes
- Voted # this one keeps track of each users votes in each game.
- TestUsers
- Guilds (not used)
- Guild Members (not used)

# FACEBOOK BLOCK #
These are the interface functions that deal with the communication with
the facebook GRAPH api. most of these functions uses urllib to make requests.

# VIEW FUNCTION BLOCK #
View functions. These functions are what flask connects the URL's with the different templates. Most of the game logic and facebook functions are called from index(). This function should maybe be broken down further??
Functinos to be moved: end_vote, add_round_score, add_final_score, create_board, and should be moved to GAME LOGIC FUNCTIONS

# GAME LOGIC FUNCTIONS #
Game Logic functions that primarily deals with voting. 


"""



# configuration

DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

VOTE_LIMIT = 2

# POINT VARIABLES

START_BONUS = 0.8
PER_MEMBER_BONUS = 0.02

REWARD = 10
DECAY = 0.8

FEVER_LEVEL_1 = 50
FEVER_LEVEL_2 = 70
FEVER_LEVEL_3 = 80
FEVER_LEVEL_4 = 90

DEFAULT_VOTE_TIMER = 1200

# Other variables.

timers = {}


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+oursql://ikee:mypass@localhost/fothello'

db = SQLAlchemy(app)

class Boards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(100))
    board = db.Column(db.String(250))
    current_turn = db.Column(db.String(1)) # sort of obsolite
    current_color = db.Column(db.Integer)
    fever_team_1 = db.Column(db.Integer)
    fever_team_2 = db.Column(db.Integer)

    # leader_team_1 = db.Column(db.Integer, db.ForeignKey('users.id'))
    # leader_team_2 = db.Column(db.Integer, db.ForeignKey('users.id'))

    game_state = db.Column(db.Boolean)
    time_left = db.Column(db.Integer)
    turn_duration = db.Column(db.Integer)

    def __init__(self, board, 
                 current_turn, 
                 current_color, 
                 game_state):
        self.board = board
        self.current_turn = current_turn
        self.current_color = current_color
        self.game_state = game_state
        self.fever_team_1 = 10
        self.fever_team_2 = 10

    def __repr__(self):
        return '<Boards %s and board is: %s>' % (str(self.id), self.board)
    
    @classmethod
    def create_from_board_data(self,board_data):
        return Boards(json.dumps(board_data.get("board")), board_data.get("current_turn"), board_data.get("current_color"), board_data.get("game_state"))


    @classmethod
    def get_board_data(self):
        board = board_class.Board()
        board.load_board(json.loads(self.board),
                         self.current_turn,
                         self.current_color,
                         self.game_state)
        return board.get_board_data()

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    votes = db.Column(db.Integer)
    x_coordinate = db.Column(db.Integer)
    y_coordinate = db.Column(db.Integer)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'))    

    def __init__(self, votes, x_coordinate,y_coordinate, board_id):
        self.votes = votes
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.board_id = board_id
        
    def __repr__(self):
        return '<Votes for board %r>' % self.board_id

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facebook_id = db.Column(db.String(30))
    name = db.Column(db.String(30))
    score = db.Column(db.Integer)
    
    def __init__(self, facebook_id, name):
        self.name = name
        self.facebook_id = facebook_id
        self.score = 0

    def __repr__(self):
        return '<Users %r>' % self.name

class Voted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer)
    user_id = db.Column(db.String(30))
    has_voted = db.Column(db.Boolean)
    team = db.Column(db.Integer) # 1 for red, 2 for blue
    vote_id = db.Column(db.Integer) # vote id
    game_score = db.Column(db.Integer)

    def __init__(self, board_id, user_id, team):
        self.board_id = board_id
        self.user_id = user_id
        self.has_voted = False
        self.team = team
        self.vote_id = None
        self.game_score = 0;

    def __repr__(self):
        return '<Voted user %r>' % str(self.user_id) + ' board ' + str(self.board_id)

        
# class Guilds(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # guild_name = db.Column(db.String(20))
    # guild_master_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # score = db.Column(db.Integer)

    # def __init__(self, guild_name, guild_master_id):
        # self.guild_name = guild_name
        # self.guild_master_id = guild_master_id
        # score = 800;

    # def __repr__(self):
        # return '<Guilds guild: %r>' % self.guild_name + " GM: " + str(self.guild_master_id) 

# class Guildmembers(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # guild = db.Column(db.Integer, db.ForeignKey('guilds.id'))
    # member = db.Column(db.Integer, db.ForeignKey('users.id'))
    # protector = db.Column(db.Boolean(False))

    # def __init__(self, guild, member, protector=""):
        # self.guild = guild
        # self.member = member
        # if not protector == "":
            # self.protector = protector

    # def __repr__(self):
        # return '<Guildmembers guild: %r>' % self.guild + " user: " + str(self.member)
        
        
class Testusers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_user_id = db.Column(db.String(50))
    full_name = db.Column(db.String(50))
    installed = db.Column(db.String(10))
    permissions = db.Column(db.String(200))
    access_token = db.Column(db.String(150))
    login_url = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(40))

    def __init__(self, test_user_id, full_name,installed, permissions, access_token, login_url, email, password):
        self.test_user_id = test_user_id
        self.full_name = full_name
        self.installed = installed
        self.permissions = permissions
        self.access_token = access_token
        self.login_url = login_url
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Testusers test_user_id %r>' % self.test_user_id
 
    

  
    
# these are hard coded for now... =/

color_X = 1 # X's color!
color_O = 2 # O's color!   

# HELPER CLASSES


class VoteTimer(threading.Thread):
    def __init__(self,board_id,turn_duration = DEFAULT_VOTE_TIMER):
        
        self.time_left = turn_duration
        self.turn_duration = turn_duration
        self.board_id = board_id
        threading.Thread.__init__(self)
        self.running = True


    def stop(self):
        self.running = False
    
    
    def restart_timer(self):
        # print "theoreticlly, lets display what it woould be if we restarted: "
        
        # show_string =  str(datetime.datetime.now().minute)
        # show_string = show_string + " */" + str(self.duration)
        # show_string = show_string +  " * * *"
        # print show_string


        # print str(datetime.datetime.now().minute) + " * * * *"
         
        self.time_left = self.turn_duration

    def run(self):
        # print "Starting timer, with this boolean: ",self.running
        while self.running:
            time.sleep(1000.0/1000.0)
            # board.time_left = board.time_left -1
            self.time_left = self.time_left -1
            if self.time_left == 0:
                # sleep a second so we don't call end_vote more than once
                # time.sleep(1)
                db.session.remove()
                # print "timer for board " + str(self.board_id) + "is now attempting to shut down voiting! :D"
                _end_vote(self.board_id)
                # print "vote ended due to timer!"
                self.restart_timer()
        print "Now timer ceased to work!"




# **********************************************
# ******* Facebook Interaction Functions *******
# **********************************************


# general functions.

def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

def parse_signed_request(signed_request):
    l = signed_request.split('.', 2)
    encoded_sig = l[0]
    payload = l[1]

    sig = base64_url_decode(encoded_sig)
    data = json.loads(base64_url_decode(payload))

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        log.error('Unknown algorithm')
        return None
    else:
        expected_sig = hmac.new(conf.APP_SECRET, msg=payload, digestmod=hashlib.sha256).digest()
    if not expected_sig == sig:
        return None
    else:
        # print "Valid data recieved!"
        return data


def get_app_access_token():
    url = "https://graph.facebook.com/oauth/access_token?"
    url = url + "client_id=" + str(conf.APP_ID)
    url = url + "&client_secret=" + conf.APP_SECRET
    url = url + "&grant_type=client_credentials" 

    data = urllib.urlopen(url).read()
    
    content = data.split('=')
    conf.APP_ACCESS_TOKEN = content[1]

        
        
def get_user_data(oauth_token):
    # print "starting get_user_data with token: ", oauth_token
    url = "https://graph.facebook.com/me"
    url = url + "?fields=id,name,gender"
    url = url + "&access_token=" + oauth_token
    data = json.load(urllib.urlopen(url))
    if not data.get('id',None) is None:
        user = Users.query.filter_by(facebook_id=data.get('id')).first()
        if user is None: # user does not exist, add user!
            # print "user does not exist, attempting to create user with following data: ", data
            user = Users(data.get('id'), data.get('name'))
            db.session.add(user)
            db.session.commit()
        session['user_id'] = data.get('id')
        session['name'] = data.get('name')
        session['gender'] = data.get('gender')
        session['access_token'] = oauth_token
        board = Boards.query.order_by('-id').first()
        if board is None:
            create_board()
            board = Boards.query.first()
        
            # print "get_user_data game state: ", board.game_state
            # print "get_user_data - setting board_id to: ", board.id
        

        session['board_id'] = board.id
        
        # old implementation
        # in case user wasn't here when game was created:
        # voted = Voted.query.filter_by(board_id = session['board_id'], 
        #                               user_id = session['user_id']).first()
        # if voted is None:
        #     voted = Voted(board_id = session['board_id'],
        #                   user_id = session['user_id'])
        #     db.session.add(voted)
        #     db.session.commit()
        return data
    return None

    

def check_admin_status():
    url = "https://graph.facebook.com/me/accounts"
    url = url + "?access_token=" + session["access_token"]
    url = url + "&method=get"
    data = json.load(urllib.urlopen(url)).get('data')
    for application in data:
        if application.get('id') == conf.APP_ID:
            return True

    return False

    
    
# Request functions.    

def read_app_request(user_facebook_id, user_access_token):

    print "reading app request..."

    url = "https://graph.facebook.com/"
    url = url + str(user_facebook_id) + "/"
    url = url + "apprequests"
    url = url + "?access_token=" + user_access_token

    data = json.load(urllib.urlopen(url))

    print data.get('data')
    
    return data

def delete_all_app_request(app_request_data):

    for data in app_request_data.get('data'):
        request_id = data.get('id')
        print "deleting request with id ", request_id
        delete_app_request(request_id)

def delete_app_request(request_id):

    print "deleting app request nr: ", request_id
    
    url = "https://graph.facebook.com/"
    url = url + request_id + "/"
    url = url + "?access_token=" + conf.APP_ACCESS_TOKEN    
    url = url + "&method=delete"

    data = json.load(urllib.urlopen(url))

    print data

    
# Test user functions.

def create_test_user(installed, full_name, permissions):
    print "creating test_user..."

    url = "https://graph.facebook.com/"
    url = url + str(conf.APP_ID) + "/"
    url = url + "accounts/test-users?"
    url = url + "installed="+installed
    url = url + "&name=" + full_name
    url = url + "&permissions=" + permissions
    url = url + "&locale=en_US"
    url = url + "&method=post"
    url = url + "&access_token=" + conf.APP_ACCESS_TOKEN

    data = json.load(urllib.urlopen(url))
    
    print data

    if not data.get('id',None) is None:
        print "test_user created successfully!"
        test_user = Testusers(data.get('id'), 
                              full_name,
                              installed,
                              permissions,
                              data.get('access_token'), 
                              data.get('login_url'), 
                              data.get('email'), 
                              data.get('password'))
        db.session.add(test_user)
        db.session.commit()
    else:
        print "unable to create test_user", data


def access_all_test_users():
    url = "https://graph.facebook.com/APP_ID/accounts/test-users?"
    url = url + "access_token="
    url = url + conf.APP_ACCESS_TOKEN
    response = json.load(urllib.urlopen(url))
    print response
    for row in response.get('data'):
        print row



def delete_test_user(test_user_id):
    url = "https://graph.facebook.com/" + test_user_id  + "?"
    url = url + "method=delete"
    url = url + "&access_token=" + conf.APP_ACCESS_TOKEN
    data = json.load(urllib.urlopen(url))
    test_user = Testusers.query.filter_by(test_user_id = test_user_id).first()
    print "test_user is now: ", test_user
    if not test_user is None:
        db.session.delete(test_user)
        db.session.commit()
        print "deletion from datatable was complete"
    print "deletion of testuser was: ", data

def delete_all_test_users():
    print "trying to access all test users!"
    url = "https://graph.facebook.com/" + conf.APP_ID
    url = url + "/accounts/test-users?"
    url = url + "access_token=" + conf.APP_ACCESS_TOKEN
    data = json.load(urllib.urlopen(url)).get('data')
    print "data for accessed test users are the following: ", data
    
    # access and delete them all from table, and delete them from facebook.

    for user_data in data:
        delete_test_user(user_data.get('id'))
        user = Testusers.query.all()


def setup_test_users():
    print "setting up test users..."
    data = [{'installed': "true",
             'full_name': "lisa",
             'permissions': ""},
            {'installed': "true",
             'full_name': "Arnold",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Fittoussy",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Laban",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Gorli",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Kyoko",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Misa",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Minato",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Shinji",
             'permissions': ""},

            {'installed': "true",
             'full_name': "Kenshin",
             'permissions': ""}
            ]
    for user_data in data:
        create_test_user(user_data.get('installed'), 
                         user_data.get('full_name'), 
                         user_data.get('permissions'))


def setup_friend_connections():
    test_users = Testusers.query.all()
    user1 = test_users.pop()
    for userx in test_users:
        friend_connection(user1, userx)

def friend_connection(test_user1, test_user2):
    # send request to user2
    url1 = "https://graph.facebook.com/" + test_user1.test_user_id
    url1 = url1 + "/friends/"
    url1 = url1 + test_user2.test_user_id + "?"
    url1 = url1 + "method=post"
    url1 = url1 + "&access_token=" + test_user1.access_token
    
    response1 = json.load(urllib.urlopen(url1))
    
    print url1
    print "sending friends request to " + test_user2.full_name
    print "... sending was", response1
    
    # user1 accept the friendship request
    url2 = "https://graph.facebook.com/" + test_user2.test_user_id
    url2 = url2 + "/friends/"
    url2 = url2 + test_user1.test_user_id + "?"
    url2 = url2 + "method=post"
    url2 = url2 + "&access_token=" + test_user2.access_token

    response2 = json.load(urllib.urlopen(url2))
    print url2
    print "accepting friends request from " + test_user1.full_name
    print "... acceptence was ", response2    


# *************************************
# ********** view functions ***********
# *************************************



# **********************
#       tear down
#***********************

# This ensures that we have a new session per request (important
# for timers (thread issue).
@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


# Implemented but not used functions. Kept for future reference.
# Used connected to buttons during development.

@app.route('/board_management/')
def board_management():

    if not check_admin_status():
        return make_response(render_template('error.html', message="you tried to access an admin page when you are not an admin :("))
    boards = Boards.query.all()
    return make_response(render_template('board_management.html', boards=boards))


@app.route('/delete_current_board/')
def delete_current_board():
    board = Boards.query.filter_by(id = session['board_id']).first()

    db.session.delete(board)
    db.session.commit()
    boards = Boards.query.all()
    return make_response(render_template('game_page.html', name=session['name'], message="now I'm not sure what is to be here..."))
                         

@app.route('/delete_board/<board_id>')
def delete_board(board_id):
    if not check_admin_status():
        return make_response(render_template('error.html', message="You tried to act like an admin!"))


    board = Boards.query.filter_by(id = board_id).first()
    db.session.delete(board)
    db.session.commit()
    boards = Boards.query.all()
    return make_response(render_template('board_management.html', boards=boards))


@app.route('/end_vote/')
def end_vote():

    admin_status = check_admin_status()
    if not admin_status:
        return make_response(render_template('error.html', message="You tried \
to pretend to be an Admin!"))

    _end_vote()
    
    return make_response(render_template('game_page.html',
                                         name=session['name'],
                                         message="it's your turn!",
                                         admin=admin_status))



# **************************************
# ##### Implemented View Functions #####
# **************************************

# First some helpers, that should be moved.


def _end_vote(board_id=None):
    if board_id is None:
        board_id = session['board_id']
    print "ending vote prematurely..."

    board = Boards.query.filter_by(id = board_id).first()

    # print board.id

    votes1 = Votes.query.filter_by(board_id = board_id).order_by('-votes').first()

    if votes1 is not None:
        # print "we are trying to get votes from board ", board_id
        # print "first round of votes are: ", votes1
        # print "it has this many votes: ", votes1.votes

        if not votes1.votes == 0:

            votes2 = Votes.query.filter_by(board_id = board_id, 
                                           votes = votes1.votes).all()


            # votes2 are all votes who has the highest amount of votes. right now
            # if there are more than 1 votes, pick one at random.
            
            # print votes2

            votes2_length = len(votes2)
            
            index = random.choice(range(votes2_length));
            
            # print index
            
        # index is a random index of the possible votes we have

            game_state = _place_tile(board_id,
                                     votes2[index].x_coordinate, 
                                     votes2[index].y_coordinate)

        
            if not game_state:
                print "end_vote: game is over, stopping timer!"
                # send end game notifications??
                _add_final_score(board_id)
                timers[board_id].stop()
            else:
                vote_id = votes2[index].id # for clarity
                #_add_round_score(board_id, vote_id)
                _send_end_turn_reminders(board_id)
                timers[board_id].restart_timer()
        else:
            # print "Noone has voted yet :( restarting timer..."
            timers[board_id].restart_timer()



# data = board.get_board_data()
# _delete_all_votes(db, board_id)
# _create_votes(db, data.get('helper_moves'),board_id)

# db.session.commit()
            
# boards = Boards.query.all()



        # timers[board_id].restart_timer()
    else:
        print "end_vote: error- can't find votes for board  ", board_id
        print "attempting to stop timer, can't find any votes in game :("
        timers[board_id].stop()

def _add_round_score(board_id, vote_id):
    # this function must be ran before board is updated in _move.
    # alternative solution is to check for TEAM =! CURRENT_COLOR,
    # but then we have to run it after we update board...

    board = Boards.query.filter_by(id = board_id).first()
    print "CALLING ADD ROUND SCORE! :DDD"

    vote = Votes.query.filter_by(id = vote_id).first()

    for voted in Voted.query.filter_by(board_id = board_id,
                                       team = board.current_color,
                                       has_voted = True,
                                       vote_id = vote_id).all():
        # vote = Votes.query.filter_by(id = voted.vote_id).first()
        print "voted.facebook_id is: ", voted.user_id
        print "voted.game_score is before assignment: ", voted.game_score
        # print "vote_id is: ", voted.vote_id
        print "number of votes is: ", vote.votes
        voted.game_score = voted.game_score + vote.votes
        print "voted.game_score is after assignment: ", voted.game_score

    team_members = Voted.query.filter_by(board_id = board_id,
                                          team = board.current_color).count()
    percent = float(vote.votes) / float(team_members);
    bonus = START_BONUS + PER_MEMBER_BONUS*team_members
    total_modifier = (REWARD * percent * bonus)


    if board.current_color == 1:
        board.fever_team_1 = int(board.fever_team_1*DECAY + total_modifier)
    else:
        board.fever_team_2 = int(board.fever_team_2*DECAY + total_modifier)

    db.session.commit()


def _add_final_score(board_id):
    print "called add_final_score!!!!"

    board = Boards.query.filter_by(id = board_id).first()

    board_list = json.loads(board.board)

    red_score = 0; # team 1

    blue_score = 0; # team 2

    for row in board_list:
        red_score = red_score + row.count(1)
        blue_score = blue_score + row.count(2)
    

    total_score = red_score + blue_score

    # team 1:

    red_factor = 2.0*float(red_score)/float(total_score)-0.5
    blue_factor = 2.0*float(blue_score)/float(total_score) - 0.5


    for voted in Voted.query.filter_by(board_id = board_id,
                                       team=1).all():
        print Users.query.all()
        print voted
        user = Users.query.filter_by(facebook_id = voted.user_id).first()
        user.score = user.score + voted.game_score*red_factor



    for voted in Voted.query.filter_by(board_id = board_id,
                                       team=2).all():
        print Users.query.all()
        print voted
        user = Users.query.filter_by(facebook_id = voted.user_id).first()
        user.score = user.score + int(voted.game_score * blue_factor)




    db.session.commit()



def _send_end_turn_reminders(board_id):
    board = Boards.query.filter_by(id = board_id).first()
    voted = Voted.query.filter_by(board_id = board_id,
                                  team = board.current_color).all()

    for row in voted:
        reminder = _end_turn_reminder(row.user_id)



def _end_turn_reminder(user_id):
    url = "https://graph.facebook.com/" + user_id  +"/apprequests"
    url = url + "?message=A new turn has started in the match ... vs ..., vote for the next move now! :))))"
    # url = url + "&icon=" + url_for('static', filename='reversi_icon.png')
    url = url + "&access_token=" + conf.APP_ACCESS_TOKEN
    url = url + "&method=POST"
    print "sending reminder..."
    data = json.load(urllib.urlopen(url))

    print data

    

# View function for deleting test_users. Used in test_user interface.



@app.route('/test_users/<test_user_id>')
def _delete_test_user(test_user_id):
    delete_test_user(test_user_id)
    return make_response(redirect(url_for('test_user_page')))
    

@app.route('/test_users/', methods=['GET','POST'])
def test_user_page():
    print "trying to access test_user_page!"
    # if not check_admin_status():
    #    return make_response(render_template("error.html", message="you tried to access admin pages when you are not admin :("))
    if request.method == 'POST': # we got a request to craete a user!
        if request.form['command'] == "delete_all":
            delete_all_test_users()
        elif request.form['command'] == "access_all":
            access_all_test_users()
        elif request.form['command'] == "create_all":
            setup_test_users()
        elif request.form['command'] == "setup_friends":
            setup_friend_connections()
        else:
            create_test_user(request.form['installed'], 
                             request.form['full_name'], 
                             request.form['permissions'])
    else:
        # get_app_access_token()
        # create_test_user(installed,fullname,permissions)
        # create_test_user("true","Sarah Kerrigen","")
        # delete_all_test_users()
        pass
    data = Testusers.query.all()
    # print data
    return render_template('test_users.html', data = data)


@app.route('/_add_to_team/<team>')
def add_to_team(team):
    print "TROLL ADD TO TEAM!"
    data = {}
    if team == "blue":
        data["team"] = "blue"
        voted = Voted(session['board_id'], session['user_id'], 2)
        db.session.add(voted)
        db.session.commit()
    else:
        data["team"] = "red"
        voted = Voted(session['board_id'], session['user_id'], 1)
        db.session.add(voted)
        db.session.commit()

    return json.dumps(data)

@app.route('/send_request/')
def send_request():
    print "spamming ikshu! :D"

    user = Users.query.filter_by(name=session['name']).first()

    url = "https://graph.facebook.com/" + user.facebook_id  +"/apprequests"
    url = url + "?message=" + session['name'] + " is the undefeated champion in Mockello! Can you beat him/her??"
    url = url + "&icon=" + url_for('static', filename='reversi_icon.png')
    url = url + "&access_token=" + conf.APP_ACCESS_TOKEN
    url = url + "&method=POST"


    data = json.load(urllib.urlopen(url))
    
    print data
    

    return make_response(render_template('game_page.html',
                                         name=session['name'],
                                         message="sneaky!",
                                         admin=False))



@app.route('/index/', methods=['GET','POST'])
def index_page():
    if request.method == 'POST':
        if request.form.get('signed_request') is not None:
            data = parse_signed_request(request.form.get('signed_request'))
        else:
            data = None
        # print data
        if data is None:
            print "We got faulty data!"
            return make_response(render_template('error.html', error_message="The authurization process has been tampe\
red with, please contact the application developers or facebook."))
            
        # print "POST-method recieved"
        if data.get('user_id', None) is None:
            # print "the user hasn't authurized the app yet, redirecting..."


            url = "https://www.facebook.com/dialog/oauth/"
            url = url + "?client_id=" + str(conf.APP_ID)
            url = url + "&redirect_uri=" + str(conf.APP_URI)


            return make_response(render_template('redirect.html', url=url))

        # autherized user!

        # print "the user has autherized us"
        oauth_token = data.get('oauth_token',None)

        # In case user has autherized us, but havn't visited the page yet,
        # Get users data from facebook server again!
        if not oauth_token is None:
            content = get_user_data(data.get('oauth_token'))
            ## return make_response(
            ##     render_template('select_team_page.html',
            ##                     name = session['name'],
            ##                     team = "both"))

            # If user id exists, we go on!
            if not content.get('id',None) is None:
                
                boards = Boards.query.all()
                board = Boards.query.order_by('-id').first();
                # print "index - board_id is now set to: ", board.id
                # print "index game state: ", board.game_state
                session['board_id'] = board.id;
                

                app_request_data = read_app_request(session['user_id'],
                                                    session['access_token'])


                # DO STUFF WITH DATA HERE!

                # for example, if there is a request to X from Y, create
                # a new game where they are the main players.


                # /DO STUFF WITH DATA HERE!

                delete_all_app_request(app_request_data)

                
                # print request.form.get('signed_request')
                print "connected to new index page!"
                return make_response(render_template('index_page.html'))

    elif request.method == "GET":
        print request.form.get('signed_request')
        print "connected to new index page!"
        return make_response(render_template('index_page.html'))




@app.route('/app/', methods=['GET','POST'])
def index():
    # print "we just got a facebook connection!"
    if request.method == 'POST' or request.method == 'GET': #ugly hax, need to access page!
        if request.form.get('signed_request') is not None:
            data = parse_signed_request(request.form.get('signed_request'))
        else:
            data = None
        # print data
        if data is None:
            print "We got faulty data!"
            return make_response(render_template('error.html', error_message="The authurization process has been tampered with, please contact the application developers or facebook."))
        
        # print "POST-method recieved"
        if data.get('user_id', None) is None:
            # print "the user hasn't authurized the app yet, redirecting..."
            url = "https://www.facebook.com/dialog/oauth/"
            url = url + "?client_id=" + str(conf.APP_ID)
            url = url + "&redirect_uri=" + str(conf.APP_URI)
            
            return make_response(render_template('redirect.html', url=url))

        # autherized user!
        
        # print "the user has autherized us"
        oauth_token = data.get('oauth_token',None)
        
        # In case user has autherized us, but havn't visited the page yet,
        # Get users data from facebook server again!
        if not oauth_token is None:
            content = get_user_data(data.get('oauth_token'))
            #### searchtag bajs ####
            ## return make_response(
            ##     render_template('select_team_page.html',
            ##                     name = session['name'],
            ##                     team = "both"))
        
            # If user id exists, we go on!
            if not content.get('id',None) is None:
                boards = Boards.query.all()
                board = Boards.query.order_by('-id').first();
                # print "index - board_id is now set to: ", board.id
                # print "index game state: ", board.game_state
                session['board_id'] = board.id;
                
                if check_admin_status():
                    print "USER IS ADMIN LOL!"
                    admin_status = True;
                    # return make_response(render_template('admin.html', name=content.get('name'), boards=boards)) 


                else:
                    # print "User is just a regular booring person... :("
                    admin_status = False;
                # print "content is: ", content
                # print "user name is: ",  content.get('name');
                # print "user gender is: ", content.get('gender');

                # print "board id: ", session['board_id']
                # print "user_id: ", session['user_id']

                # return make_response(
                #     render_template('start_page.html', 
                #                     name=content.get('name'),
                #                     gender=content.get('gender'), 
                #                     boards=boards))

                voted = Voted.query.filter_by(board_id = session['board_id'],
                                              user_id = session['user_id']).first()
                if voted is None:
                    # voted = Voted(session['board_id'],session['user_id'])
                    # db.session.add(voted)
                    # db.session.commit()
                    blue = 0
                    red = 0
                    for voted in Voted.query.filter_by(board_id = session['board_id']).all():
                        if voted.team == 1:
                            red = red + 1
                        elif voted.team == 2:
                            blue = blue + 1

                    print "blue: ", blue
                    print "red: ", red


                    if blue == 0 or blue < red*3/4:
                        pickable_team = "blue"
                        print "choosable team is blue!"
                    elif red == 0 or red < blue*3/4:
                        pickable_team = "red"
                        print "choosable team is red!"
                    else:
                        pickable_team = "both"
                        print "both teams are available!"
                    return make_response(
                        render_template('select_team_page.html',
                                        name = session['name'],
                                        team = pickable_team))

                turn = voted.team == board.current_color
                voted = not voted.has_voted

                # print "current board is: ", session['board_id'] 
                return make_response(render_template('game_page.html', 
                                                     name=content.get('name'),
                                                     turn=turn,
                                                     voted=voted,
                                                     admin=admin_status))
            

            # error
            else:
                return make_response(render_template('error.html', error_message = "We couldn't verify your data, please try logging out and in again :("))
        
        # We SHOULD NOT get here, but in case something goes wrong,
        # show the user an error message instead of a 404.
        else:
            return make_response(render_template('error.html', error_message = "Ehm... We are not really sure what happened, but something went wrong during authentification :/ Try to reinstall the app, go to account-> settings -> app, remove the app and visit this place again! We are sorry for the inconvience!"))

    else:
        print "We didn't get a POST... :("
        return make_response(render_template('lobby_base.html'))



@app.route('/create_guild')
def create_guild_page():
    # reroute to create guild page! :) Here we assume that the user is logged in! 
    return make_response(render_template('create_guild.html'))

@app.route('/save_guild', methods=['POST'])
def save_guild():
    # print Users.query.all()
    # print session
    # guild = Guilds(request.form['name'], session.get('id'))
    # db.session.add(guild)
    # db.session.commit()
    return make_response(render_template('start_page.html'))


def create_board(time = DEFAULT_VOTE_TIMER):
    board_ = board_class.Board()
    board_data = board_.get_board_data()
    board = Boards.create_from_board_data(board_data)
    board.time_left = time
    board.turn_duration = time
    db.session.add(board)
    db.session.commit()
    board = Boards.query.order_by('-id').first()
    session['board_id']=board.id
    # print "create_board: setting board_id to: ", board.id
    _create_votes(db,board_data.get('helper_moves'),
                  board.id)

    # for user in Users.query.all():
    #     voted = Voted(board.id, user.facebook_id)
    #     db.session.add(voted)

    db.session.commit()


    # print "craete board: board_id: ", board.id

    timers[board.id] = VoteTimer(board.id)
    timers[board.id].start()
    # print "craete_board: timers: ", timers
    session['board_id'] = board.id

@app.route('/_create_new_board')
def _create_new_board():
    # print "connected to server, attempting to create new board!"
    # print "first removing old timer..."
    # print "timers are: ", timers
    # print "board_id is: ", session['board_id']
    timers[session['board_id']].stop()
    create_board();
    # print "created new board!"
    return make_response(render_template('game_page.html', 
                                         name=session['name'], 
                                         message="now I'm not sure..."))
    
@app.route('/_load_board/')    
def _load_board() :
    # print "loading board..."
    # id = request.args.get('id', 1)
    # print session
    id = session['board_id']
    # print "attempting to load board number: ", id
    data = Boards.query.filter_by(id=id).first()
    if data is None:
        return make_response(render_template('error.html', message = "The game was not found, it might have been deleted!"))
    
    #### print "Load_board game state: ", data.game_state

    board_ = board_class.Board()
    board_.load_board(json.loads(data.board), 
                      data.current_turn , 
                      data.current_color, 
                      data.game_state)
    
    board_data = board_.get_board_data()
    voted = Voted.query.filter_by(user_id = session['user_id'],
                                  board_id = session['board_id']).first();
    

    # shoudln't be needed here, but it was bugging!
    if voted is None:
         return make_response(render_template('error.html', message="It appears you have a faulty session, please restart your browser :("))


    if timers.get(session['board_id']) is None:
        timers[session['board_id']] = VoteTimer(session['board_id'])
        timers[session['board_id']].start()


    # Check if player has voted
    has_voted = voted.has_voted

    # check if players turn!
    players_turn = (board_data.get('current_color') == voted.team)

    # OR it is other teams turn and they are in fever mode! :D
    # players_turn = players_turn || FEVER_LEVEL_3 < 

    players_turn = players_turn and board_data.get('game_state')
    # if game is over, it is not players turn!



    # print "debug 2.1, current color:  ", board_data.get('current_color')
    # print "debug 2.2, player team:  ", voted.team


    # print "debug3, ", players_turn




    # get the scores:

    total_score = voted.game_score

    if voted.vote_id is not None and voted.has_voted:
        vote = Votes.query.filter_by(id = voted.vote_id).first()
        round_score = vote.votes
    else:
        round_score = 0;

        ## searchtag slicka
    if voted.team == 1:
        self_fever_points = data.fever_team_1
        enemy_fever_points = data.fever_team_2
    else:        
        self_fever_points = data.fever_team_2
        enemy_fever_points = data.fever_team_1




    # print "game state is currently: ", data.game_state

    board = json.dumps({"id":data.id,
                        "board": board_data.get('board'),
                        "o_score":board_data.get('o_score'),
                        "x_score":board_data.get('x_score'), 
                        "current_turn":board_data.get('current_turn'), 
                        "current_color":board_data.get('current_color'),
                        "helper_moves": _cast_votes_to_helper_moves(db, id),
                        "game_state":board_data.get('game_state'),
                        "players_turn":players_turn,
                        "has_voted":has_voted,
                        "round_score":round_score,
                        "total_score": total_score,
                        "self_fever_points": self_fever_points,
                        "enemy_fever_points": enemy_fever_points,})
    data2 = board

    board_data['id'] = data.id
    # data2['players_turn'] = players_turn

    return data2
    


@app.route('/challenge/')
def challenge():

    url = "https://www.facebook.com/dialog/apprequests?"
    url = url + "app_id=" + conf.APP_ID + "&"
    url = url + "message=" + message + "&"
    url = url + "max_recipients=1&"
    url = url + "redirect_uri=" + conf.APP_URI




@app.route('/instructions/', methods=['POST','GET'])
def show_instructions():
    if request.method=="POST":
        print "WE GOT INSTRUCTION POST!"
    else:
        print "WE GOT INSTRUCTION GET!"
    

    return make_response(render_template('instructions_page.html'))



@app.route('/show_game_list/', methods=['POST','GET'])
def show_game_list():
    voted = Voted.query.filter_by(user_id = session['user_id']).all()
    return make_response(render_template('game_list.html'))

    
@app.route('/show_game/<game_id>')
def show_game(game_id):
    return make_response(render_template('error.html', message="you tried to access an unimplemented page!"))


# is actually our old index, this one contains the game!
@app.route('/show_game/', methods=['POST','GET'])
def show_game():

    if request.method=="GET":
        make_response(render_template('error.html',message="you tried to access teh page outside of facebook, didn't you...?"))

    # check if current game is active, if not, create new game!
    board = Boards.query.filter_by(id = session['board_id']).first()
    # long if to prevent checking a None board's game_state.
    if board is None or (board is not None and not board.game_state):
        # sets session['board_id'] appropriatily
        print "game is over, or no boards exists, create new one!"
        create_board()
    

    voted = Voted.query.filter_by(board_id = session['board_id'],
                                  user_id = session['user_id']).first()
    if voted is None:
        # voted = Voted(session['board_id'],session['user_id'])
        # db.session.add(voted)
        # db.session.commit()
        blue = 0
        red = 0
        for voted in Voted.query.filter_by(board_id = session['board_id']).all():
            if voted.team == 1:
                red = red + 1
            elif voted.team == 2:
                blue = blue + 1
                
        print "blue: ", blue
        print "red: ", red
                
        
        if blue == 0 or blue < red/2:
            pickable_team = "blue"
            print "choosable team is blue!"
        elif red == 0 or red < blue/2:
            pickable_team = "red"
            print "choosable team is red!"
        else:
            pickable_team = "both"
            print "both teams are available!"
        return make_response(render_template('select_team_page.html',
                                             name = session['name'],
                                             team = pickable_team))
    
    # turn = voted.team == board.current_color
    voted = not voted.has_voted
                
                # print "current board is: ", session['board_id']
    return make_response(render_template('game_page2.html',
                                         name=session['name'],
                                         turn=False,
                                         voted=voted,
                                         admin=False))



@app.route('/_move')    
def _move():
    #function to move stuff!
    
    print "now attempting to move!"
    
    # id = request.args.get('id', 1)
    id = session['board_id']
    x_coordinate = request.args.get('x_coordinate',-1)
    y_coordinate = request.args.get('y_coordinate',-1)
    
    voted = Voted.query.filter_by(board_id = session['board_id'],
                                  user_id = session['user_id']).first()

    # we will not generate the clickable surface if not players turn
    # so this is a bit redundant to check for this before. This is also
    # why we later don't check for if players turn matches the 
    # current turn.

    players_turn = not voted.has_voted
    
    if not players_turn:
        # do nothing, user clicked when it wasn't their turn! :p :)
        data = {} # create empty dict so we can return something.
        print "it is not players turn!!!"
    else:
        # make the vote!    
        
        # if number of votes exceed a certain number (we only have 
        # to check this vote, right? because else we'd already 
        # triggered it!), make the move! BUSTA MOVE!


        print "now going to try to cast a vote!"
        
        enough_votes = _cast_vote(db, x_coordinate, y_coordinate, id) 
        
        
        
    #returns if votes > VOTE_LIMIT
    # and because we just voted, we know that it is not players turn!
        
        
        
        players_turn = False
        
        if enough_votes:
            _end_vote()
            #_place_tile(session['board_id'],  
            #            int(x_coordinate), 
            #            int(y_coordinate))          
            
        else:
            pass;
        # cast helper moves regardless of enough votes or not.
    board_db_data = Boards.query.filter_by(id = id).first()
    board = board_class.Board()
    board.load_board(json.loads(board_db_data.board), 
                     board_db_data.current_turn, 
                     board_db_data.current_color, 
                     board_db_data.game_state)

    data = board.get_board_data()

    data['helper_moves'] = _cast_votes_to_helper_moves(db, id)
        
        
    data['players_turn'] = players_turn
    return json.dumps(data)
    

@app.route('/_reset_board')    
def _reset_board():
    #function to reset the board!
    # id = request.args.get('id', 1)
    id = session['board_id']
    print "attempting to restart server!"
    board = board_class.Board()
    data = board.get_board_data()
    board_data = Boards.query.filter_by(id=id).first()

    board_data.board = json.dumps(data.get('board'))
    board_data.current_turn = data.get('current_turn')
    board_data.current_color = data.get('current_color')
    board_data.game_state = data.get('game_state')
    
    _delete_all_votes(db, id)
    _create_votes(db, data.get('helper_moves'), int(id))
    
    db.session.commit()
    return json.dumps(0)


@app.route('/_check_for_update')
def _check_for_update():
    # print "server spam!", timers
    data = {};
    data['update'] = True;
    return json.dumps(data);


@app.route('/_get_timer/')
def _get_timer():
    # print "getting timer!"
    data = {}
    data['status'] = False
    board = Boards.query.filter_by(id=session['board_id']).first()
    #### print "get_timer game state: ",board.game_state
    if board is not None:
        try:
            # time = board.time_left
            # time = timers[board.id].cron_tab.next()
            if timers[board.id].running:
                time = timers[board.id].time_left
                data['board_id'] = board.id
                data['hours'] = int(time / 3600)
                data['minutes'] = int((time - data['hours']*3600)/60)
                data['seconds'] = int(time - data['hours']*3600)
                data['seconds'] = data['seconds'] - data['minutes']*60
                
            # change status to True
                data['status'] = True
            # print "timer is now: ", board.time_left
            # print "data is now: ", data
        except(KeyError):
            print "key error, it didn't exist :/"
    return json.dumps(data)
    
    
def _create_votes(db, helper_moves, id):
    print "create_votes, helper moves are the following: ", helper_moves
    for move in helper_moves:
        # print "we are creating a vote!"
        vote = Votes(0, move[0], move[1], id)
        db.session.add(vote)
        db.session.commit()

                
def _delete_all_votes(db, id):
    Voted.query.filter_by(board_id = id).update({'has_voted' : False})
    Votes.query.filter_by(board_id = id).delete()
    db.session.commit()
    
def _cast_vote(db, x_coordinate, y_coordinate, id):
    vote = Votes.query.filter_by(board_id = id, 
                                 x_coordinate = x_coordinate, 
                                 y_coordinate = y_coordinate).first();

    # voted will be None if we have not voted yet!
    voted = Voted.query.filter_by(board_id = id,
                                  user_id = session['user_id']).first();
    
    # if vote exists and we have not voted:
    if (vote is not None) and (not voted.has_voted):
        vote.votes = (vote.votes + 1)
        db.session.commit()

        voted.has_voted = True
        voted.vote_id = vote.id
        db.session.commit()
        board = Boards.query.filter_by(id = id).first()
        ## searchtag kiss
        if vote.votes >= Voted.query.filter_by(board_id = id,
                                               team = board.current_color).count():
            return True      
    return False    # will get here if above if statement previous is false.
    
def _cast_votes_to_helper_moves(db, id):
    result = []
    data = Votes.query.filter_by(board_id=id).all()
    # print "cast_votes_to_helper: we got the following data... ", data
    sum = 0;
    for votes in data:
        sum = sum + votes.votes;

    if sum == 0:
        sum = 1 # because all are zero, we divide 0/1 and get 0 :)

    for votes in data:
        result.append([votes.x_coordinate,votes.y_coordinate, float(votes.votes)/float(sum)])
    return result


#def _place_tile(x_coordinate,y_coordinate, board_data):
#    board = board_class.Board()
#    board.load_board(json.load(board_data.board), board_data.current_turn, board_data.current_color)
#    print board


def _place_tile(board_id, x_coordinate, y_coordinate):


    board = board_class.Board()
    board_data = Boards.query.filter_by(id = board_id).first()
    print "Place Tile game state: ", board_data.game_state
    print "_place_tile: board is now: " , board
    print "_place_tile board_data is now: " , board_data
    print json.loads(board_data.board)
    board.load_board(json.loads(board_data.board),
                     board_data.current_turn,
                     board_data.current_color,
                     board_data.game_state)

    
    # must be ran before we update board, else we do ugly hax 
    # in function, and it must be ran after we change board :p
    vote = Votes.query.filter_by(board_id = board_id, 
                                 x_coordinate = x_coordinate, 
                                 y_coordinate = y_coordinate).first();

    _add_round_score(board_id, vote.id)



    board.place_tile(x_coordinate, y_coordinate)

    data = board.get_board_data()
    
    board_data.board = json.dumps(data.get('board'))
    board_data.current_turn = data.get('current_turn')
    board_data.current_color = data.get('current_color')
    board_data.game_state = data.get('game_state')

    db.session.commit()
    
    # board_data = board.get_board_data()
    
    # self.board = json.dump(board_data.get('board'))
    # self.current_turn = board_data.get('current_turn')
    # self.current_color = board_data.get('current_color')
    
    # data = board.get_board_data()




    _delete_all_votes(db, board_id)
    _create_votes(db, data.get('helper_moves'),board_id)

    return board_data.game_state




def _get_session_data(variable_list):
    data = {}
    for data_name in variable_list:
        data[data_name] = session[data_name]
    return data


    
if __name__ == '__main__':
    #app.run(host='10.150.191.231')
    app.run()
