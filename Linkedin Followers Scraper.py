#!/usr/bin/env python
# coding: utf-8

# In[862]:


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
import caffeine
import random
import schedule

caffeine.on(display=True)

#accessing Chromedriver
browser = webdriver.Chrome('chromedriver')


#Replace with you username and password
username = "username"
password = "password"

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
time.sleep(2)


# In[863]:


likers = browser.find_element_by_class_name('social-details-social-counts__count-value')
likers.click()
time.sleep(2)


# In[ ]:


#Scrolls the main page
def scroll():
    #Simulate scrolling to capture all posts
    SCROLL_PAUSE_TIME = 1.5

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# In[977]:


#Scrolls popups
def scroll_popup(class_name):
    #Simulate scrolling to capture all posts
    SCROLL_PAUSE_TIME = 1.5

    # Get scroll height
    js_code = "return document.getElementsByClassName('{}')[0].scrollHeight".format(class_name)
    last_height = browser.execute_script(js_code)

    while True:
        # Scroll down to bottom
        path = "//div[@class='{}']".format(class_name)
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", browser.find_element_by_xpath(path))

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script(js_code)
        if new_height == last_height:
            break
        last_height = new_height


# In[738]:


#Function that estimates user age based on earliest school date or earlier work date
def est_age():

    browser.switch_to.window(browser.window_handles[1])
    date = datetime.today()
    current_year = date.strftime("%Y")
    school_start_year = "9999"
    work_start_year = "9999"

    #Get page source
    user_profile = browser.page_source
    user_profile = bs(user_profile.encode("utf-8"), "html")


    #Look for earliest university start date
    try:
        grad_year = user_profile.findAll('p',{"class":"pv-entity__dates t-14 t-black--light t-normal"})
        
        if grad_year == []:
            browser.execute_script("window.scrollTo(0, 1000);")
            user_profile = browser.page_source
            user_profile = bs(user_profile.encode("utf-8"), "html")
            grad_year = user_profile.findAll('p',{"class":"pv-entity__dates t-14 t-black--light t-normal"})
            
        
        for d in grad_year:
            year = d.find('time').text.strip().replace(' ', '')
            start_year = re.sub(r'[a-zA-Z]', r'', year)
            start_year = start_year[0:4]
            if start_year < school_start_year:
                        school_start_year = start_year
    except:
        pass
    

    #Look for earlies work date
    try:
        #Click see more if it's there
        try:
            browser.find_element_by_xpath("//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link-without-visited-state']").click()
        except:
            time.sleep(1)
            pass

        work_start = user_profile.findAll('h4', {"class":"pv-entity__date-range t-14 t-black--light t-normal"})


        for d in work_start:
            start_date = d.find('span',class_=None)
            start_date = start_date.text.strip().replace(' ', '')
            start_date = re.sub(r'[a-zA-Z]', r'', start_date)
            start_year = start_date[0:4]
            if start_year < work_start_year:
                    work_start_year = start_year
    except:
        pass

    # Compare work and school start dates to avoid adult degress
    if school_start_year < work_start_year:
        #Estimate age based on avg university start age of 18
        est_birth_year = int(school_start_year) - 18
        est_age = int(current_year) - est_birth_year

    else:
        #Estimate age based on avg post college work start date of 22
        est_birth_year = int(work_start_year) - 22
        est_age = int(current_year) - est_birth_year

    if est_age == -7961 or est_age == -7957:
        est_age = 'unknown'
    
    return est_age
        


# In[887]:


#Lists of the data we will collect
liker_names = []
liker_locations = []
liker_headlines = []
user_bios = []
est_ages = []
influencers = []
companies = []

