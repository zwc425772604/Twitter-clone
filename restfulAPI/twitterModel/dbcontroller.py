import time
import pymysql
import threading
from DBUtils.PooledDB import PooledDB, SharedDBConnection
POOL = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建


    maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
    maxshared=3,  # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    ping=0,
    # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
    host='130.245.168.85',
    port=3306,
    user='root',
    password='123456',
    database='mysql_db4',
    charset='utf8'
)


def mysqlhavelistfunc(executestring,varlist):
    # 检测当前正在运行连接数的是否小于最大链接数，如果不小于则：等待或报raise TooManyConnections异常
    # 否则
    # 则优先去初始化时创建的链接中获取链接 SteadyDBConnection。
    # 然后将SteadyDBConnection对象封装到PooledDedicatedDBConnection中并返回。
    # 如果最开始创建的链接没有链接，则去创建一个SteadyDBConnection对象，再封装到PooledDedicatedDBConnection中并返回。
    # 一旦关闭链接后，连接就返回到连接池让后续线程继续使用。

    # PooledDedicatedDBConnection
    conn = POOL.connection()

    # print(th, '链接被拿走了', conn1._con)
    # print(th, '池子里目前有', pool._idle_cache, '\r\n')

    cursor = conn.cursor()
    cursor.execute(executestring,varlist)
    result = cursor.fetchall()
    conn.close()
    return result

def mysqlnolistfunc(executestring):

    conn = POOL.connection()

    # print(th, '链接被拿走了', conn1._con)
    # print(th, '池子里目前有', pool._idle_cache, '\r\n')

    cursor = conn.cursor()
    cursor.execute(executestring)
    result = cursor.fetchall()
    conn.close()
    return result




























import pymysql


import pymongo

import string
import random
import time

def id_generator(size=10,chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

mysqlhost="130.245.168.85"
mysqlport=3306
mysqldb="mysql_db4"
mysqluser="root"
mysqlpassword="123456"


mongohost="130.245.168.85"
mongodport=27017







from bson.objectid import ObjectId

def mongod_additem(userid,username,content,timestamp,itemid,childType,like,parent,media):

    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.allitems
    likelist = []
    retweeted = 0
    hasMedia = True if len(media) else False
    originalitem = True if childType == "null" else False
    retweetitem = True if childType == 'retweet' else False
    replyitem = True if childType == 'reply' else False

    if parent != None and childType == 'retweet':
        item=collection.find_one({"itemid":parent})
        if parent=="":
            db.allitems.update({ 'itemid': parent},  {'$set': { "retweeted" : item["retweeted"] + 1, 'interest': item['interest']+1} })

    mongodbid=collection.insert({"itemid": itemid, "userid":userid,"content":content,"timestamp":timestamp,"childType":childType,"like":like,"username" : username,'likelist': likelist,
    'media': media,"parent":parent,'retweeted':retweeted,"hasMedia":hasMedia,"originalitem":originalitem,"retweetitem":retweetitem,"replyitem":replyitem,"interest":0})
    #objectid=mongodbid.__str__()
    # bulk = db.allitems.initialize_unordered_bulk_op()
    # x = ObjectId()
    # bulk.insert({"_id": x, "userid":userid,"context":context,"timestamp":timestamp,"childtype":childtype,"like":like,"username" : username} )
    # bulk.execute( )
    # objectid = x.__str__()

    client.close()
    #objectid = x.__str__()
   #return objectid





def mongod_getitem(objectid):
    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.allitems

    #item=collection.find_one({"_id":ObjectId(objectid)})
    item=collection.find_one({"itemid":objectid})
    #example {u'like': 9088, u'timestamp': 12345, u'childtype': 345444, u'userid': 765877, u'context': 890876, u'_id': ObjectId('5ab05d2b24119520c038fa1c')}
    #can just get like item["like"]
    client.close()
    return item



def mongod_deleteitem(objectid):
    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.allitems

    item=collection.remove({"_id":objectid})
    client.close()
    return













def mongod_help_searchUserItem(searchusername,q,timestamp,limit,rank,parent,replies,hasMedia):#spec
    client=pymongo.MongoClient(mongohost,27017)
    db=client.mongodb_db
    collection=db.allitems


    if replies==False:#no reply item
        if parent!="":
            result=collection.find({ "username":searchusername,"hasMedia":hasMedia,"parent":parent,"timestamp":{"$lte":timestamp},"replyitem": False,"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)

        else:
            result=collection.find({"username":searchusername, "hasMedia":hasMedia,"timestamp":{"$lte":timestamp},"replyitem": False,"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)
    else:
        if parent!="":
            result=collection.find({"username":searchusername, "hasMedia":hasMedia,"parent":parent,"timestamp":{"$lte":timestamp},"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)
        else:
            result=collection.find({"username":searchusername, "hasMedia":hasMedia,"timestamp":{"$lte":timestamp},"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)

    return result





def mongod_help_searchItem(q,timestamp,limit,rank,parent,replies,hasMedia): #all

    client=pymongo.MongoClient(mongohost,27017)
    db=client.mongodb_db
    collection=db.allitems

    if replies==False:#no reply item
        if parent!="":
            result=collection.find({"hasMedia":hasMedia,"parent":parent,"timestamp":{"$lte":timestamp},"replyitem": False,"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)

        else:
            result=collection.find({"hasMedia":hasMedia,"timestamp":{"$lte":timestamp},"replyitem": False,"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)
    else:
        if parent!="":
            result=collection.find({"hasMedia":hasMedia,"parent":parent,"timestamp":{"$lte":timestamp},"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)
        else:
            result=collection.find({"hasMedia":hasMedia,"timestamp":{"$lte":timestamp},"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)

    return result


def mongod_help_searchUserListItem (followinglist,q,timestamp,limit,rank,parent,replies,hasMedia): #the list

    client=pymongo.MongoClient(mongohost,27017)
    db=client.mongodb_db
    collection=db.allitems

    resultlist=[]
    for searchusername in followinglist:
        if replies==False:#no reply item
            if parent!="":
                result=collection.find({ "username":searchusername,"hasMedia":hasMedia,"parent":parent,"timestamp":{"$lte":timestamp},"replyitem": False,"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)

            else:
                result=collection.find({"username":searchusername, "hasMedia":hasMedia,"timestamp":{"$lte":timestamp},"replyitem": False,"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)
        else:
            if parent!="":
                result=collection.find({"username":searchusername, "hasMedia":hasMedia,"parent":parent,"timestamp":{"$lte":timestamp},"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)
            else:
                result=collection.find({"username":searchusername, "hasMedia":hasMedia,"timestamp":{"$lte":timestamp},"context":{"$regex":searchInput['q']} }).sort('_id',-1).limit(limit)

        resultlist=result.extend(result)

    return resultlist








from restfulAPI.personalModel import dbcontroller as personalInfoModeldbcontroller



def mongod_getUserFollowingList(username, lim):
    #userid = personalInfoModeldbcontroller.mysql_getuserid(username)
    client=pymongo.MongoClient(mongohost,mongodport)
    db=client.mongodb_db
    collection=db.usersRelation
    #item=collection.find_one({"_id": userid}) #current user
    item=collection.find_one({"username":username})
    followinglist = item['followingList']
    return followinglist[:lim]
