from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.common.keys import Keys // This is if I want to send key strokes
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from job_source.utils import send_telegram_notification # Import the function you just made
import time
from job_source.models import JobSource, JobPost




def create_post(source, title_text, company, location_name, brief_description, job_url):

    JobPost.objects.create(
                    source=source,
                    title=title_text,
                    company=company,
                    location=location_name,
                    description=brief_description,
                    url=job_url
                )







class Command(BaseCommand):

    help = 'Run the job scraper to fetch job postings'



    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting the job scraper...'))
        self.run_scraper()


    def run_scraper(self):
        #1 Get the parent source
        # Get the CV Keskus job source (id=2)

        #This section I can later make dynamic to choose different sources

        try:
            source = JobSource.objects.get(id=2)  # id 2 is cv.ee
        except JobSource.DoesNotExist:
            self.stdout.write(self.style.ERROR("JobSource with id=2 not found. Please create it in the admin panel."))
            #print("JobSource with id=2 not found. Please create it in the admin panel.")
            return


        #2 Set up Selenium WebDriver
        
        #make this cloud prepared

        service = Service(ChromeDriverManager().install())
        chrome_options = Options()

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # Run in headless mode
        driver = webdriver.Chrome(service=service, options=chrome_options)  
        #service = Service(executable_path="/Users/z-tek/Desktop/Job_Alert_EE_Api/job_alert_api/job_source/services/chromedriver")


        source = JobSource.objects.get(id=2) #id 2 is cv.ee



        #I can add a way to add the source dynamically later
        
        
        try:

            # Ensure Source exists(Crucial for empty DBs)
            source,_= JobSource.objects.get_or_create(name="CV Keskus", url="https://cv.ee")

            driver.get("https://cv.ee/en/search?limit=20&offset=0&keywords%5B0%5D=junior&towns%5B0%5D=312")
            
            # Wait for the page to load and find job links
            time.sleep(10)

            job_links = []

            # Find all vacancy items by their class and extract links within them
            vacancy_items = driver.find_elements(By.CSS_SELECTOR, "div.vacancy-item")
            #print(f"Found {len(vacancy_items)} vacancy items")
            
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
                        #print(f"Found job link: {full_url}")
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"error extracting link from item: {e}"))
                    #print(f"Error extracting link from item: {e}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"error extracting links: {e}"))
            #print(f"Error extracting links: {e}")
        
        
        

        # Now visit each link one by one and scrape details
        for link in job_links:
            self.scrape_single_job(driver, link, source=source)
            time.sleep(5)  # Be polite and avoid overwhelming the server

        driver.quit()
        #print("Scraper completed successfully!")
        self.stdout.write(self.style.SUCCESS('Job scraper finished.'))


    def scrape_single_job(self, driver, job_url, source):

        self.stdout.write(f"--> Scraping details for {job_url} ")
        driver.get(job_url)

        
        

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1")) 
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading job page: {e}"))
            #print(f"Error loading job page: {e}")
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
            self.stdout.write(self.style.WARNING("Company tag not found."))
            #print("Company tag not found.")


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

        #print(f"Brief Description: {brief_description}")

        # Find location

        location_name = "Tallin"

    
        # Check if JobPost with the same URL already exists
        # Normalize URL for comparison (remove trailing slash, convert to lowercase)
        normalized_url = job_url.rstrip('/').lower()
        
        # Check if the post already exists
        existing_post = JobPost.objects.filter(url__iexact=normalized_url).first()
        
        if not existing_post:
            # Create a new JobPost entry
            try:

                create_post(source, title_text, company, location_name, brief_description, job_url)
                
                #print(f"✓ JobPost created successfully. Title: {title_text}")
                self.stdout.write(self.style.SUCCESS(f"JobPost created successfully. Title: {title_text}"))

                # Send Telegram alert
                send_telegram_notification(title_text, company, job_url, brief_description, location_name)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating JobPost: {e}"))
               
        else:
            self.stdout.write(self.style.WARNING(f"JobPost already exists in database. URL: {job_url}"))
           
            
            


        pass