#Function that Scrapes user data
def get_user_data():
    browser.switch_to.window(browser.window_handles[1])
    user_profile = browser.page_source
    user_profile = bs(user_profile.encode("utf-8"), "html")
    
    #Get Liker Name
    name = user_profile.find('li',{'class':"inline t-24 t-black t-normal break-words"})
    liker_names.append(name.text.strip())
    
    #Get Liker Location
    location = user_profile.find('li',{'class':"t-16 t-black t-normal inline-block"})
    liker_locations.append(location.text.strip())
    
    #Get Liker Headline
    headline = user_profile.find('h2',{"class":"mt1 t-18 t-black t-normal break-words"})
    liker_headlines.append(headline.text.strip())
    

    #Get Liker Bio
    try:
        browser.find_element_by_xpath("//a[@id='line-clamp-show-more-button']").click()
        time.sleep(1)
        user_profile = browser.page_source
        user_profile = bs(user_profile.encode("utf-8"), "html")
        bio = user_profile.findAll("span",{"class":"lt-line-clamp__raw-line"})
        user_bios.append(bio[0].text.strip())
    except:
        try:
            bio_lines = []
            bios = user_profile.findAll('span',{"class":"lt-line-clamp__line"})
            for b in bios:
                bio_lines.append(b.text.strip())
            bio = ",".join(bio_lines).replace(",", ". ")
            user_bios.append(bio)
            
        except:
            user_bios.append('No Bio')
            pass
    
    #Get estimated age using our age function
    age = est_age()
    est_ages.append(age)


# In[980]:


#Lists of the data we will collect
liker_names = []
liker_locations = []
liker_headlines = []
user_bios = []
est_ages = []
influencers = []
companies = []

#Function that Scrapes user data
def get_user_data():
    browser.switch_to.window(browser.window_handles[1])
    user_profile = browser.page_source
    user_profile = bs(user_profile.encode("utf-8"), "html")
    
    #Get Liker Name
    name = user_profile.find('li',{'class':"inline t-24 t-black t-normal break-words"})
    liker_names.append(name.text.strip())
    
    #Get Liker Location
    location = user_profile.find('li',{'class':"t-16 t-black t-normal inline-block"})
    liker_locations.append(location.text.strip())
    
    #Get Liker Headline
    headline = user_profile.find('h2',{"class":"mt1 t-18 t-black t-normal break-words"})
    liker_headlines.append(headline.text.strip())
    

    #Get Liker Bio
    try:
        browser.find_element_by_xpath("//a[@id='line-clamp-show-more-button']").click()
        time.sleep(1)
        user_profile = browser.page_source
        user_profile = bs(user_profile.encode("utf-8"), "html")
        bio = user_profile.findAll("span",{"class":"lt-line-clamp__raw-line"})
        user_bios.append(bio[0].text.strip())
    except:
        try:
            bio_lines = []
            bios = user_profile.findAll('span',{"class":"lt-line-clamp__line"})
            for b in bios:
                bio_lines.append(b.text.strip())
            bio = ",".join(bio_lines).replace(",", ". ")
            user_bios.append(bio)
            
        except:
            user_bios.append('No Bio')
            pass
    
    #Get estimated age using our age function
    age = est_age()
    est_ages.append(age)
    
    
    #Click see more on user interests
    try: 
        interest_path = "//a[@data-control-name='view_interest_details']"
        browser.find_element_by_xpath(interest_path).click()
    except:
        scroll()
        time.sleep(1)
        try:
            interest_path = "//a[@data-control-name='view_interest_details']"
            browser.find_element_by_xpath(interest_path).click()
        except:
            #append no interests to lists
            pass
    
    time.sleep(1)
    
    #Scrape the influencers the user follows
    try:
        influencer_path = "//a[@id='pv-interests-modal__following-influencers']"
        browser.find_element_by_xpath(influencer_path).click()
        
        #Scroll the end of list
        class_name = 'entity-all pv-interests-list ml4 pt2 ember-view'
        #interest_box_path = "//div[@class='entity-all pv-interests-list ml4 pt2 ember-view']"
        scroll_popup(class_name)
        
        influencer_page = browser.page_source
        influencer_page = bs(influencer_page.encode("utf-8"), "html")
        influencer_list = influencer_page.findAll("li",{"class":"entity-list-item"})
        
        user_influencers = []
        for i in influencer_list:
            name = i.find("span",{"class":"pv-entity__summary-title-text"})
            user_influencers.append(name.text.strip())
               
        influencers.append(user_influencers)
        
    except:
        influencers.append("No Influencers")


    
    #Scrape the companies the user follows
    try:
        company_path = "//a[@id='pv-interests-modal__following-companies']"
        browser.find_element_by_xpath(company_path).click()
        
        time.sleep(2)
        
        #Scroll the end of list
        class_name = 'entity-all pv-interests-list ml4 pt2 ember-view'
        #interest_box_path = "//div[@class='entity-all pv-interests-list ml4 pt2 ember-view']"
        scroll_popup(class_name)
        
    
        company_page = browser.page_source
        company_page = bs(company_page.encode("utf-8"), "html")
        company_list = company_page.findAll("li",{"class":"entity-list-item"})
        
        user_companies = []
        for i in company_list:
            name = i.find("span",{"class":"pv-entity__summary-title-text"})
            user_companies.append(name.text.strip())
               
        companies.append(user_companies)
        
    except:
        companies.append("No Companies")
        


