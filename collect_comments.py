from  config import FACEBOOK_TOKEN,INSTA_TOKEN,MONGO_CLIENT
import pymongo
from socialApis import FacebookAPI , InstagramAPI

def generate_mongo_client(client):
    database_name = ''
    if 'database' in client:
        database_name = client['database']

    if 'host' in client:
        host = client['host']
    if 'port' in client:
        port = client['port']

    if 'user' in client:
        user = client['user']
        if 'pwd' in client:
            pwd = client['pwd']
        else:
            return pymongo.MongoClient("mongodb://" + user + "@" + host + ":" + str(port) + "/" + database_name,
                               socketTimeoutMS=None, connectTimeoutMS=None)
    else:
        return pymongo.MongoClient("mongodb://" + host + ":" + str(port) + "/" + database_name,
                           socketTimeoutMS=None, connectTimeoutMS=None)

    return pymongo.MongoClient("mongodb://" + user + ":" + pwd + "@" + host + ":" + str(port) + "/" + database_name,
                       socketTimeoutMS=None, connectTimeoutMS=None)

#Public post search is no longer available from API version >=2.0 in facebook and istagram so we will get all posts of popular tunisian pages like(mosaiqueFM,JawhraFm)  and filter posts based on message.  

popular_pages={'facebook':[346593403645,166105103436041],'instagram':[621404596,1130611308]} # like 

#get list of comments related to the death of Béji Caïd Essebsi
since=1564012800 # day of the death
interval=5 # number of days 
until=since+interval*24*60*60


# init mongo client
mongoclient=generate_mongo_client(MONGO_CLIENT)
db = mongoclient['comments']
instagram_collection=db.instagram
facebook_collection=db.facebook

#Use facebook API 
fbapi=FacebookAPI(FACEBOOK_TOKEN)
for page_id in popular_pages['facebook']:
    fbposts=fbapi.get_media(page_id,since=since,until=until)
    postcomments=[]
    for post in fbposts :
        posttext=post.get('message','').lower().replace('é','e').replace('è','e').replace('ï','i')
        #filter facebook posts
        if post['type']=='photo' and post.get('comments') and (all(x in  posttext for x in ['deces','beji'])
            or all(x in posttext for x in [u'وفاة',u'باجي'])   
            or all(x in posttext for x in ['mort','beji'])):
            postcomments.extend(fbapi.get_comments(post['comments']))
    if len(postcomments):
        facebook_collection.insert_many(postcomments) # insert in facebook collection
        
#Use instagram API 
instagramapi=InstagramAPI(INSTA_TOKEN)
for page_id in popular_pages['instagram']:
    instaposts=instagramapi.get_media(page_id,since=since,until=until)
    postcomments=[]
    for post in instaposts :
        #filter instagram posts
        caption=post.get('caption')
        if  caption :
            posttext=caption.get('text','').lower().replace('é','e').replace('è','e').replace('ï','i')
            if  post['type']=='image' and (all(x in posttext for x in ['deces','beji'])
                or all(x in posttext for x in [u'وفاة',u'باجي'])   
                or all(x in posttext for x in ['mort','beji'])):

                postcomments.extend(instagramapi.get_comments(post['id']))
    if len(postcomments)   :     
        instagram_collection.insert_many(postcomments) # insert in instagram collection
mongoclient.close()