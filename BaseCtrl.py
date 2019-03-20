from flask import Flask, flash, redirect, render_template, request
import os
from flask_sqlalchemy import SQLAlchemy
import json
from base64 import b64encode

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Venu0p@l@localhost/TeamPlayer'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost:3306/teamplayer'
db = SQLAlchemy(app)


class Team(db.Model):
    """docstring for team"""
    __tablename__ = 'team' 
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(80))
    team_image = db.Column(db.LargeBinary)

    def __repr__(self):
        return "<Team(team_name='%s', team_id='%s)>" % (
                                self.team_name, self.team_id)


class Player(db.Model):
    """docstring for Player"""
    __tablename__ = 'player'
    player_id = db.Column(db.Integer, primary_key=True)
    player_fname = db.Column(db.String(80))
    player_lname = db.Column(db.String(80))
    player_image = db.Column(db.LargeBinary)
    team_id = db.Column(db.Integer, db.ForeignKey('team.team_id'))

    def __repr__(self):
        return "<Team(player_fname='%s', player_id='%s, team_id='%s)>" % (
                                self.player_fname, self.player_id, self.team_id)


@app.route('/login')
def home():
    """This method used for display login page"""
    return render_template('login.html')


@app.route('/detail', methods=['POST'])
def do_admin_login():
    """this method used for admin login"""
    if request.form['password'] == 'admin' and request.form['username'] == 'admin':
        teams = get_team()
        if teams:
            return render_template('team-players.html', teams=teams)
        else:
            return render_template('team-players.html')
    else:
        flash('Invalid username or password. Please try again!')
        return render_template('login.html')


@app.route('/teamplayer', methods=['POST'])
def add_team_player():
    """This method used for display add team /player button"""
    if request.form['add_template'] == 'Add Team':
        return render_template('addteam.html')
    elif request.form['add_template'] == 'Add Player':
        teams = get_team()
        return render_template('addplayer.html', teams=teams)
    else:
        return getAllPlayers()


@app.route('/addteam', methods=['POST', 'GET'])
def add_team():
    """This method used for create player record"""
    if request.method == 'POST':
        result = request.form
        teamImage = request.files['teamImage'].read()
        team = Team.query.filter_by(team_name=result['team_name']).first()
        if not team:
            team1 = Team(team_name=result['team_name'], team_image=teamImage)
            db.session.add(team1)
            db.session.commit()
            flash(result['team_name'] + ' is added successfully')
            teams = get_team()
            return render_template('team-players.html', teams=teams)
        else:
            flash(result['team_name'] + ' is already present')
            return render_template('addteam.html')


@app.route('/player_information', methods=['POST', 'GET'])
def player_information():
    """This method used for display team player details"""
    if request.method == 'POST':
        result = request.form
        if request.files:
            playerImage = request.files['playerImage'].read()
        else:
            playerImage = None
        player = Player(player_image=playerImage, player_fname=result['player_first_name'],
                        player_lname=result['player_last_name'], team_id=result['team_selected'])
        db.session.add(player)
        db.session.commit()
        teams = get_team()
        if teams:
            return render_template('team-players.html', teams=teams)
        else:
            return render_template('team-players.html')


def get_team():
    """This method used for get all team information"""
    teams = Team.query.all()
    for each in teams:
        if each.team_image is not None:
            each.team_image = b64encode(each.team_image)
    return teams


@app.route('/edit_team/<int:team_id>', methods=['POST', 'GET', 'PUT'])
def team_edit(team_id):
    """This method used for edit team information"""
    if request.method == 'GET':
        team = Team.query.filter_by(team_id=team_id).one()
        return render_template('edit_team.html', team=team)


@app.route('/update_team', methods=['POST', 'GET'])
def updateteam():
    """This method used for update team information"""
    if request.method == 'POST':
        result = request.form
        teamImage = request.files['teamImage'].read()
        team = Team.query.filter_by(team_id=result.get('team_id')).one()
        team.team_name = result.get('team_name')
        team.team_image = teamImage
        db.session.commit()
        teams = get_team()
        if teams:
            return render_template('team-players.html', teams=teams)


@app.route('/deleteTeam/<int:team_id>', methods=['POST', 'GET'])
def delete_team(team_id):
    """This method used for delete the Team record from database"""
    if request.method == 'GET':
        Team.query.filter_by(team_id=team_id).delete()
        db.session.commit()
        teams = get_team()
        if teams:
            return render_template('team-players.html', teams=teams)
        else:
            return render_template('team-players.html')


