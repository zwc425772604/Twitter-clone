#!/usr/bin/python3

from flask import Flask
from flask import session

#from flask.ext.restful import reqparse, Api, Resource, fields, marshal_with


from restfulAPI.personalModel import dbcontroller

import smtplib
import datetime
import time
import random
import string
import json
import os


from pymemcache.client.base import Client

memhost="localhost"
memport=11211

def login(request):
    if request.method=='POST':

        if 'username' in session:
            return json.dumps({'status':'OK'})
        else:
            data=request.get_data()
            json_data = json.loads(data.decode('utf-8'))


            username = json_data.get('username')
            password = json_data.get('password')

            if (username is None or password is None):
                return json.dumps({'status':'error', 'error': "null username or password"})

            res = dbcontroller.mysql_login(username,password)

            if res == False:
                return json.dumps({'status':'error', 'error': "wrong login"})
            else:
                #mc=Client((memhost,11211))
                #mc.set(,info)
                session['username'] = username
                session['userID'] =res[0]
                return json.dumps({'status':'OK'})



def logout(request):
    if request.method == "POST":
        try:
            session.pop('username',None)
            session.pop('userID',None)
        except KeyError:
            pass
        return json.dumps({'status':'OK'})






def adduser(request):
    if request.method == 'POST':
        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))

        username = json_data.get('username')
        password = json_data.get('password')
        email=json_data.get('email')

        userid=''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)]);

        if username is None or password is None or email is None:
            return json.dumps({'status':'error',"error":"have empty block"})


        key = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])

        timestamp = int(time.time())

        res=dbcontroller.mysql_checkuser(username,email)


        if res==False:
            return json.dumps({'status':'error', 'error' : 'email already register or username already in use'})

        #use memcache
        mc=Client((memhost,memport))

        info={"username":username,"password":password,"email":email,"timestamp":timestamp,"key":key,"userid":userid}
        print(info)
        mc.set(email,info)
        #return json.dumps({'status':mc.get(email)})

        if sendMail(email,key) == True:
            return json.dumps({'status':'OK'})
        else:
            return json.dumps({'status':'error', 'error' : 'invalid email address'})
    else:
        return json.dumps({'status':'error'})












def sendMail(email,random_key):
    # random_key = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])
    sendmail_location = "/usr/sbin/sendmail" # sendmail location
    p = os.popen("%s -t" % sendmail_location, "w")
    p.write("From: %s\n" % "1.0@cloud.compas.cs.stonybrook.edu")
    p.write("To: %s\n" % email)
    p.write("Subject: CSE356\n")
    p.write("\n") # blank line separating headers from body
    p.write("validation key: <")
    p.write(random_key)
    p.write(">\n")
    status = p.close()
    if status != 0:
        print("Sendmail exit status", status)
        return True
    return False





def verify(request):
    if request.method == 'POST':
        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))
        email = json_data.get('email')

        print(email)
        key = json_data.get('key')

        print (key)

        if(email is None or key is None):
            return json.dumps({'status':'error', 'error' : 'none email or key'})
        #return json.dumps({'status':'OK'})
        mc=Client((memhost,memport))
        #return json.dumps({"eee":"eer"})
        info=eval(mc.get(email))    #info={"username":username,"password":password,"email":email,"timestamp":timestamp,"key":key}


        #return json.dumps({'status':'OK'})

        #info=info1.decode("utf8")
        #return json.dumps({'status':info["key"]})
        #return

        if info is None:
            return json.dumps({'status':'error', 'error' : 'not register email'})

        if key==info["key"]:
            #return json.dumps({'status':'OK'})


            #info["userid"]=''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)]);
            #pid =os.fork()

            #if pid ==0:
            #    dbcontroller.mysql_adduser(info)
            #    quit()
                #return json.dumps({'status':'OK'})
            #else:
            #    return json.dumps({'status':'OK'})
            dbcontroller.mysql_adduser(info)
            return json.dumps({'status':'OK'})


            #res = dbcontroller.mysql_adduser(info)
            #if res == False:
            #    return json.dumps({'status':'error', 'error': 'database error'})
            #else:
            #    return json.dumps({'status':'OK'})



        else:
            return json.dumps({'status':'error', 'error' : 'key does not match with the email address'})







def follow(request):
    if request.method == 'GET':
        return json.dumps({'status':'error'})

    elif request.method == 'POST':
        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))
        username = json_data.get('username')

        if username is None:
            return json.dumps({'status':'error',"error":"no username"})
        #return json.dumps({'status':username})
        follow = True
        if 'follow' in json_data:
            follow = json_data.get('follow')
        #if 'username' in request.session:
        #    return json.dumps({'sojbk':request.session['username']})
        #else:
        #    return json.dumps({'status':"555"})
        currentUser = session['username']

        dbcontroller.mongod_followUser(currentUser,username,follow)
        return json.dumps({'status':'OK'})
        #pid=os.fork()
        #if pid==0:
        #    dbcontroller.mongod_followUser(currentUser, username,follow)
        #    quit()
            #return json.dumps({'status':'OK'})
        #else:
        #    return json.dumps({'status':'OK'})

        #dbcontroller.mongod_followUser(currentUser, username,follow)
        #return json.dumps({'status':'OK'})



def getUserInfo(request,username):
    if request.method == "GET":

        res=dbcontroller.mongod_getUser(username)
        returnjson={"email":res["email"],"followers":res["followersCount"],"followering":res["followeringCount"]}
        return json.dumps({'status':"OK","user":returnjson})


def getUserFollowers(request,username):
    if request.method == "GET":

        limit = request.args.get('limit')
        if limit is None or limit<0:
            limit = 50
        elif limit>200:
            limit=200
        res = dbcontroller.mongod_getUserFollowersList(username, limit)
        return json.dumps({'status':"OK", "users" : res,"test":"i1"})
    return json.dumps({'status':'error'})



def getUserFollowing(request,username):
    if request.method == 'GET':
            limit = request.args.get('limit')
            if limit is None or limit<0:
                limit = 50
            elif limit>200:
                limit=200
            res = dbcontroller.mongod_getUserFollowingList(username, limit)
            return json.dumps({'status':"OK", "users" : res,"test":"i2"})
    return json.dumps({'status':'error'})
