##########    CHANGE THIS TO SET CONFIGURATION FILE NAME    ###########
config_file_name = "config.txt"


from TwitterFollowBot import TwitterBot
from twitter import Twitter, OAuth, TwitterHTTPError
from random import randint
import time
from time import sleep
import colorama
from colorama import Fore, Style, Back, init
import subprocess
import os
os.system('cls' if os.name=='nt' else 'clear')
init(autoreset=True) 


#Helper function to truncate time
def truncate(x, d):
    return int(x*(10.0**d))/(10.0**d)

##### Introduction ######

#Twitter logo
print "\n"
if os.path.exists('twitterLogo.txt'):
	with open('twitterLogo.txt', 'r') as fin:
		print Fore.BLUE + Style.BRIGHT + fin.read()

#Print BotTweet
print "\n"
if os.path.exists('titleLogo.txt'):
	with open('titleLogo.txt', 'r') as fin:
		print Fore.BLUE + Style.BRIGHT + fin.read()
print "Copyright " + u"\u00a9" + " 2015 Brandon Jabr.\n"


#TO-DO: CHECK CONFIG FILE

#Load environment
TwitterAPI = TwitterBot(config_file_name)
username = TwitterAPI.BOT_CONFIG["TWITTER_HANDLE"]
print Style.BRIGHT + "\nCurrent User: " + Fore.BLUE + str(username)
TwitterAPI.sync_follows()
sessionTweets = 0
totalTweets = 0
skipTweets = []
currentID = None
maxID = None
userMaxID = None
tweet_type = ""
amount = 15
following = list(TwitterAPI.get_follows_list())
auto_follow = False

#Collect user input
while True:
	search_term = raw_input(Style.BRIGHT + "Please enter a phrase to search (with quotes): ")
	if len(search_term) != 0 and search_term[0] == "\"" and search_term[-1] == "\"":
		break
	else:
		print(Fore.RED + "Invalid Input: Please put quotes around your search phrase. Example: \"#botTweet\"")
        continue

while True:
    tweet_type = raw_input(Style.BRIGHT + "\nType of tweet to search (recent|popular|mixed): ")
    if tweet_type not in {'recent','popular','mixed'}:
        print(Fore.RED + "Invalid Input: Please type either recent, popular, or mixed. (Note: mixed means both popular and recent will be searched).")
        continue
    else:
        break

while True:
    amount = raw_input(Style.BRIGHT + "\nNumber to search per batch. (1-100): ")
    if not amount.isdigit():
        print(Fore.RED + "Invalid Input: Enter a number between 1 and 100. (Note this is tweets per batch, not total tweets to search.")
        continue
    elif amount > 100:
    	amount = 15
        break
    else:
    	break

while True:
    auto_follow_str = raw_input(Style.BRIGHT + "\nAutomatically follow users you retweet (yes|no): ")
    if auto_follow_str in {'yes','YES','Yes','y'}:
    	auto_follow = True
    	break
    elif auto_follow_str in {'no','NO','No','n'}:
    	auto_follow = False
    	break
    else:
    	print(Fore.RED + "Invalid input. Please enter yes or no.")
    	continue


############# Get all user tweets/retweets to skip #################
print Fore.LIGHTBLUE_EX + Style.NORMAL + "\nLoading tweets to skip (user already tweeted/retweeted)..."
print Fore.LIGHTBLUE_EX + Style.NORMAL + "This may take a few seconds."
for page in range(0,16):
	myTweets = None
	if userMaxID == None:
		myTweets = TwitterAPI.TWITTER_CONNECTION.statuses.user_timeline(screen_name=username,count=200)
	else:
		myTweets = TwitterAPI.TWITTER_CONNECTION.statuses.user_timeline(screen_name=username,count=200,max_id=userMaxID)

	for skipTweet in myTweets:
		if "retweeted_status" in skipTweet:
			if skipTweet["retweeted_status"]["retweeted"] == True:
				skipTweets.append(skipTweet["retweeted_status"]["id"])
		skipTweets.append(str(skipTweet["id"]))
		if skipTweet == myTweets[-1]:
			userMaxID = skipTweet["id"]

totalTweets = len(skipTweets)
print Fore.LIGHTBLUE_EX + Style.NORMAL + "Done."
sleep(1)
################################################################

###START###
time_start = time.time()
if os.path.exists('start.txt'):
	with open('start.txt', 'r') as fin:
		print Fore.GREEN + Style.BRIGHT + fin.read()
