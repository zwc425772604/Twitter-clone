#!/usr/bin/python3

from flask import Flask
from flask import session

#from flask.ext.restful import reqparse, Api, Resource, fields, marshal_with



from restfulAPI.twitterModel import dbcontroller
from restfulAPI.mediaModel import mediacontroller
import smtplib
import datetime
import time
import random
import string
import json
import os


def id_generator(size=24,chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))




def additem(request):
    if request.method == 'POST':
        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))
        content=""
        childType="null"
        parent="null"
        media="null"
        like=0

        if "content" in json_data:
            content = json_data['content']
        else:
            return json.dumps({'status':'error',"error" : "no content"})

        if 'childType' in json_data:
            childType=json_data['childType']

        if 'parent' in json_data:
            parent=json_data["parent"]

        if 'media' in json_data:
            media=json_data["media"]

        if 'username' in session:
            username = session['username']
            userID = session["userID"]
            timestamp = int(time.time())
            res = dbcontroller.mongod_additem(userID,username,content,timestamp,childType,like,parent,media)
            
            if (res != None):
                return json.dumps({'status':'OK',"id" : res})
            else:
                return json.dumps({'status':'error',"error" : "failed to post"})
        else:
            return json.dumps({'status':'error',"error" : "have to login"})

















def itemAction(request,item_id):
    if request.method == 'GET':
        objectID = item_id
        res = dbcontroller.mongod_getitem(objectID)
        #mysql_rs=dbcontroller.mysql_find(res['userid'],"userid")
        
        itemid=res["_id"].__str__()
        username=res["username"]
        propertylist={"likes":res["like"]}
        
        retweeted=res["retweeted"]
        content=res["content"]
        timestamp=res["timestamp"]

        childType=res["childType"]
        parent=res["parent"]
        media=res["media"]


        iteminfo={"id":itemid,"username":username,"retweeted" : retweeted, "content":content,"timestamp":timestamp,"property":propertylist,"childType":childType,"parent":parent,"media":media}

        return json.dumps({"status" : "OK", "item" : iteminfo})

    elif request.method == 'DELETE':

        if 'username' in session:
            res = dbcontroller.mongod_getitem(objectID)
            media=res["media"]

            dbcontroller.mongod_deleteitem(item_id)
            mediacontroller.remove_mediaList(media)
            return json.dumps({'status':'OK'})

        else:
            return json.dumps({'status':'error'})




def itemLike(request):
     
    return json.dumps({'status':'OK'})





#old........
def search(request):
    if request.method == 'GET':
        return json.dumps({'status':'OK'})
    elif request.method == 'POST':
        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))

        print(json_data)
        timestamp=int(time.time())
        limit=25
        following=True
        if 'timestamp' in json_data:
            timestamp = json_data.get('timestamp')
            #timestamp = timestamp
        if 'limit' in json_data:
            limit = json_data.get('limit')
            if limit > 100:
                limit = 100
        if 'following' in json_data:
            following=json_data.get('following')

        searchType = 'default'

        queryinfo={"timestamp":timestamp,"limit":limit,"following":following}


        followingUsernameList=[]







        if 'q' in json_data:
            queryinfo['q']=json_data.get('q')


        if 'username' in json_data:
            queryinfo['username']=json_data.get('username')




        if following==True:
            followingUsernameList = dbcontroller.mongod_getUserFollowingList(session['username'],200)
            print(session["username"])
            queryinfo["followingUsernameList"]=followingUsernameList

            if 'username' in json_data:
                if queryinfo['username'] not in followingUsernameList:
                    return json.dumps({'status':'OK',"items":[],"i1":json_data})


                followingUsernameList=list(queryinfo["username"])
                queryinfo["followingUsernameList"]=followingUsernameList

                if 'q' not in json_data:  #just username
                    searchType="followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i2":json_data})
                else:  #q in json_data
                    searchType="q+followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i3":json_data})


            else:#username not in

                if 'q' in json_data:
                    searchType="q+followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i4":json_data})

                else:  #userdata
                    searchType="followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i5":json_data})


        else:
            if 'q' not in json_data and 'username' not in json_data:  #search all context
            #default
                searchType="default+all"  #just time and limit
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i6":json_data})

            elif 'q' in json_data and 'username' in json_data:
                searchType="q+username+all"
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i7":json_data})

            elif 'q' in json_data:
                searchType="q+all"
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i8":json_data})

            elif 'username' in json_data:
                searchType="username+all"
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i9":json_data})






