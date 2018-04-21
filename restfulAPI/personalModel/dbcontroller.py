
import pymysql
#pymysql.install_as_MySQLdb()

import pymongo

import string
import random
import time


mysqlhost="130.245.168.85"
mysqlport=3306
mysqldb="mysql_db4"
mysqluser="root"
mysqlpassword="123456"


mongohost="130.245.168.85"
mongodport=27017


def id_generator(size=10,chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def mysql_find(item,style):
    db=pymysql.connect(host=mysqlhost,user=mysqluser,passwd=mysqlpassword,db=mysqldb,charset='utf8')
    cursor=db.cursor()
    if style=="username+email":
        cursor.execute("select * from users where username=%s OR email=%s",[item["username"],item["email"]])
    elif style=="username":
        cursor.execute("select * from users where username=%s",item)
    elif style=="userid":
        cursor.execute("select * from users where userid=%s",item)
    elif style=="email":
        cursor.execute("select * from users where email=%s",item)

    rs=cursor.fetchone()
    cursor.close()
    db.close()
    return rs   #control excetion later


def mysql_checkuser(username,email): #use to check there aresame username or emaiul
    item={"username":username,"email":email}
    res = mysql_find(item,"username+email")
    if res is None:
        return True
    else:
        return False



def mysql_adduser(info):

    username=info["username"]
    password=info["password"]
    email=info["email"]
    timestamp=info["timestamp"]
    userid=id_generator()
    db=pymysql.connect(host=mysqlhost,user=mysqluser,passwd=mysqlpassword,db=mysqldb,charset='utf8')

    cursor=db.cursor()

    cursor.execute('insert into users (userid,username, email, password,timestamp) values (%s, %s, %s,%s,%s);', [userid,username, email,password,timestamp])
    db.commit()
    cursor.close()
    db.close()
    mongod_createUser(userid,username,email)   #can do block i/o
    return True








def mysql_login(username,password):
    rs=mysql_find(username,"username")
    #user is not registerd
    if rs is None:
        return False

    if password==rs[3]:    #rs[3] is password
        return rs
    else:
        return False



def mysql_getuserid(username):
    rs=mysql_find(item=username,style="username")
    id=rs[0]
    return id



from bson.objectid import ObjectId




def mongod_createUser(userid,username,email):
    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.usersRelation

    mongodbid=collection.insert({"_id": userid, "userid":userid,"username":username,"email":email,"followersCount": 0,"followingCount":0,"followersList": [],"followingList": []})
    objectid=mongodbid.__str__()
    return objectid

def mongod_getUser(username):
    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.usersRelation

    userid = mysql_getuserid(username)
    item=collection.find_one({'_id':userid})

    return item

def mongod_followUser(currentUsername, username,action):
    #userid = mysql_getuserid(currentUsername)
    #secondUserId = mysql_getuserid(username)

    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.usersRelation

    #item=collection.find_one({"_id": userid}) #current user
    #item1 = collection.find_one({"_id": secondUserId}) #second user

    item=collection.find_one({"username": currentUsername}) #current user
    item1 = collection.find_one({"username": username}) #second user
    followingList = item["followingList"] # list of usernames that current user follow
    followersList = item1["followersList"]  # list of followers' username that second user has

    if action: #follow an user
        followingList.append(username)
        #collection.update({ '_id': userid},  {'$set': { "followingCount" : item["followingCount"] + 1, 'followingList' : followingList} })
        collection.update({ 'username': currentUsername},  {'$set': { "followingCount" : item["followingCount"] + 1, 'followingList' : followingList} })
        followersList.append(currentUsername)
        #collection.update({ '_id': secondUserId},  {'$set': { "followerCount" : item1["followersCount"] + 1, 'followersList' : followersList} })
        collection.update({ 'username': username},  {'$set': { "followerCount" : item1["followersCount"] + 1, 'followersList' : followersList} })
        return item
    else: #unfollow an user
        followingList.remove(username)
        #collection.update({ '_id': userid},  {'$set': { "followingCount" : item["followingCount"] - 1, 'followingList' : followingList} })
        collection.update({ 'username':currentUsername },  {'$set': { "followingCount" : item["followingCount"] - 1, 'followingList' : followingList} })
        followersList.remove(currentUsername)
        #collection.update({ '_id': secondUserId},  {'$set': { "followerCount" : item1["followersCount"] - 1, 'followersList' : followersList} })
        collection.update({ 'username': username},  {'$set': { "followerCount" : item1["followersCount"] - 1, 'followersList' : followersList} })
        return item


def mongod_getUserFollowersList(username, lim):

    #userid=mysql_getuserid(username)

    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.usersRelation

    #item=collection.find_one({"_id": userid}) #current user
    item=collection.find_one({"username": username}) #current user
    followerslist = item['followersList']
    return followerslist[:lim]



def mongod_getUserFollowingList(username, lim):

    #userid=mysql_getuserid(username)

    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.usersRelation


    #item=collection.find_one({"_id": userid}) #current user
    item=collection.find_one({"username": username}) #current user
    followinglist = item['followingList']
    return followinglist[:lim]
