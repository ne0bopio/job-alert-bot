import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from job_source.utils import send_telegram_notification # Import the function you just made
import time
from job_source.models import JobSource, JobPost




def test_one_url():
    service = Service(executable_path="/Users/z-tek/Desktop/Job_Alert_EE_Api/job_alert_api/job_source/services/chromedriver")
    driver = webdriver.Chrome(service=service)
    source = JobSource.objects.get(id=2) #id 2 is cv.ee
    
    # Use a specific URL that you know has a long description
    test_url = "https://cv.ee/en/vacancy/1498749/seb/junior-mid-software-developer-in-finance-risk-and-data-tribe-or-seb-tallinn"
    
    scrape_single_job(driver, test_url, source=source, location_name="Tallinn")

    time.sleep(11)  # Pause to see the result before closing
    
    driver.quit()


def scrape_single_job(driver, job_url, source, location_name):
    print(f"--> Scraping details for {job_url} ")
    driver.get(job_url)

    
    #headers = {
    #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    #}

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1")) 
        )
    except Exception as e:
        print(f"Error loading job page: {e}")
        return
    
    # parse the rendered HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #title 
    title_tag = soup.select_one('h1')
    title_text = title_tag.text.strip() if title_tag else 'No Title Found'
   

    #company
    company = 'No Company Found'
    company_tag = soup.select_one('a[href*="/employer/"]')

    if company_tag:
        company = company_tag.get_text().strip()
    else:
        print("Company tag not found.")


    # Description

    desc_tags = soup.select('div.vacancy-details p')
    brief_description = "No brief description found."

    if desc_tags:
        keywords = ["Job description", "Tasks", "About the role", "Duties", "Töö kirjeldus", "Ülesanded"]
        for i, p in enumerate(desc_tags):
            text = p.get_text(strip=True)

            # Check if this paragraph contains our keywords
            if any(key in text for key in keywords):
                if ":" in text and len(text.split(":", 1)[1]) > 10:
                    brief_description = text.split(":", 1)[1].strip()

                elif i + 1 < len(desc_tags):
                    brief_description = desc_tags[i+1].get_text(strip=True)
                
                break #stop once we find the main summary

    if brief_description == "No brief description found." and desc_tags:
        brief_description = " ".join([tag.get_text(strip=True) for tag in desc_tags[:2]])

    print(f"Brief Description: {brief_description}")


        #description = "\n\n".join([p.get_text(strip=True) for p in desc_tags if p.get_text(strip=True)])
        #print((f"Extracted {len(description)} description paragraphs."))
    #else:
     #   description = 'No Description Found'
     #   print("No description paragraphs found.")

    #description
    #description = ''
    #try:
        # Try to wait for description to load
    #    WebDriverWait(driver, 5).until(
    #        EC.presence_of_element_located((By.CSS_SELECTOR, "div.vacancy-details"))
    #    )
    #    time.sleep(1)  # Give it extra time to render
    #    vacancy_details = driver.find_elements(By.CSS_SELECTOR, "div.vacancy-details")
    #    for detail in vacancy_details:
    #        try:
    #            paragraph = detail.find_elements(By.TAG_NAME, "p")
    #            for p in paragraph:
    #                text = p.text.strip()
    #                if text:
    #                    description += text + "\n"
    #        except:
    #            pass  # Description might not be there, that's OK
    #except Exception as e:
    #    print(f"Error waiting for vacancy details: {e}")

    #testing
    #print(f"Title: {title_tag}, Company: {company}, Location: {location_name}, URL: {job_url}, Company: {company}, source: {source}, description description: {len(description)} characters")
    
 
    # Check if JobPost with the same URL already exists
 

    if not JobPost.objects.filter(url=job_url).exists():
        # Create a new JobPost entry
        JobPost.objects.create(
            source=source,
            title=title_text,
            company=company,
            location=location_name,
            description=brief_description,
            url=job_url
        )
        print(f"JobPost created successfully. Title: {title_text}")
        # Send Telegram alert
        send_telegram_notification(title_text, company, job_url, brief_description, location_name)
    else:
        print("JobPost already exists in the database.")
        #Here we will send a notification of new post added.



    pass





