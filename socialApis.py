import time
import pymongo
import requests


class APIError(Exception):

    def __init__(self, status_code, error_type, error_message):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self):
        return "(%s) %s-%s" % (self.status_code, self.error_type, self.error_message)
    
class InstagramAPI:

    def __init__(self,access_token):
        self.access_token = access_token

    def _Apicall(self,url):
        res=requests.get(url)
        status_code=res.status_code
        content_obj=res.json()
        if status_code==200:
            return content_obj['data'],content_obj.get('pagination',{}).get('next_url')
            
        else:
            raise APIError(status_code, content_obj['meta']['error_type'], content_obj['meta']['error_message']) 
        
    def get_media(self,user_id,since=0,until=time.time()):
        #get list of media
        media_list=[]
        url='https://api.instagram.com/v1/users/{}/media/recent/?access_token={}'.format(user_id,self.access_token)
        object_,pagination_=self._Apicall(url)
        media_list.extend(object_)
        if len(object_):
            post_epochtime=object_[len(object_)-1].get('created_at')
        
        
        while (pagination_ and post_epochtime > since and post_epochtime < until):
            object_,pagination_=self._Apicall(pagination_)
            post_epochtime=object_[len(object_)-1].get('created_at')
            media_list.extend(object_)
        return media_list
    
    def get_comments(self,media_id):
        #get list of comments
        comments_list=[]
        url='https://api.instagram.com/v1/media/{}/comments?access_token={}'.format(media_id,self.access_token)
        object_,pagination_=self._Apicall(url)
        comments_list.extend(object_)
        while (pagination_):
            object_,pagination_=self._Apicall(pagination_)
            comments_list.extend(object_)
            
                
        return comments_list
class FacebookAPI:

    def __init__(self,access_token):
        self.access_token = access_token

    def _Apicall(self,url):
        res=requests.get(url)
        status_code=res.status_code
        content_obj=res.json()
        if status_code==200:
            return content_obj['data'],content_obj.get('paging',{}).get('next')
            
        else:
            raise APIError(status_code, content_obj['error']['type'], content_obj['error']['message'])
        
    def get_media(self,page_id,since=0,until=time.time()):
        #get list of media
        media_list=[]
        url='https://graph.facebook.com/{}/posts?fields=type,message,id,created_time,comments&since={}&until={}&access_token={}'.format(page_id,since,until,self.access_token)        
        object_,pagination_=self._Apicall(url)
        media_list.extend(object_)
        while (pagination_):         
            object_,pagination_=self._Apicall(pagination_)
            media_list.extend(object_)                
        return media_list
    
    def get_comments(self,comments_data):
        #get list of comments
        comments_list=comments_data['data']
        pagination_=comments_data.get('paging',{}).get('next')
        while (pagination_):
            object_,pagination_=self._Apicall(pagination_)
            comments_list.extend(object_)            
        return comments_list