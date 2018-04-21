
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

def remove_mediaList(mediaList):
	return






def addmedia(request):
    if request.method == 'GET':
        # fs = pyhdfs.HdfsClient(hosts='130.245.170.190:50070', user_name='hduser')
        # re = fs.listdir('/user/hduser/media/')
        return json.dumps({'status':'error'})
    elif request.method == 'POST':
        inputfile = request.FILES['content']
        filename = request.FILES['content'].name
        filesize = request.FILES['content'].size
        fs = pyhdfs.HdfsClient(hosts='130.245.170.190:50070', user_name='hduser')
        path = '/user/hduser/media/' + filename
        fs.create(path,inputfile)
        re = fs.get_file_status(path)
        fileid = re['fileId']
        #data = request.FILES['content'].chunks().decode('utf-8')
        #my_uploaded_file = request.FILES['content'].read()
        #json_data = request.body
        #inputfile = json.load(request.FILES['content']
        #print(inputfile)
        #json.dumps(str(inputfile))
        #content = json_data['content']
        return json.dumps({'status':'OK',"id" : fileid, "content": request.FILES['content'].size, "filename" : filename})


def getMedia(request,media_id):
    if request.method == "GET":
        mediaId = int(media_id)
        fs = pyhdfs.HdfsClient(hosts='130.245.170.190:50070', user_name='hduser')
        path = '/user/hduser/media/'
        re = fs.listdir(path)
        found = False
        fileIdList = []
        for f in re:
            id1 = fs.get_file_status(path + f).fileId
            fileIdList.append(id1)
            if id1 == mediaId:
                found = True
                da = fs.open(path + f)
                return HttpResponse(da.read(), content_type="image/png")
        return json.dumps({'status':'error',"result": re,"found": found, "fileidlist" : fileIdList, "media_id": mediaId})

