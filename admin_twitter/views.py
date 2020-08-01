from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from keras.models import load_model
import pickle
from keras.preprocessing import text, sequence
from tweets.models import Tweet
from accounts.models import UserProfile
from django.contrib.auth import get_user_model

from pprint import pprint
from collections import Counter
from hashtags.models import HashTag
# import emoji
# import re
# import sys
import numpy as np
import os
# Create your views here.


def analyze(request):
	return 1 
def admin_home(request):
	if request.method == 'POST' and 'run_script' in request.POST:
		user_rating = Counter()
		user_rating_list = []
		toxic_tweets = []
		normal_tweets = []
		hashtag_rating = []
		pwd = os.path.dirname(__file__)
		flag = 0
		remodel = load_model(pwd + "\\toxic_model.h5")
		pickle_in = open(pwd +"\\token.pkl","rb")
		tok = pickle.load(pickle_in)
		max_features = 20000
		maxlen = 100
		tweets = Tweet.objects.all()
		for tweet in tweets:
			tweet_text = tweet.content
			user_username = tweet.user.username
			user = tweet.user
			X = [tweet_text]
			X = [x.lower() for x in X]
			list_tokenized_test = tok.texts_to_sequences(X)
			X_te = sequence.pad_sequences(list_tokenized_test, maxlen=maxlen)
			preds = remodel.predict(X_te)
			threshold = np.float32(0.7)
			p = UserProfile.objects.filter(user = user).get()
			print(p.rating)
			# user_rating[user] += p.rating
			for pred in preds[0]:
			    if(pred>threshold):
			        print("Yes")
			        toxic_tweet = {'User' : user_username , 'tweet' : tweet_text , 'prediction' : 'Toxic' , 'status':'Deleted'}
			        toxic_tweets.append(toxic_tweet)
			        p.rating+= -20
			        p.save()
			        # user_rating[user] = p.rating
			        print(p.rating)
			        flag=1
			        tweet.delete()
			        break
			if(flag==0):
				normal_tweet = {'User' : user_username , 'tweet' : tweet_text , 'prediction' : 'Not Toxic' , 'status' : 'Not Deleted'}
				normal_tweets.append(normal_tweet)
				# user_rating[user] += 0
				print("No")
			flag=0
		pprint(toxic_tweets)
		print()
		pprint(normal_tweets)
		User = get_user_model()
		superuser = User.objects.filter(is_superuser=True).get()
		profiles = UserProfile.objects.all().exclude(user = superuser)
		for profile in profiles:
			rating = profile.rating
			if(rating<=(-100)):
				user_element  = {'User' : profile.user.username , 'rating' : rating , 'status' : 'Deleted'}
				profile.user.delete()
			else:
				user_element  = {'User' : profile.user.username , 'rating' : rating , 'status' : 'Not Deleted'}
			user_rating_list.append(user_element)
		pprint(user_rating_list)
		hashtags = HashTag.objects.all()
		for hashtag in hashtags:
			tweet_hashtag  = Tweet.objects.filter(content__icontains="#" + hashtag.tag)
			if(len(tweet_hashtag)==0):
				h = {'hashtag' : hashtag , 'status' : 'Deleted'}
				hashtag_rating.append(h)
				hashtag.delete()
			else:
				h  = {'hashtag' : hashtag , 'status' : 'Not Deleted'}
				hashtag_rating.append(h)
		return render(request,'admin_twitter/analysis.html' , {'normal_tweets' : normal_tweets , 'toxic_tweets' : toxic_tweets , 'user_rating_list' : user_rating_list , 'hashtag_rating' : hashtag_rating})

			
		# tweets[0].delete()
		
    # import function to run
	    # from path_to_script import function_to_run

	    # # call function
	    # function_to_run() 

	    # # return user to required page
	    # return render(request, 'admin_twitter/admin_home.html')

	return render(request, 'admin_twitter/admin_home.html')