import tweepy
import csv

class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.id_str)
        
        # check and see if it is a retweet & has place attribute
        is_retweet = hasattr(status, "retweeted_status")
        loc = status.place
        if (not is_retweet) and (loc is not None):
            # get the extended tweet text
            if hasattr(status,"extended_tweet"):
                text = status.extended_tweet['full_text']
            else:
                text = status.text
            
            # get the loc of tweet
            tweet_loc_name = str(loc.full_name) 
            tweet_loc_cor = str(loc.bounding_box.coordinates)
            #remove invalid locations
            if not all(ord(char) < 128 for char in tweet_loc_name):
                tweet_loc_name = 'None'
            
            # get location of the user
            user_location = str(status.user.location)
                #remove invalid locations
            if not all(ord(char) < 128 for char in user_location):
                user_location = 'None'
                
#             # get the place info of the post: simple version
#             tweet_loc = str(status.place)                
        
            # csv formating
            remove_characters = [',','\n','\r','\t']
            for c in remove_characters:
                text = text.replace(c," ")
                user_location = user_location.replace(c," ")
                tweet_loc_name = tweet_loc_name.replace(c," ")
                tweet_loc_cor = tweet_loc_cor.replace(c," ")
            
            # write into csv file
            with open('out.csv','a',encoding = 'utf-8') as f:
                friend = str(status.user.friends_count)
                follower = str(status.user.followers_count)
                user_favourite = str(status.user.favourites_count)
                num_retweet = str(status.retweet_count)
                print(status.created_at, status.user.screen_name,user_location, tweet_loc_name, tweet_loc_cor, num_retweet,text,friend,follower,user_favourite)
                f.write('{},{},{},{},{},{},{},{},{},{}\n'.format(status.created_at, status.user.screen_name,user_location, tweet_loc_name, tweet_loc_cor, num_retweet,text,friend,follower,user_favourite))
            #        if status.text.startswith('RT @') == False:
    def on_error(self, status_code):
        print('Encountered error with status code:', status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        print('Timeout...')
        return True # Don't kill the stream
    
# send request
auth = tweepy.OAuthHandler("0Fb3ejpBVMiGY6Wj5Hc9GP753", "ATn8k1Xhf4poQyJejb5LNVjyxMxWu754875zfaVPWUMPbvgHFy")
auth.set_access_token("1206214771420192768-NXrcDvqsOEBpfK20jbnWUun6HEeSqY", "gEAKOpbKemObeX16TJH9YVybf0e3qY7yiXt7I3OLJmWKh")
api = tweepy.API(auth)

# set keywords to track
tracklist = ['Corona','Virus','Wuhan', 'China', 'COVID','nCov',
             'Novel virus','Pneumonia','Isolate', 'Outbreak',
             'Quarantine','Lockdown']
# Washington Rome London Singapore
region = [-77.1506,38.8457,-76.9126,39.0024,
          12.402444,41.811056,12.561822,41.963047,
          -0.404723,51.346458,0.1214,51.654595,
          103.680604,1.265325,103.96869,1.426108]
    
# STREAMING API: 1% OF TOTAL VOLUME
sapi = tweepy.streaming.Stream(auth, CustomStreamListener(), tweet_mode = 'extended',wait_on_rate_limit=True,wait_on_rate_limit_notify=True)    
sapi.filter(track = tracklist, languages = ['en'], locations= region) 