def run_scraper():
    #1 Get the parent source
    #source, created = JobSource.objects.get_or_create(name="CV Keskus", url="https://cv.ee")
    #source = JobSource.objects.get(id=2) #id 2 is cv.ee

    #2 Download the page
    # Now we have to get the url of the post by filtering in the website
    #https://cv.ee/et/search?limit=20&offset=0&keywords%5B0%5D=junior&towns%5B0%5D=312 <-- In this sample, the keyword used is 'junir' and town is 312(tallin)
    #that url gives a list of job, limit of 20.
    # the div that wraps everything has this clas --> class="jsx-994990582 search__content"
    # Then we have an <ul> tag which containg the list 'unordered list' which inside each item is inside a <li>
    # inside that <li> we have a <div class= jsx-2322545010 vacancy-item >
    # The title of the job is in a h2 tag, but with soup we can scrap though the class which I need to learn later
    # and the h2 has this class --> class="jsx-2322545010 vacancy-item__title"
    # The url of this job post it's inside <a href="job_post_url"


    #Here we are going to put the search url
    #search_url = "https://cv.ee/en/search?limit=20&offset=0&keywords%5B0%5D=junior&towns%5B0%5D=312"
    #headers = {
    #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    #}
    #print(f"Scanning Search Page: {search_url}")
    #response = requests.get(search_url, headers=headers)
    #soup = BeautifulSoup(response.text, 'html.parser')
    #test = soup.find_all('h2', class_="jsx-2322545010 vacancy-item__title")
    
    service = Service(executable_path="/Users/z-tek/Desktop/Job_Alert_EE_Api/job_alert_api/job_source/services/chromedriver")
    driver = webdriver.Chrome(service=service)  

    driver.get("https://cv.ee/en/search?limit=20&offset=0&keywords%5B0%5D=junior&towns%5B0%5D=312")
    
    # Wait for the page to load and find job links
    time.sleep(10)
    
    job_links = []
    try:
        # Find all vacancy items by their class and extract links within them
        vacancy_items = driver.find_elements(By.CSS_SELECTOR, "div.vacancy-item")
        print(f"Found {len(vacancy_items)} vacancy items")
        
        for item in vacancy_items:
            try:
                # Find the h2 tag within the vacancy item, then find the link within h2
                h2 = item.find_element(By.TAG_NAME, "h2")
                link = h2.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")
                if href:
                    if href.startswith("http"):
                        full_url = href
                    
                    job_links.append(full_url)
                    print(f"Found job link: {full_url}")
                  
            except Exception as e:
                print(f"Error extracting link from item: {e}")
    except Exception as e:
        print(f"Error extracting links: {e}")
    
    print(f"\nTotal job links found: {len(job_links)}")

    # Now visit each link one by one and scrape details
    
    #for job_url in job_links:
    #    scrape_single_job(driver, job_url, source="CV Keskus", location_name="Tallin")
    #   time.sleep(5)  # Be polite and avoid overwhelming the server
    for link in job_links[:1]:
        scrape_single_job(driver, link, source="CV Keskus", location_name="Tallin")
        time.sleep(5)  # Be polite and avoid overwhelming the server

    driver.quit()
    
    


    #This finds the first <h1> tag on the page
    #title_tag = soup.select_one('h1')



    
    # This was a test part
    #if title_tag:
    #    print(f"Job Title Found: {title_tag.text.strip()}")
    #else:
    #    print("No h1 tag found.")

    #3 Find all job cards (adjust selector based on your 'Inspect' step)
    #job_cards = soup.select('h1')

    #print(response)

#if __name__ == "__main__":
    #test_one_url()
    #run_scraper()

test_one_url()
# IN ORDER TO RUN THIS SCRIPT IT MUST BE DONE USING DJANGO MANAGA.PY SHELL
# I CAN CREATE A MANAGEMENT COMMAND LATER TO MAKE IT EASIER
# AND LATER TO AUTOMATE AND SCHEDULE THE RUN OF THIS SCRIPT TO FIND NEW JOB POSTS AND SAVE THEM TO THE DATABASE AND SEND ALERTS