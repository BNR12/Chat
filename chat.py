import os
import json
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from models import db, User, Room

app = Flask(__name__)

app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='test',

	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')
))

db.init_app(app)

#i am using a message id to keep track of new vs old messages for polling updates
msg_increment = 1;

#initialize db
@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.create_all()
	print('Initialized the database.')

#home page
@app.route('/')
def to_login():
	#test if logged in
	if not session.get('logged_in'):
		#return URL to login page
		return redirect(url_for('login'))
	else:
		#return chat dashboard if logged in
		return redirect(url_for('dashboard'))
		

#log in page
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None

	if request.method == 'POST':
		#try to login
		#get username and password from form
		usernameEnter = request.form['username']
		passwordEnter = request.form['password']

		#query db for user with this username
		userDB = User.query.filter_by(username=usernameEnter).first()

		#if user not found
		if userDB is None:
			error="Invalid username"
		elif userDB.password != passwordEnter:
			error="Invalid password"
		else:
			#login
			session['logged_in']=True
			session['curr_user']=usernameEnter

			#send to dashboard
			return redirect(url_for('dashboard'))
	return render_template('login.html', error=error)

#log out
@app.route('/logout')
def logout():
	#perform logout
	session.pop('logged_in', None)
	session.pop('curr_user', None)

	#redirect to main page
	return redirect(url_for('to_login'))

#create account page
@app.route("/newaccount", methods=['GET', 'POST'])
def new_account():
	#form to create new account
	error = None
	msg = None
	if request.method == 'POST':
		#get username and password from form
		usernameEnter = request.form['username']
		passwordEnter = request.form['password']

		#query db for user with this username
		userDB = User.query.filter_by(username=usernameEnter).first()

		#if user not found
		if userDB is None:
			#create new user
			new = User(usernameEnter, passwordEnter)
			db.session.add(new)
			db.session.commit()
			msg="Account Successfully Created"
		else:
			error="Username already in use"
	return render_template('create.html', error=error, msg=msg)

#chat dashboard
@app.route('/dashboard')
def dashboard():
	#listing of chat rooms
	#should only appear if logged in
	#this does not need to be user specific, since any user can view all chat rooms
	#test if logged in
	if not session.get('logged_in'):
		#return URL to login page
		return redirect(url_for('login'))
	else:
		#query for chat rooms
		rooms = Room.query.all()
		return render_template('dashboard.html', rooms=rooms, user=session.get('curr_user'))

#create new chat room
@app.route('/newroom', methods=['GET', 'POST'])
def new_room():
	error = None
	msg = None
	#create a new chat room
	if not session.get('logged_in'):
		#return URL to login page
		return redirect(url_for('login'))
	elif request.method == 'POST': 
		roomName = request.form['name']

		#test if room exists
		room = Room.query.filter_by(name=roomName).first()
		if room is None:
			#create room
			new = Room(roomName)
			db.session.add(new)
			db.session.commit()
			msg = "Room successfully created"

			#create new json file
			filename = roomName + ".json"
			file = open(filename, 'w')
			json.dump([], file)
			file.close()
		else:
			error = "Room name already in use"
	return render_template('newroom.html', error=error, msg=msg)

#chat room page
@app.route('/room/<room>')
def chat_room(room):
	filename = room + ".json"
	file = open(filename, 'r')
	history = file.read()

	#sends json string to template as history variable
	return render_template('chatroom.html', room=room, user=session.get('curr_user'), history=history)

#add new message
@app.route("/send_message", methods=["POST"])
def add():
	#append to json file

	#get variables
	room = request.form["room"]
	msg = request.form["msg"]
	user = request.form["user"]
	history = room + ".json"

	#open and read file
	file = open(history)
	messages = json.load(file)
	file.close()

	#add new message to the history (including the id)
	global msg_increment
	num = str(msg_increment)
	messages.append({"user":user, "text":msg, "id":num})
	msg_increment+=1;

	#dump to file
	file = open(history, 'w')
	json.dump(messages, file)
	file.close()
	return num

@app.route("/messages", methods=["POST"])
def get_messages():
	#return new messages
	room = request.form["room"]
	history = room + ".json"

	last = request.form["id"]

	file = open(history)
	messages = json.load(file)
	file.close()

	#filter new messages > the last loaded message
	new_messages = [x for x in messages if x['id'] > last]
	return json.dumps(new_messages)



if __name__ == "__main__":
	app.run()