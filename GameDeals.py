import smtplib
import praw
import time
import io
import requests
import json
from twython import Twython, TwythonError

# Authentication for Twitter
twitter = Twython("ALyrXKsaa5XK05i8c4pU6w", "MVqiPCH03rRs0x5mvpFBWNfWQn6Xbctf4O6spbhh7E", "1473653377-9ZT2YeiO37q88c9duRtlUaUuaHD2wgu8CZy6bbR", "aRj0Pk2B1W7sCI04YqvZTqeTCo7OwhySy7QvhhCc")

# PRAW initialization
r = praw.Reddit('PRAW submission fetcher from r/gamedeals')

# URL for Google URL Shortener
gUrl = 'https://www.googleapis.com/urlshortener/v1/url'

# Already posted links
alreadyPosted = [line.strip() for line in open('PostedLinks.txt')]

def processSubmission(post):
    postTitle = post.title
    url = post.url
    redditURL = post.short_link
    return postTitle, url, redditURL
	 
def shortenURL(url):
    data = json.dumps({'longUrl': url})
    r = requests.post(gUrl, data, headers={'Content-Type': 'application/json'})
    j = json.loads(r.text)
    sURL = j['id']
    return sURL

# Function for sending emails containing deal information
def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()


subreddit = r.get_subreddit('gamedeals')

# Main execution loop
# Checks new posts against already posted deals
# Update already posted links and post new deals to Twitter
while(True):
	try:
		for submission in subreddit.get_new(limit=25):
			if submission.id not in alreadyPosted:
				
				postTitle, url, redditURL = processSubmission(submission)
				
				sURL = shortenURL(url)
				
				if len(postTitle) > 115:
					postTitle = postTitle[0:116]
					postTitle += "-"
					
				try:
					tStatus = ""+postTitle+" "+sURL
					twitter.update_status(status=tStatus)
					alreadyPosted.insert(0,submission.id)
					del alreadyPosted[-1]
				except TwythonError as e:
					print(e)
				except Exception as ee:
					print(ee)
				
				#loginN = "gmail account"
				#passw = "gmail password"
				
				#sendemail(from_addr    = 'yourgmailaddress@gmail.com', 
						  #to_addr_list = ['toaddress@gmail.com'],
						  #cc_addr_list = [], 
						  #subject      = postTitle, 
						  #message      = ""+postTitle+" "+url+" "+redditURL, 
						  #login        = loginN, 
						  #password     = passw)
		
		#Overwrites existing file containing already posted deals with 25 most-recent postings
		f = open('PostedLinks.txt', 'w')
		for post in alreadyPosted:
			f.write(""+post+"\n")
		f.close()
		time.sleep(900)
	except Exception as e:
		print "Error with connection \n"
		print(e)
		time.sleep(900)
            
