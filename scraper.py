import requests
import json
import re
from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords

last_tweet_id = ''
all_words = []
all_images = []
common_words = set(stopwords.words('english'))


def get_latest_tweet_id(tweets):
    global last_tweet_id
    tweets_id = [tweet['data-item-id'] for tweet in tweets]
    last_tweet_id = tweets_id[len(tweets_id) - 1]


def get_words_from_tweets(data):
    global all_words
    soup = BeautifulSoup(data, 'html.parser')
    tweets = [tweet for tweet in soup.findAll('div', class_='tweet')]
    get_latest_tweet_id(tweets)
    tweet_texts = [p.text for p in soup.findAll('p', class_='tweet-text')]

    for tweet in tweet_texts:
        for word in tweet.split():
            if re.search('(http)s?(://)', word):
                split_word = word.split('http')[0].lower()
                if split_word not in common_words:
                    all_words.append(split_word)
            elif re.search('pic.twitter.com', word):
                split_word = word.split('pic.twitter.com')[0].lower()
                if split_word not in common_words:
                    all_words.append(split_word)
            else:
                if word not in common_words:
                    all_words.append(word.lower())


def get_images_from_tweets(data):
    global all_images
    soup = BeautifulSoup(data, 'html.parser')

    image_containers = [image for image in soup.findAll("div", class_='AdaptiveMedia')]
    for image_container in image_containers:
        images = [img for img in image_container.findAll('img')]
        for image in images:
            all_images.append(image['src'])


base_url = u'https://twitter.com/'
query = u'realDonaldTrump'
next_page = u'i/profiles/show/' + query + '/timeline/tweets?include_available_features=1&include_entities=1&max_position='

request = requests.get(base_url + query)
get_words_from_tweets(request.text)
get_images_from_tweets(request.text)

for _ in range(10):
    request = requests.get(base_url + next_page + last_tweet_id)
    data = json.loads(str(request.text))
    get_words_from_tweets(data['items_html'])
    get_images_from_tweets(data['items_html'])

counter = Counter()
counter.update(all_words)

#print(len(all_words))

print(counter.most_common())
print(all_images)