while True:
	pageRetweets = 0
	print (Fore.LIGHTBLUE_EX + Style.NORMAL + "Loading new results for: " + "'" + search_term + "'...")
	sleep(1)
	print (Fore.LIGHTBLUE_EX + Style.NORMAL + "Applying filters...\n\n")

	result = TwitterAPI.TWITTER_CONNECTION.search.tweets(q=search_term, count=100, result_type = "mixed",max_id=maxID)
	print (Fore.BLACK + Style.BRIGHT + "Found ") + (Fore.GREEN + Style.BRIGHT + str(len(result["statuses"]))) + (Fore.BLACK + Style.BRIGHT + " matches on current page.")
	
	if len(result["statuses"]) == 0:
		print Fore.YELLOW + Style.BRIGHT + "\nNo new results found, waiting 15-20 minutes for additional tweets.\n"
		sleep(900)
		continue
	

	print (Fore.GREEN + Style.BRIGHT + "Start Retweeting:\n")
	sleep(1)

	finishedTweets = 0
	for tweet in result["statuses"]:
		try:
			if "retweeted_status" in tweet:
				originalTweet = tweet["retweeted_status"]
				checkFollow = originalTweet["retweeted"]
				checkFollow2 = tweet["retweeted"]
				checkID = str(originalTweet["id"])

				checkRepeat = False
				if checkID in skipTweets:
					checkRepeat = True

				if checkFollow == False and checkFollow2 == False and checkRepeat == False:
					currentID = originalTweet["id"]
					TwitterAPI.TWITTER_CONNECTION.statuses.retweet(id=originalTweet["id"])
					sessionTweets = sessionTweets + 1
					print Fore.BLUE + Style.BRIGHT + "\nRetweeted: '" + Style.RESET_ALL +  originalTweet["text"] + "'"

					getUser = originalTweet["user"]["id"]
					getHandle = originalTweet["user"]["screen_name"]

					#Auto-Follow
					if auto_follow is True:
						TwitterAPI.TWITTER_CONNECTION.friendships.create(user_id=getUser, follow=True)
						following.append(originalTweet["user"]["id"])
						print Fore.MAGENTA + Style.BRIGHT + "Followed: " +  Style.RESET_ALL + str(getHandle) + ""

					print "\n"
					print Style.BRIGHT + "Retweets: " +  Fore.BLUE + str(sessionTweets) + Fore.BLACK
					if auto_follow is True:
						print Style.BRIGHT + "Follows: " +  Fore.MAGENTA + str(sessionTweets) + Fore.BLACK
					print Style.BRIGHT + Fore.BLACK + "Runtime: " + Fore.GREEN + str(truncate((time.time() - time_start),2)) + "s\n"
					pageRetweets = pageRetweets + 1
					print Fore.LIGHTBLUE_EX + Style.NORMAL+ "\nWaiting for 45-60 seconds...\n"
					sleep(randint(45, 60))

		except TwitterHTTPError as api_error:
			if "rate limit" in str(api_error).lower():
				if os.path.exists('stop.txt'):
					with open('stop.txt', 'r') as fin:
						print Fore.RED + Style.BRIGHT + fin.read()
				print (Fore.RED + Style.BRIGHT + "\nYou have reached your rate limit. Sleeping for 15 minutes.\n")

				sleep(950)
			elif "status update limit" in str(api_error).lower():
				if os.path.exists('stop.txt'):
					with open('stop.txt', 'r') as fin:
						print Fore.RED + Style.BRIGHT + fin.read()
				print (Fore.RED + Style.BRIGHT + "\nYou have reached your status update limit. Sleeping for 15 minutes...\n")
				sleep(950)
			elif "already retweeted" in str(api_error).lower():
				skipTweets.append(str(currentID))

		finally:
			finishedTweets = finishedTweets + 1
			if finishedTweets == len(result["statuses"]):
				#load next page
				maxID = currentID
				print (Style.BRIGHT + "\n\n---- Page finished with ") + (Fore.GREEN + Style.BRIGHT + str(pageRetweets)) + (Style.BRIGHT + Fore.BLACK +  " new retweets (" + (Fore.BLUE + Style.BRIGHT + str(sessionTweets)) + " total" + Style.BRIGHT + Fore.BLACK + "). Loading new page of tweets. ----\n\n")
				sleep(randint(2,5))
