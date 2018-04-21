
from flask import Flask,jsonify,Response
from flask import request
#from flaskext.mysql import MySQL
import json

#import memcache
#from pymemcache.client.base import Client
#mysql = MySQL()
#app = Flask(__name__)
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = '0822'
#app.config['MYSQL_DATABASE_DB'] = 'hw7'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)
 
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

#from restfulAPI.mediaModel import controller as mediaModel
from restfulAPI.personalModel import controller as personalModel
from restfulAPI.twitterModel import controller as twitterModel
from restfulAPI.mediaModel import mediacontroller as mediaModel





@app.route('/', methods=['GET'])
def route_home():
    return jsonify("Home")

@app.route('/login', methods=['POST'])
def route_login():
    return personalModel.login(request)

@app.route('/logout', methods=['POST'])
def route_logout():
    return personalModel.logout(request)

@app.route('/verify', methods=['POST'])
def route_verify():
    return personalModel.verify(request)

@app.route('/adduser', methods=['POST'])
def route_adduser():
    return personalModel.adduser(request)

@app.route('/follow', methods=['POST'])
def route_follow():
    return personalModel.follow(request)

@app.route('/user/<username>', methods=['GET'])
def route_getUserInfo(username):
    return personalModel.getUserInfo(request,username)

@app.route('/user/<username>/followers', methods=['GET'])
def route_getUserFollowers(username):
    return personalModel.getUserFollowers(request,username)

@app.route('/user/<username>/following', methods=['GET'])
def route_getUserFollowing(username):
    return personalModel.getUserFollowing(request,username)

@app.route('/additem', methods=['POST'])
def route_additem():
    return twitterModel.additem(request)

@app.route('/item/<itemID>', methods=['GET','DELETE'])
def route_itemAction(itemID):
    return twitterModel.itemAction(request,itemID)

@app.route('/item/<itemID>/like', methods=['POST'])
def route_itemLike(itemID):
    return twitterModel.itemLike(request,itemID)

@app.route('/search', methods=['POST'])
def route_search():
    return twitterModel.search(request)


@app.route('/addmedia', methods=['POST'])
def route_addmedia():
    return mediaModel.additem(request)

@app.route('/media/<mediaID>', methods=['GET'])
def route_getMedia(mediaID):
    return mediaModel.getMedia(request,mediaID)




if __name__ == '__main__':
    app.run()