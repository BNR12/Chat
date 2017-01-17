from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#user
#username and password only
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True)
	password = db.Column(db.String(60), nullable=False)

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<Username {}>'.format(self.username)


#rooms
#name, link to JSON message history
class Room(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)

	def __init__(self, name):
		self.name = name
	

	def __repr__(self):
		return '<Room {}>'.format(self.name)