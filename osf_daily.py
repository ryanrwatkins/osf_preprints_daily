# script to get an email with yesterdays osf preprints (typically 30 to 40 per day)
# I use a free Deepnote.com account to schedule this script to run each day (if you don't want to do that, you can put it on your server and use a CRON to run it each day)
# in Deepnote you use the drop down from the "run notebook" button to schedule the script to run once a day


import json
import requests 

# you can install langdetect in your environment, or you can !PIP install each time the script runs (once a day). For Deepnote I installed in the environment with a requirements.txt file. 
#This will be used to check the article description to see if it is in English.
from langdetect import detect

from datetime import date
from datetime import timedelta
today = date.today()
yesterday = str(today - timedelta(days = 1))

# get all preprints from yesterday
osf_api = 'https://api.osf.io/v2/preprints/?filter%5Bdate_created%5D=' + yesterday  

# api comes in 10 per page so we collect all the pages into one
osf_api = requests.get(osf_api).json()
all_articles = osf_api["data"]
while osf_api["links"]["next"]:
    osf_api = requests.get(osf_api["links"]["next"]).json()
    all_articles.extend(osf_api["data"])  

# We get the desired information for each article in the api return
todays_articles = "" 
for i in enumerate(all_articles):
    #first we get only the English language articles, then we take out any subject areas we are not interested in
    if (detect(i[1]['attributes']['description']) == "en") and (i[1]['attributes']['subjects'][0][0]['text'] not in ( "Psychiatry", "Medicine and Health Sciences", "Life Sciences")):
        article = "<b>" + i[1]['attributes']['subjects'][0][0]['text'] +"</b><p><b><font size='+2'><a href='" + i[1]['links']['html'] + "' target='_blank'>" + i[1]['attributes']['title'] + "</a></b></font>" +"<br>Open Data: " + i[1]['attributes']['has_data_links'] +"<br>Pre-registration: " + i[1]['attributes']['has_prereg_links']
        todays_articles += str(article) + "\n\n<p><p>"

# in order to email it we have to add a break \n between the header and message, so we put it at the beginning. We also remove all non-ascii characters.
todays_articles = "\n" + todays_articles.encode("ascii", errors="ignore").decode()

#option for printing test runs
#print(todays_articles)


#this will email the resulting "todays_articles"
import smtplib
from email.mime.text import MIMEText

# Set Global Variables
gmail_user = 'YOUR @gmail.com'  
gmail_password = 'YOUR Gmail APP password'    #this is an app password not your personal password, instructions for setting this up are found at: https://support.google.com/accounts/answer/185833?hl=en

# to and from
mail_from = gmail_user
mail_to = ['YOUR @kill-the-newsletter.com', 'YOUR OTHER EMAILS']  #the first email address creates an RSS feed using https://kill-the-newsletter.com/

# create message
msg = MIMEText(todays_articles, 'html') 
msg['Subject'] = 'OSF articles for ' + yesterday
msg['From'] = mail_from
msg['To'] = ", ".join(mail_to)   #this allows for multiple recipients

# Send
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(gmail_user, gmail_password)
server.sendmail(mail_from, mail_to, msg.as_string())
server.close()