# In[883]:


# companies = []

# #Scrape the companies the user follows
#     try:
#         company_path = "//a[@id='pv-interests-modal__following-companies']"
#         browser.find_element_by_xpath(company_path).click()
        
#         time.sleep(2)
        
#         #Scroll the end of list
#         class_name = 'entity-all pv-interests-list ml4 pt2 ember-view'
#         #interest_box_path = "//div[@class='entity-all pv-interests-list ml4 pt2 ember-view']"
#         scroll_popup(class_name)
        
    
#         company_page = browser.page_source
#         company_page = bs(company_page.encode("utf-8"), "html")
#         company_list = company_page.findAll("li",{"class":"entity-list-item"})
        
#         user_companies = []
#         for i in company_list:
#             name = i.find("span",{"class":"pv-entity__summary-title-text"})
#             user_companies.append(name.text.strip())
               
#         companies.append(user_companies)
        
#     except:
#         companies.append("No Companies")


# In[885]:


# influencers = []

# #Scrape the influencers the user follows
#     try:
#         influencer_path = "//a[@id='pv-interests-modal__following-influencers']"
#         browser.find_element_by_xpath(influencer_path).click()
        
#         #Scroll the end of list
#         class_name = 'entity-all pv-interests-list ml4 pt2 ember-view'
#         #interest_box_path = "//div[@class='entity-all pv-interests-list ml4 pt2 ember-view']"
#         scroll_popup(class_name)
        
#         influencer_page = browser.page_source
#         influencer_page = bs(influencer_page.encode("utf-8"), "html")
#         influencer_list = influencer_page.findAll("li",{"class":"entity-list-item"})
        
#         user_influencers = []
#         for i in influencer_list:
#             name = i.find("span",{"class":"pv-entity__summary-title-text"})
#             user_influencers.append(name.text.strip())
               
#         influencers.append(user_influencers)
        
#     except:
#         influencers.append("No Influencers")
        


# In[731]:


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


# In[734]:


def current_time():
    current_time = datetime.now().strftime("%H:%M")
    return current_time


#Liker link number we will iterate to the path
i=1
#Scoll length we will iterate
l=500
#The path of the block that we need to select to scroll
block_path = "//div[@class='artdeco-modal__content social-details-reactors-modal__content ember-view']"


# In[735]:



while True:
    
    time.sleep(random.randint(3,15))
    
    path = "//ul[@class='artdeco-list artdeco-list--offset-1']/li[{}]".format(i) 
    user_page = browser.find_element_by_xpath(path)
    user_page.click()

    time.sleep(random.randint(1,3))

    # Switch to the new window and scroll and retry if it wasn't found
    try:
        browser.switch_to.window(browser.window_handles[1])
    except:
        print("One sec, I need to scroll")
        browser.execute_script("arguments[0].scrollTop = arguments[1];",browser.find_element_by_xpath(block_path), l);
        time.sleep(2)
        l += 500
        path = "//ul[@class='artdeco-list artdeco-list--offset-1']/li[{}]".format(i) 
        user_page = browser.find_element_by_xpath(path)
        user_page.click()
        browser.switch_to.window(browser.window_handles[1]) 
        pass
    
    time.sleep(random.randint(2,5))
    get_user_data()

    # Close the tab with URL B
    browser.close()
    # Switch back to the first tab with URL A
    browser.switch_to.window(browser.window_handles[0])

    #Iterate save progress if multiple of 10
    i+=1
    if i % 10 == 0:
        export_df()
        print(i)
        
        #Random long sleep function to prevent linkedin rate limit
        time.sleep(random.randint(20,1200))
       
        #Stop for the night
        while current_time() < "07:05":
            schedule.run_pending()
            time.sleep(60)
            
    else:
        time.sleep(1)


# In[ ]:




