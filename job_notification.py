import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time

def fetch_jobs():
    url = "https://www.mourjan.com/ae/al-ain/vacancies/en/?sl=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    jobs = []
    postings = soup.find_all("div", class_="ad")
    for post in postings:
        link_element = post.find("a", class_="link")
        date_element = post.find("div", class_="box hint")
        
        if link_element and date_element:
            job_link = link_element["href"].strip()
            date_divs = date_element.find_all("div")
            if len(date_divs) > 1:
                date_posted = date_divs[1].text.strip()
                
                job_title = post.find("div", {"dir": "auto"}).text.strip() if post.find("div", {"dir": "auto"}) else "No title"
                
                if "hour" in date_posted or "minute" in date_posted:
                    time_ago = int(date_posted.split()[0])
                    if "hour" in date_posted and time_ago <= 24:
                        jobs.append({"title": job_title, "link": f"https://www.mourjan.com{job_link}", "date": date_posted})
                    elif "minute" in date_posted:
                        jobs.append({"title": job_title, "link": f"https://www.mourjan.com{job_link}", "date": date_posted})

    return jobs

def save_session():
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=selenium")  # Path to user data
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://web.whatsapp.com")

    print("Please scan the QR code with your phone to log in.")
    time.sleep(60)  # Increase the time if needed

    # Save cookies
    with open("whatsapp_cookies.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)

    driver.quit()

def load_session(driver):
    # Load cookies
    with open("whatsapp_cookies.pkl", "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    
    driver.refresh()

def send_whatsapp_message(jobs, contact_name):
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=selenium")  # Path to user data
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://web.whatsapp.com")

    # Load session data
    load_session(driver)

    # Refresh the page to apply the session data
    driver.refresh()

    try:
        # Wait for the page to load
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@role="textbox"][@aria-label="Search input textbox"]'))
        )

        # Search for the contact
        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@role="textbox"][@aria-label="Search input textbox"]')
        search_box.click()
        search_box.send_keys(contact_name)
        search_box.send_keys(Keys.ENTER)

        # Wait for the contact to open
        time.sleep(2)

        # Find the message box and send the message
        message_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@role="textbox"][@aria-label="Type a message"]'))
        )
        message_box.click()

        # Create message text
        message = "New jobs posted within the last 2 hours:\n\n"
        for job in jobs:
            message += f"Title: {job['title']}\nLink: {job['link']}\nDate: {job['date']}\n\n"

        # Send the message
        message_box.send_keys(message)
        message_box.send_keys(Keys.ENTER)

        print("Message sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        time.sleep(5)
        driver.quit()

def main():
    new_jobs = fetch_jobs()
    if new_jobs:
        send_whatsapp_message(new_jobs, "FriendName")
    else:
        print("No new jobs posted within the last 24 hours.")

if __name__ == "__main__":
    # First, save the session by scanning the QR code once
    #save_session()

    # Then, use the session to send messages
    main()