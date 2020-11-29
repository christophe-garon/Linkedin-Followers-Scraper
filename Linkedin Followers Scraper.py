#!/usr/bin/env python
# coding: utf-8

# In[257]:


#required installs (i.e. pip3 install in terminal): pandas, selenium, bs4, and possibly chromedriver(it may come with selenium)
#Download Chromedriver from: https://chromedriver.chromium.org/downloads
#To see what version to install: Go to chrome --> on top right click three dot icon --> help --> about Google Chrome
#Move the chrome driver to (/usr/local/bin) -- open finder -> Command+Shift+G -> search /usr/local/bin -> move from downloads

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd
import re


#accessing Chromedriver
browser = webdriver.Chrome('chromedriver')


#Replace with you username and password
username = "topgaron@gmail.com"
password = "garon2395"

#Open login page
browser.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

#Enter login info:
elementID = browser.find_element_by_id('username')
elementID.send_keys(username)

elementID = browser.find_element_by_id('password')
elementID.send_keys(password)
elementID.submit()


#Go to company webpage
browser.get('https://www.linkedin.com/company/rei/')


# In[258]:


likers = browser.find_element_by_class_name('social-details-social-counts__count-value')
likers.click()
time.sleep(3)


# In[ ]:


#Function that estimates user age based on earliest school date or earlier work date
def est_age():

    browser.switch_to.window(browser.window_handles[1])
    date = datetime.today()
    current_year = date.strftime("%Y")
    school_start_year = current_year
    work_start_year = current_year
    
    #Get page source
    user_profile = browser.page_source
    user_profile = bs(user_profile.encode("utf-8"), "html")
    user_profile.prettify()
    
    #Look for earliest university start date
    try:
        grad_year = user_profile.findAll('p',{"class":"pv-entity__dates t-14 t-black--light t-normal"})
        
        for d in grad_year:
            year = d.find('time').text.strip().replace(' ', '')
            year = re.sub(r'[a-zA-Z]', r'', year)
            if year < school_start_year:
                school_start_year = year
        
        #Estimate age based on avg university start age of 18
        est_birth_year = int(school_start_year) - 18
        est_age = int(current_year) - est_birth_year
        
    except:
        
        #If no university start date, get earlier work date 
        try:       
            try:
                browser.find_element_by_xpath("//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link-without-visited-state']").click()
            except:
                time.sleep(2)
                pass
        
            work_start = user_profile.findAll('h4', {"class":"pv-entity__date-range t-14 t-black--light t-normal"})

            for d in work_start:
                start_date = d.find('span',class_=None)
                start_date = start_date.text.strip()
                start_year = start_date[4:8]
                if start_year < work_start_year:
                    work_start_year = start_year
            
            #Estimate age based on avg post college work start date of 22
            est_birth_year = int(work_start_year) - 22
            est_age = int(current_year) - est_birth_year
                               
        except:
            est_age = "unknown"
            
    return est_age

        


# In[261]:


#Lists of the data we will collect
liker_names = []
liker_locations = []
liker_headlines = []
user_bios = []
est_ages = []


#Function that Scrapes user data
def get_user_data():
    browser.switch_to.window(browser.window_handles[1])
    user_profile = browser.page_source
    user_profile = bs(user_profile.encode("utf-8"), "html")
    user_profile.prettify()
    
    #Get Liker Name
    name = user_profile.find('li',{'class':"inline t-24 t-black t-normal break-words"})
    liker_names.append(name.text.strip())
    
    #Get Liker Location
    location = user_profile.find('li',{'class':"t-16 t-black t-normal inline-block"})
    liker_locations.append(location.text.strip())
    
    #Get Liker Headline
    headline = user_profile.find('h2',{"class":"mt1 t-18 t-black t-normal break-words"})
    liker_headlines.append(headline.text.strip())
    
    #Get estimated age using our age function
    age = est_age()
    est_ages.append(age)

    
    #Get Liker Bio
    try:
        browser.find_element_by_class_name("lt-line-clamp__more").click()
        bio = user_profile.find("span",{"class":"lt-line-clamp__raw-line"})
        user_bios.append(bio.text.strip())
    except:
        try:
            bio = user_profile.find('p',{"class":"pv-about__summary-text mt4 t-14 ember-view"})
            user_bios.append(bio.text.strip())
        except:
            user_bios.append('No Bio')
            pass
    
#     try:
#         #Get estimated age using our age function
#         est_age = est_age()
#         print(est_age)
#         est_ages.append(est_age)
#     except:
#         est_ages.append('unknown')


# In[262]:


# def scroll():
#     #Simulate scrolling to capture all posts
#     SCROLL_PAUSE_TIME = 1.5

#     # Get scroll height
#     last_height = browser.execute_script("return document.body.scrollHeight")

#     while True:
#         # Scroll down to bottom
#         browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#         # Wait to load page
#         time.sleep(SCROLL_PAUSE_TIME)

#         # Calculate new scroll height and compare with last scroll height
#         new_height = browser.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height


# In[ ]:


def export_df():
    #Constructing Pandas Dataframe
    data = {
        "Name": liker_names,
        "Location": liker_locations,
        "Age": est_ages,
        "Headline": liker_headlines,
        "Bio": user_bios

    }

    df = pd.DataFrame(data)


    #Exporting csv to program folder
    df.to_csv("linkedin_page_followers.csv", encoding='utf-8', index=False)

    #Export to Excel
    writer = pd.ExcelWriter("linkedin_page_followers.xlsx", engine='xlsxwriter')
    df.to_excel(writer, index =False)
    writer.save()


# In[263]:


#Iterate through the list of users who engaged with post and collect their info

i=1

while i != 0:
    try:
        path = "//ul[@class='artdeco-list artdeco-list--offset-1']/li[{}]".format(i) 
        user_page = browser.find_element_by_xpath(path)
        user_page.click()
        time.sleep(2)

        # Switch to the new window and open URL B
        browser.switch_to.window(browser.window_handles[1])
        print(i)
        
#         scroll()
        time.sleep(1)
        get_user_data()

        # Close the tab with URL B
        browser.close()
        # Switch back to the first tab with URL A
        browser.switch_to.window(browser.window_handles[0])

        #Iterate save progress if multiple of 10
        i+=1
        if i % 10 == 0:
            export_df()
        else:
            time.sleep(1)

    except:
        i=0


# In[242]:


# #Constructing Pandas Dataframe
# data = {
#     "Name": liker_names,
#     "Location": liker_locations,
#     "Age": est_ages,
#     "Headline": liker_headlines,
#     "Bio": user_bios
    
# }

# df = pd.DataFrame(data)


# #Exporting csv to program folder
# df.to_csv("linkedin_page_followers.csv", encoding='utf-8', index=False)

# #Export to Excel
# writer = pd.ExcelWriter("linkedin_page_followers.xlsx", engine='xlsxwriter')
# df.to_excel(writer, index =False)
# writer.save()


# In[ ]:




