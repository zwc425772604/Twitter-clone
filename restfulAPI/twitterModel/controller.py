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

        print (json_data)
        content=""
        childType="null"
        parent=""
        media=""
        like=0

        if "content" in json_data:
            content = json_data.get('content')
        else:
            return json.dumps({'status':'error',"error" : "no content"})


        if 'childType' in json_data:
            childType=json_data.get('childType')

        if 'parent' in json_data:
            parent=json_data.get("parent")

        if 'media' in json_data:
            media=json_data.get("media")

        if 'username' in session:
            username = session['username']
            userID = session["userID"]
            print(username)
            timestamp = int(time.time())
            
           
            
            itemid = id_generator()
            

            dbcontroller.mongod_additem(userID,username,content,timestamp,itemid,childType,like,parent,media)
            return json.dumps({'status':'OK',"id" : itemid})
            #pid=os.fork()
            #if pid==0:
            #    dbcontroller.mongod_additem(userID,username,content,timestamp,itemid,childType,like,parent,media)
            #    quit()
            #else:
            #    return json.dumps({'status':'OK',"id" : res})
            
            #if (res != None):
            #    return json.dumps({'status':'OK',"id" : res})
            #else:
            #    return json.dumps({'status':'error',"error" : "failed to post"})
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

            #pid=os.fork()
            #if pid==0:
            #    dbcontroller.mongod_deleteitem(item_id)
            #    mediacontroller.remove_mediaList(media)
                #return json.dumps({'status':'OK'})
            #    quit()

            #else:
             

            #    return json.dumps({'status':'OK'})
            dbcontroller.mongod_deleteitem(item_id)
            mediacontroller.remove_mediaList(media)
            return json.dumps({'status':'OK'})

        else:
            return json.dumps({'status':'error'})




def itemLike(request,item_id):
    if request.method == 'GET':
        return json.dumps({"status" : "error"})
    elif request.method == 'POST':
        data=request.get_data()
        json_data = json.loads(data.decode('utf-8'))

        like = True
        currentUsername = session['username']
        if "like" in json_data:
            like = json_data.get('like')
        res = dbcontroller.mongod_itemLike(item_id,currentUsername,like)
        return json.dumps({'status':'OK'})    









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
            following=json_data.get("following")
        
        if "rank" in json_data:
            rank=json_data.get("rank")

        if "parent" in json_data:
            parent=json_data.get("parent")

        if "replies" in json_data:
            replies=json_data.get("replies")

        if "hasMedia" in json_data:
            hasMedia=json_data.get("hasMedia")


        if "username" not in session:
            return json.dumps({'status':'errorr',"error":"have to login"})


        if following==False:  #search all
            if searchusername!="":
                #search all seachusernam
               #dbcontroller.mongod_getSpecUserItem(searchusername,timestamp,lim,q)
                res=dbcontroller.mongod_help_searchUserItem(searchusername,q,timestamp,limit,rank,parent,replies,hasMedia)   
                returnlist=help_sortReturnItemList(res,rank,limit)
                return json.dumps({"status":"OK","items":returnlist})

            else:
                #search all item in random
                res=dbcontroller.mongod_help_searchItem(q,timestamp,limit,rank,parent,replies,hasMedia)
                returnlist=help_sortReturnItemList(res,rank,limit)
                return json.dumps({"status":"OK","items":returnlist})



        elif following==True: #just search current user
            currentusername=session["username"]
            
            followinglist=dbcontroller.mongod_getUserFollowingList(currentusername,200)
            
            if searchusername!="":

                if searchusername not in followinglist:
                    return json.dumps({'status':'OK',"items":[]})

                else: #searchusername in following list
                    #just search this searchusername
                    res=dbcontroller.mongod_help_searchUserItem(searchusername,q,timestamp,limit,rank,parent,replies,hasMedia)
                    returnlist=help_sortReturnItemList(res,rank,limit)
                    return json.dumps({"status":"OK","items":returnlist})

            
            else:
                #searchusername="". seach all user who in followinglist
                #returnlist=[]
                
                ##map reduce


                #for each in followinglist:
                #    res=help_searchUserItem(each,q,timestamp,limit,rank,parent,replies,hasMedia)
                #    returnlist.extend(res)
                
                res=dbcontroller.mongod_help_searchUserListItem(followinglist,q,timestamp,limit,rank,parent,replies,hasMedia)
                #according rank,limit renew sort the return

                returnlist=help_sortReturnItemList(res,rank,limit)

                return json.dumps({"status":"OK","items":returnlist})











    





from operator import itemgetter
def help_sortReturnItemList(itemlist,rank,limit):
    
    if rank=="time":

        sorted(itemlist, key=lambda k: k["timestamp"])
        return itemlist[:limit]

    if rank=="interest":
        sorted(itemlist,key=lambda k: k["interest"])
        return itemlist[:limit]        






