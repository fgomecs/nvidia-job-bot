#By Francisco Gomez - All Rights Reserved 2025
Let’s modify the script to use environment variables for your email credentials (`sender_email`, `sender_password`, and `recipient_email`) instead of hardcoding them. This is a best practice for security, especially since you’re pushing the code to GitHub. We’ll use Python’s `os` module to access environment variables, and I’ll show you how to set them up on your Ubuntu VM.

### Step 1: Modify the Script to Use Environment Variables
We’ll update `job_alert.py` to read the email credentials from environment variables using `os.getenv()`. If the variables aren’t set, we’ll provide a fallback or raise an error to ensure the script doesn’t run without them.

Here’s the updated script:

```python
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
```

### Key Changes
1. **Removed Hardcoded Credentials**:
   - Removed the hardcoded `sender_email`, `sender_password`, and `recipient_email` from the `main()` function.

2. **Added Environment Variable Access**:
   - Used `os.getenv()` to read `SENDER_EMAIL`, `SENDER_PASSWORD`, and `RECIPIENT_EMAIL`.
   - Added a check to raise a `ValueError` if any of these variables are missing, ensuring the script fails early if not configured properly.

### Step 2: Set Up Environment Variables on Ubuntu
You need to set the environment variables on your Ubuntu VM so the script can access them. There are a few ways to do this, but since you’re using `cron` to schedule the script, we’ll set them in the crontab file to ensure they’re available when the script runs.

1. **Edit the Crontab**:
   Open the crontab file:
   ```bash
   crontab -e
   ```

2. **Add Environment Variables to Crontab**:
   Add the environment variables at the top of the crontab file, followed by the existing cron job. Replace the placeholder values with your actual email credentials:
   ```
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   RECIPIENT_EMAIL=recipient-email@example.com
   0 * * * * /usr/bin/env python3 ~/nvidia-job-alert/job_alert.py >> ~/nvidia-job-alert/cron.log 2>&1
   ```
   - `SENDER_EMAIL`: Your Gmail address (e.g., `your-email@gmail.com`).
   - `SENDER_PASSWORD`: Your Gmail App Password (e.g., `abcd efgh ijkl mnop`).
   - `RECIPIENT_EMAIL`: The email address to receive job alerts (e.g., `recipient-email@example.com`).

3. **Save and Exit**:
   Save the crontab file (e.g., `Ctrl+O`, then `Ctrl+X` in `nano`).

### Step 3: Test the Script Manually
To test that the environment variables are working, you can temporarily set them in your shell and run the script:

1. **Set Environment Variables in the Shell**:
   ```bash
   export SENDER_EMAIL="your-email@gmail.com"
   export SENDER_PASSWORD="your-app-password"
   export RECIPIENT_EMAIL="recipient-email@example.com"
   ```

2. **Run the Script**:
   ```bash
   python3 ~/nvidia-job-alert/job_alert.py
   ```
   It should work the same as before, sending an email if there are new jobs. If the environment variables aren’t set, you’ll see an error like:
   ```
   ValueError: Missing required environment variables: SENDER_EMAIL, SENDER_PASSWORD, or RECIPIENT_EMAIL
   ```

### Step 4: Update the `README.md`
Since we’ve changed how the email credentials are handled, let’s update the `README.md` to reflect this. Here’s the revised `README.md`:

```markdown
# NVIDIA Job Alert

This project is a Python script that scrapes NVIDIA job postings from the Workday career site, filters for jobs posted today in specific US locations, and sends an email with new job listings every hour. It ensures that emails are only sent for new jobs by tracking job IDs (JR numbers).

## Features
- Scrapes NVIDIA job postings from a filtered Workday URL (specific US locations).
- Filters jobs posted today (based on the "Posted Today" label).
- Tracks previously seen jobs using JR numbers (e.g., `JR1996090`) to avoid duplicate emails.
- Sends an email with new job details (title, location, posted date, JR number, and URL) every hour if new jobs are found.
- Runs automatically every hour using a cron job on Ubuntu.
- Uses environment variables for secure email configuration.

## Prerequisites
- **Python 3**: Ensure Python 3 is installed on your system (`python3 --version`).
- **Firefox**: Required for Selenium (`sudo apt update && sudo apt install firefox`).
- **Geckodriver**: Automatically installed via `webdriver_manager`.
- **Dependencies**: Install the required Python packages:
  ```bash
  pip3 install selenium webdriver_manager
  ```
- **Email Account**: A Gmail account with an App Password for sending emails.
  - Enable 2-factor authentication in your Google Account.
  - Generate an App Password (Google Account > Security > App Passwords > Generate).
- **Ubuntu**: The script is designed to run on an Ubuntu VM with cron for scheduling.

## Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/nvidia-job-alert.git
   cd nvidia-job-alert
   ```

2. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure Email Settings**:
   - The script uses environment variables for email configuration:
     - `SENDER_EMAIL`: Your Gmail address (e.g., `your-email@gmail.com`).
     - `SENDER_PASSWORD`: Your Gmail App Password (e.g., `abcd efgh ijkl mnop`).
     - `RECIPIENT_EMAIL`: The email address to receive job alerts (e.g., `recipient-email@example.com`).
   - Set these variables in your crontab (see "Scheduling with Cron" below) or in your shell for testing:
     ```bash
     export SENDER_EMAIL="your-email@gmail.com"
     export SENDER_PASSWORD="your-app-password"
     export RECIPIENT_EMAIL="recipient-email@example.com"
     ```

4. **Make the Script Executable**:
   ```bash
   chmod +x job_alert.py
   ```

5. **Test the Script**:
   Run the script manually to ensure it works:
   ```bash
   python3 job_alert.py
   ```
   It should scrape jobs, check for new ones, and send an email if there are new jobs posted today.

## Scheduling with Cron
The script is designed to run every hour and only send an email if new jobs are found.

1. **Edit Crontab**:
   ```bash
   crontab -e
   ```

2. **Add Environment Variables and Cron Job**:
   Add the following lines to set environment variables and run the script every hour (at the start of each hour):
   ```
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   RECIPIENT_EMAIL=recipient-email@example.com
   0 * * * * /usr/bin/env python3 ~/nvidia-job-alert/job_alert.py >> ~/nvidia-job-alert/cron.log 2>&1
   ```
   - Replace `your-email@gmail.com`, `your-app-password`, and `recipient-email@example.com` with your actual values.
   - `0 * * * *`: Runs at minute 0 of every hour (e.g., 1:00, 2:00, etc.).
   - Logs output to `cron.log` for debugging.

3. **Save and Exit**:
   Save the crontab file (e.g., `Ctrl+O`, then `Ctrl+X` in `nano`).

## Files
- `job_alert.py`: The main script that scrapes jobs, tracks seen jobs, and sends emails.
- `seen_jobs.json`: Automatically generated file that stores JR numbers of previously seen jobs.
- `page_source.html`: Debugging file with the HTML of the scraped page.
- `screenshot.png`: Debugging screenshot of the scraped page.
- `cron.log`: Log file for cron job output (created after scheduling).

## How It Works
1. **Scraping**: The script uses Selenium to scrape NVIDIA job postings from a filtered Workday URL.
2. **Filtering**: Filters jobs posted today (based on "Posted Today" label).
3. **Tracking**: Compares JR numbers (e.g., `JR1996090`) against a stored list in `seen_jobs.json` to identify new jobs.
4. **Emailing**: Sends an email with new job details (title, location, posted date, JR number, URL) if new jobs are found.
5. **Scheduling**: Runs every hour via cron, ensuring emails are only sent for new jobs.

## Debugging
- **No Email Sent**:
  - Check `cron.log` for errors.
  - Ensure your environment variables are set correctly in the crontab.
  - Verify new jobs exist (run the script manually to see output).
- **No Jobs Found**:
  - Check `page_source.html` and `screenshot.png` to ensure the page loaded correctly.
  - Verify the Workday URL and selectors (`css-1q2dra3`, etc.) are still valid.
- **Reset Seen Jobs**:
  - Delete `seen_jobs.json` to start fresh (e.g., `rm seen_jobs.json`).

## Security Note
- **Environment Variables**: Email credentials are stored in environment variables to avoid hardcoding them in the script. Ensure these variables are set in your crontab or shell environment.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

### Step 5: Proceed with GitHub Setup
Now that the script is updated to use environment variables, you can safely proceed with pushing to GitHub. Here’s a quick recap of the remaining steps (from the previous message):

1. **Initialize the Git Repository** (if not already done):
   ```bash
   cd ~/nvidia-job-alert
   git init
   ```

2. **Add Files**:
   Ensure you have `job_alert.py`, `README.md`, `requirements.txt`, and `.gitignore` (from the previous message). Add them to Git:
   ```bash
   git add job_alert.py README.md requirements.txt .gitignore
   ```

3. **Commit**:
   ```bash
   git commit -m "Initial commit: NVIDIA Job Alert script with email, scheduling, and environment variables"
   ```

4. **Create a GitHub Repository**:
   - Go to GitHub, create a new repository named `nvidia-job-alert` (don’t initialize with a README).
   - Copy the repository URL (e.g., `https://github.com/your-username/nvidia-job-alert.git`).

5. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/your-username/nvidia-job-alert.git
   git push -u origin main
   ```
   - Authenticate with your GitHub username and a Personal Access Token if prompted.

6. **Add a License** (optional):
   Create a `LICENSE` file with the MIT License (as shown in the previous message), then:
   ```bash
   git add LICENSE
   git commit -m "Add MIT License"
   git push origin main
   ```

### Final Notes
- The script is now secure for GitHub since the email credentials are no longer hardcoded.
- The `README.md` has been updated to reflect the use of environment variables.
- After pushing to GitHub, you can share the repository URL with me if you’d like me to take a look!

Let me know if you run into any issues while pushing to GitHub or if you’d like to make any further adjustments! 😊