@app.route('/display_selected_team/<int:team_id>', methods=['POST', 'GET'])
def display_selected_team(team_id):
    """Display selected team Details"""
    if request.method == 'GET':
        result_dict = {}
        teams = get_team()
        players = Player.query.join(Team, Player.team_id==team_id).\
        add_columns(Player.player_fname,Player.player_lname,Team.team_name,Player.player_id)
        result_dict['teams'] = teams
        result_dict['players']= players
        return render_template('viewplayers.html', result=result_dict)


@app.route('/deletePlayer/<int:player_id>', methods=['POST', 'GET'])
def delete_player(player_id):
    """This method used for delete the player record from database"""
    if request.method == 'GET':
        Player.query.filter_by(player_id=player_id).delete()
        db.session.commit()
        return getAllPlayers()


def getAllPlayers():
    """This method pull all player information from player table"""
    result_dict = {}
    teams = get_team()
    players = db.session.query(Player, Team).join(Team, Player.team_id == Team.team_id)
    for each in players:
        if each.Player.player_image is not None:
            each.Player.player_image = b64encode(each.Player.player_image)
    result_dict['teams'] = teams
    result_dict['players']= players
    return render_template('viewplayers.html', result=result_dict)


@app.route('/edit_player/<int:player_id>', methods=['POST', 'GET'])
def player_edit(player_id):
    """This method used for edit player information"""
    if request.method == 'GET':
        result = {}
        player = Player.query.filter_by(player_id=player_id).one()
        player.player_image = b64encode(player.player_image)
        teams = get_team()
        result['player'] = player
        result['teams'] = teams
        return render_template('edit_player_info.html', results=result)


@app.route('/update_player', methods=['POST', 'GET'])
def updateplayer():
    if request.method == 'POST':
        result = request.form
        player = Player.query.filter_by(player_id=result.get('player_id')).one()
        player.player_fname = result.get('player_fname')
        player.player_lname = result.get('player_lname')
        player.team_id = result.get('team_selected')
        if request.files:
            player.player_image = request.files['playerImage'].read()
        db.session.commit()
    return getAllPlayers()


@app.route('/getAllTeamInfo', methods=['POST', 'GET'])
def get_all_team_info():
    """This method return all team information"""
    # hit this url in browser or postman like  http://127.0.0.1:5000/getAllTeamInfo and it will return json data
    final_team_list = []
    if request.method == 'GET':
        teams = Team.query.all()
        for rec in range(len(teams)):
            final_team = {}
            final_team['Team_name'] = teams[rec].team_name
            final_team['Team_ID'] = teams[rec].team_id
            final_team_list.append(final_team)
    return json.dumps({"TeamInformation": final_team_list})


@app.route('/getPlayersInfo/<string:team_name>', methods=['POST', 'GET'])
def get_players_info(team_name):
    """This method return all players based on team name"""
    # hit this url in browser or postman like http://127.0.0.1:5000/getPlayersInfo/TeamName and it will return json data
    final_player_list = []
    if request.method == 'GET':
        team_res = Team.query.filter_by(team_name=team_name).first()
        if team_res:
            player_res = Player.query.filter_by(team_id=team_res.team_id).all()
            for rec in range(len(player_res)):
                player_info = {}
                player_info['Player_First_Name'] = player_res[rec].player_fname
                player_info['Player_Lirst_Name'] = player_res[rec].player_lname
                player_info['Team'] = team_name
                player_info['Player_ID'] = player_res[rec].player_id
                player_info['Team_ID'] = player_res[rec].team_id
                final_player_list.append(player_info)
            return json.dumps({"TeamInformation": final_player_list})
        else:
            return json.dumps({team_name: "Team is not available"})


@app.route('/playersDetails', methods=['POST', 'GET'])
def display_read_only_user():
    """This method used for display all player information for read only user """
    # hit this url in browser.
    if request.method == 'GET':
        result_dict = {}
        teams = get_team()
        players = db.session.query(Player, Team).join(Team, Player.team_id == Team.team_id)
        for each in players:
            if each.Player.player_image is not None:
                each.Player.player_image = b64encode(each.Player.player_image)
        result_dict['teams'] = teams
        result_dict['players'] = players
        return render_template('team_player_detail.html', result=result_dict)


app.secret_key = os.urandom(24)
app.run()
