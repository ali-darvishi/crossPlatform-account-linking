# For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
# For displaying the data after
import pandas as pd
# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
import unicodedata
#To add wait time between requests
import time
import pandas as pd

from datetime import datetime, timezone, timedelta


from twarc_csv import CSVConverter
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened

import praw

# Input credentials:

# Client_id = input("Please enter your Reddit Client id:")
# Client_secret = input("Please enter your Reddit Client secret:")
# Username = input("Please enter your Reddit Username:")
# Password = input("Please enter your Reddit Password:")
# Token = input("Please enter your Twitter API bearer token:")

# OR read credential from a text file:
for line in open("credential.txt","r").readlines(): # Read the lines
    credential=line.split()
Client_id = credential[0]
Client_secret = credential[1]
Username = credential[2]
Password = credential[3]
Token = credential[4]

# Reddit and Twitter APIs 
r = praw.Reddit(client_id= Client_id,
                client_secret=Client_secret,
                username= Username,
                password= Password,
                user_agent='UQ_RA_A/0.0.2')

t = Twarc2(bearer_token = Token)

# Functions to Check if user exists in:

## Reddit

from prawcore.exceptions import NotFound
def user_exists(name):
    try:
        r.redditor(name).id
    except NotFound:
        return False
    except: 
        pass #pass other exceptions 
    return True

## Twitter

def Twitter_user_exists(name):
    try:
        t.timeline(name)
    except ValueError:
        return False
    except: 
        pass #pass other exceptions 
    return True


# Read crosslinked usernames


users = pd.read_csv ('users.csv')
users.info()


# Collect data


fields = ( 'author','author_fullname', 'body', 'link_title','created_utc', 'id','link_id','parent_id','permalink','score','send_replies','subreddit_name_prefixed','link_url')
for i in range(118,len(users)): #len(users)
    if user_exists(users['Reddit_username'][i]): # Check if Reddit user exists
        if getattr(r.redditor(users['Reddit_username'][i]), 'is_suspended', False): # Check if Reddit user is suspended
            with open('Deleted_users.txt', 'a') as f:
                f.write(str(i) + ' Suspended Reddit username: ' + users['Reddit_username'][i]+'\n') # Save Suspended users in a text file
                print('Suspended user reddit:'+str(i) + '_' + users['Reddit_username'][i])
        elif Twitter_user_exists(users['author.username'][i]):
            list_of_items = []
            user = r.redditor(users['Reddit_username'][i])
            for comment in user.comments.new(limit=100):
                to_dict = vars(comment)
                to_dict['author'] = users['Reddit_username'][i]
                sub_dict = {field:to_dict[field] for field in fields}
                list_of_items.append(sub_dict)
            json_str = json.dumps(list_of_items)
            with open(str(i) + '_' + str(users['Reddit_username'][i])+'_reddit.json', 'w') as f:
                json.dump(list_of_items, f)            
            search_results = t.timeline(users['author.username'][i], max_results=100,exclude_retweets=True)
            for page in search_results:
                with open(str(i) + '_' + str(users['author.username'][i])+'_tweet.json', 'w') as f:
                    f.write(json.dumps(page) )
                break
        else:
            with open('Deleted_users.txt', 'a') as f:
                f.write(str(i) + ' Deleted Twitter username: ' + users['author.username'][i]+'\n') # Save Deleted users in a text file
                print('Deleted user Twitter: '+str(i) + '_' + users['author.username'][i])         
    else:
        with open('Deleted_users.txt', 'a') as f:
            f.write(str(i) + ' Deleted Reddit username: ' + users['Reddit_username'][i]+'\n') # Save Deleted users in a text file
            print('Deleted user reddit: '+str(i) + '_' + users['Reddit_username'][i])
    print("User Number: {}".format(i))

