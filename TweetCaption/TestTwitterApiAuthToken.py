
import requests
import json
import Config

def getTweetsIds(username, fromDate, toDate):
    data = {
      'grant_type': 'client_credentials'
    }

    response = requests.post(Config.twitter_token_url, data=data,
                             auth=(Config.twitter_api_key, Config.twitter_api_secret_key))

    result_as_json = json.loads(response.text)
    token = '{0} {1}'.format(result_as_json['token_type'], result_as_json['access_token'])

    headers = {
        'authorization': token,
        'content-type': 'application/json',
    }

    data = '{ "query":"from:' + username + '",  "maxResults": "500", "fromDate":"' \
           + fromDate + '", "toDate":"' + toDate + '" }'

    response = requests.post(Config.twitter_search_url, headers=headers, data=data)

    result_as_json = json.loads(response.text)
    tweets = result_as_json['results']

    tweet_ids = []
    index = 0
    while index < len(tweets):
        tweet_ids.append(tweets[index]['id_str'])
        index += 1

    return tweet_ids