'''
def search(request):
    if request.method=="POST":

        if "username" in session:
            print(session["username"])

        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))
        print(json_data)


        timestamp=int(time.time())
        limit=25

        q=""
        searchusername=""
        following=True

        rank="interest"
        parent=None
        replies=False
        hasMedia=False
        
        currentusername=""
        if "timestamp" in json_data:
            timestamp=int(json_data.get("timestamp"))

        if "limit" in json_data:
            limit=int(json_data.get("limit"))
            if limit>100:
                limit=100
            if limit<=0:
                limit=25

        if "q" in json_data:
            q=json_data.get("q")

        if "username" in json_data:
            searchusername=json_data.get("username")

        if "following" in json_data:
            searchusername=json_data.get("following")
        
        if "rank" in json_data:
            searchusername=json_data.get("rank")

        if "parent" in json_data:
            searchusername=json_data.get("parent")

        if "replies" in json_data:
            replies=json_data.get("replies")

        if "hasMedia" in json_data:
            replies=json_data.get("hasMedia")

'''



'''



def search(request):
    if request.method == 'GET':
        return json.dumps({'status':'OK'})
    elif request.method == 'POST':
        if "username" in session:
            print(session["username"])
        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))
        print(json_data)

        timestamp=int(time.time())
        limit=25
        following=True
        if 'timestamp' in json_data:
            timestamp = int(json_data.get('timestamp'))
            #timestamp = timestamp
        if 'limit' in json_data:
            limit = json_data.get('limit')
            if limit > 100:
                limit = 100
        if 'following' in json_data:
            following=json_data.get('following')

        searchType = 'default'

        queryinfo={"timestamp":timestamp,"limit":limit,"following":following}


        followingUsernameList=[]







        if 'q' in json_data:
            queryinfo['q']=json_data.get('q')


        if 'username' in json_data:
            queryinfo['username']=json_data.get('username')


        print(queryinfo)

        if following==True:
            followingUsernameList = dbcontroller.mongod_getUserFollowingList(session['username'],200)
            queryinfo["followingUsernameList"]=followingUsernameList

            if 'username' in json_data:
                if queryinfo['username'] not in followingUsernameList:
                    return json.dumps({'status':'OK',"items":[],"i1":json_data})


                followingUsernameList=list(queryinfo["username"])
                queryinfo["followingUsernameList"]=followingUsernameList

                if 'q' not in json_data:  #just username
                    searchType="followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i2":json_data})
                else:  #q in json_data
                    searchType="q+followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i3":json_data})


            else:#username not in

                if 'q' in json_data:
                    searchType="q+followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i4":json_data})

                else:  #userdata
                    searchType="followingUsernameList"
                    res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                    return json.dumps({'status':'OK',"items":res,"i5":json_data})


        else:
            if 'q' not in json_data and 'username' not in json_data:  #search all context
            #default
                searchType="default+all"  #just time and limit
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i6":json_data})

            elif 'q' in json_data and 'username' in json_data:
                searchType="q+username+all"
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i7":json_data})

            elif 'q' in json_data:
                searchType="q+all"
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i8":json_data})

            elif 'username' in json_data:
                searchType="username+all"
                res = dbcontroller.mongod_searchitems(searchType,queryinfo)
                return json.dumps({'status':'OK',"items":res,"i9":json_data})
'''

