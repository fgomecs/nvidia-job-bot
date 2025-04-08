#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

# URL to scrape US jobs with specific location filters
JOB_URL = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite?locationHierarchy1=2fcb99c455831013ea52fb338f2932d8&locations=91336993fab910af6d7122ef682cc375&locations=91336993fab910af6d716c1bb8d4c415&locations=16fc4607fc4310011e929f7115f90000&locations=91336993fab910af6d7006cdf31cc289&locations=91336993fab910af6d7022e347dcc2ca&locations=91336993fab910af6d7020bf3b14c2c5"

# File to store seen JR numbers
SEEN_JOBS_FILE = "seen_jobs.json"

def load_seen_jobs():
    """
    Load the list of seen JR numbers from a file.
    """
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, "r") as f:
            return set(json.load(f))  # Use a set for faster lookups
    return set()

def save_seen_jobs(seen_jobs):
    """
    Save the list of seen JR numbers to a file.
    """
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen_jobs), f)

def get_jobs():
    # Setup WebDriver to use Firefox
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    try:
        # Navigate to the job page
        driver.get(JOB_URL)
        time.sleep(5)  # Wait for the page to load completely (adjust sleep time if necessary)

        # Save the page source for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Take a screenshot for debugging purposes
        driver.save_screenshot("screenshot.png")

        # Find job elements
        job_elements = driver.find_elements(By.CLASS_NAME, "css-1q2dra3")  # Job listing container
        print(f"Found {len(job_elements)} job elements.")

        jobs = []
        for job_element in job_elements:
            try:
                title = job_element.find_element(By.CLASS_NAME, "css-19uc56f").text  # Job title
                location = job_element.find_element(By.CLASS_NAME, "css-129m7dg").text  # Job location
                url = job_element.find_element(By.TAG_NAME, "a").get_attribute("href")  # Job URL
                
                # Try to extract the posting date (look for "Posted Today", etc.)
                try:
                    posted_date = job_element.find_element(By.XPATH, './/*[contains(text(), "Posted")]').text
                except Exception as e:
                    print(f"Could not find posting date for {title}: {e}")
                    posted_date = "Not Found"

                # Extract the JR number from the URL (e.g., JR1996090)
                try:
                    jr_number = url.split("_")[-1].split("?")[0]  # Extract JR number from URL
                except Exception as e:
                    print(f"Could not extract JR number for {title}: {e}")
                    jr_number = None

                # Only add to the list if we successfully captured title, location, URL, and JR number
                if title and location and url and jr_number:
                    jobs.append({
                        "title": title,
                        "location": location,
                        "url": url,
                        "posted_date": posted_date,
                        "jr_number": jr_number
                    })
            except Exception as e:
                print(f"Error extracting job data: {e}")

        return jobs
    finally:
        driver.quit()

def filter_jobs_by_posted_date(jobs, desired_date="Posted Today"):
    """
    Filter jobs by their posted date (e.g., 'Posted Today').
    """
    filtered_jobs = [job for job in jobs if job["posted_date"] == desired_date]
    return filtered_jobs

def get_new_jobs(jobs, seen_jobs):
    """
    Return jobs that have not been seen before based on JR number.
    """
    new_jobs = [job for job in jobs if job["jr_number"] not in seen_jobs]
    return new_jobs

def send_email(jobs, sender_email, sender_password, recipient_email):
    """
    Send an email with the list of new jobs posted today.
    """
    # Email configuration
    smtp_server = "smtp.gmail.com"  # Use Gmail's SMTP server
    smtp_port = 587  # Port for TLS

    # Create the email
    subject = "New NVIDIA Jobs Posted Today"
    body = "Here are the new NVIDIA jobs posted today:\n\n"
    
    if not jobs:
        body += "No new jobs were posted today."
    else:
        for i, job in enumerate(jobs):
            body += f"Job {i+1}:\n"
            body += f"  Title: {job['title']}\n"
            body += f"  Location: {job['location']}\n"
            body += f"  Posted Date: {job['posted_date']}\n"
            body += f"  JR Number: {job['jr_number']}\n"
            body += f"  URL: {job['url']}\n\n"

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS
        server.login(sender_email, sender_password)  # Login to the server
        server.sendmail(sender_email, recipient_email, msg.as_string())  # Send the email
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    # Load previously seen JR numbers
    seen_jobs = load_seen_jobs()
    print(f"Previously seen jobs: {len(seen_jobs)}")

    # Get all jobs
    all_jobs = get_jobs()
    
    if not all_jobs:
        print("No jobs found.")
        return

    # Filter jobs posted today
    today_jobs = filter_jobs_by_posted_date(all_jobs, "Posted Today")
    print(f"Jobs posted today: {len(today_jobs)}")

    # Find new jobs (not previously seen)
    new_jobs = get_new_jobs(today_jobs, seen_jobs)
    print(f"New jobs posted today: {len(new_jobs)}")

    # If there are new jobs, send an email
    if new_jobs:
        # Load email configuration from environment variables
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        recipient_email = os.getenv("RECIPIENT_EMAIL")

        # Check if environment variables are set
        if not all([sender_email, sender_password, recipient_email]):
            raise ValueError("Missing required environment variables: SENDER_EMAIL, SENDER_PASSWORD, or RECIPIENT_EMAIL")

        # Send the email with the new jobs
        send_email(new_jobs, sender_email, sender_password, recipient_email)

        # Update the seen jobs list with the new JR numbers
        seen_jobs.update(job["jr_number"] for job in new_jobs)
        save_seen_jobs(seen_jobs)
        print(f"Updated seen jobs list: {len(seen_jobs)} jobs")
    else:
        print("No new jobs to email.")

if __name__ == "__main__":
    main()
