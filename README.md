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
      git clone https://github.com/fgomecs/nvidia-job-bot.git
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
      0 * * * * echo "[$(date)] Running script..." >> /home/ubuntu/nvidia-job-alert/cron.log && /usr/bin/env python3 /home/ubuntu/nvidia-job-alert/job_alert.py >> /home/ubuntu/nvidia-job-alert/cron.log 2>&1
      ```
      - Replace `your-email@gmail.com`, `your-app-password`, and `recipient-email@example.com` with your actual values.
      - Replace `/home/ubuntu` with your actual home directory path (run `echo $HOME` to find it).
      - `echo "[$(date)] Running script..."` adds a timestamp to each run for easier debugging.
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
   - `GitHubHowTo.md`: A guide for using Git and GitHub, including staging, committing, and pushing changes.

   ## How It Works
   1. **Scraping**: The script uses Selenium to scrape NVIDIA job postings from a filtered Workday URL.
   2. **Filtering**: Filters jobs posted today (based on "Posted Today" label).
   3. **Tracking**: Compares JR numbers (e.g., `JR1996090`) against a stored list in `seen_jobs.json` to identify new jobs.
   4. **Emailing**: Sends an email with new job details (title, location, posted date, JR number, URL) if new jobs are found.
   5. **Scheduling**: Runs every hour via cron, ensuring emails are only sent for new jobs.

   ## Debugging
   - **No Email Sent**:
     - Check `cron.log` for errors:
       ```bash
       tail -n 20 /home/ubuntu/nvidia-job-alert/cron.log
       ```
     - Ensure your environment variables are set correctly in the crontab.
     - Verify new jobs exist (run the script manually to see output).
   - **No Jobs Found**:
     - Check `page_source.html` and `screenshot.png` to ensure the page loaded correctly.
     - Verify the Workday URL and selectors (`css-1q2dra3`, etc.) are still valid.
   - **Reset Seen Jobs**:
     - Delete `seen_jobs.json` to start fresh (e.g., `rm /home/ubuntu/nvidia-job-alert/seen_jobs.json`).
   - **Cron Not Running**:
     - Check the system log for cron activity:
       ```bash
       grep CRON /var/log/syslog | tail -n 10
       ```

   ## Project Status
   The project is successfully deployed and sending hourly email alerts for new NVIDIA jobs as of April 2025. The cron job is logging with timestamps, and a new job was found and emailed on April 8, 2025, at 8:00 PM local time (00:00 UTC). For a guide on using Git and GitHub to manage this project, see [GitHubHowTo.md](GitHubHowTo.md).

   ## License
   This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
   ```

4. **Save and Exit**:
   - Press `Ctrl+O`, then `Enter` to save.
   - Press `Ctrl+X` to exit.

---

### Step 2: Stage and Commit the Updated `README.md`
Now that you’ve updated `README.md`, let’s stage and commit the change.

1. **Check the Status**:
   ```bash
   git status
   ```
   You should see:
   ```
   On branch main
   Changes not staged for commit:
     (use "git add <file>..." to update what will be committed)
     (use "git restore <file>..." to discard changes in working directory)
           modified:   README.md
   ```

2. **Stage the Change**:
   ```bash
   git add README.md
   ```

3. **Commit the Change**:
   ```bash
   git commit -m "Update README with project status and GitHubHowTo link"
   ```
   You should see output like:
   ```
   [main <hash>] Update README with project status and GitHubHowTo link
    1 file changed, 5 insertions(+), 1 deletion(-)
   ```

4. **Check the Status Again**:
   ```bash
   git status
   ```
   You should see:
   ```
   On branch main
   Your branch is ahead of 'origin/main' by 1 commit.
     (use "git push" to publish your local commits)
   nothing to commit, working tree clean
   ```

---

### Step 3: Push the Changes to GitHub
Now that the change is committed, let’s push it to your GitHub repository.

1. **Push to the `main` Branch**:
   ```bash
   git push origin main
   ```
   - Since SSH is set up and working, this should work without a password prompt.
   - You should see output like:
     ```
     Enumerating objects: 5, done.
     Counting objects: 100% (5/5), done.
     Delta compression using up to 2 threads
     Compressing objects: 100% (3/3), done.
     Writing objects: 100% (3/3), 312 bytes | 312.00 KiB/s, done.
     Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
     remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
     To github.com:fgomecs/nvidia-job-bot.git
        <hash>..<hash>  main -> main
     ```

---

### Step 4: Verify the Update on GitHub
- Visit your repository at `https://github.com/fgomecs/nvidia-job-bot`.
- Check the `README.md` file to confirm the new "Project Status" section is there:
  ```
  ## Project Status
  The project is successfully deployed and sending hourly email alerts for new NVIDIA jobs as of April 2025. The cron job is logging with timestamps, and a new job was found and emailed on April 8, 2025, at 8:00 PM local time (00:00 UTC). For a guide on using Git and GitHub to manage this project, see [GitHubHowTo.md](GitHubHowTo.md).
  ```
- Click the link to `GitHubHowTo.md` to ensure it works and renders correctly.

---

### If You Encounter Issues
If the push fails, please share the output of the following commands, and I’ll help debug:
```bash
git status
git log --oneline
git branch
git remote -v
```

---

### Final Notes
- Your `README.md` now reflects the latest status of your project, including the successful deployment, logging, and the new job alert you received.
- The link to `GitHubHowTo.md` makes it easy for you (or others) to manage the project on GitHub.
- Your project is fully operational, sending alerts, logging runs, and documented on GitHub.

I’m so happy to hear you found a new job posting—hopefully, it’s a great opportunity! Let me know if there’s anything else you’d like to do with the project. 😊



############
Updated steps as of July 2025


## 🛠 Deployment Guide (Oracle Cloud, Ubuntu Minimal)

This guide walks you through setting up and running the `nvidia-job-bot` on a free Oracle Cloud Ubuntu minimal instance with automated scheduling and email alerts.

---

### ☁️ 1. Provision an Oracle Cloud Ubuntu Instance

- Launch a new **Ubuntu Minimal VM** using Oracle Cloud Free Tier
- During creation, download the **private SSH key (.key)**

---

### 🔐 2. Fix SSH Key Permissions and Connect

```bash
chmod 600 ~/.ssh/your-key.key
ssh -i ~/.ssh/your-key.key ubuntu@<your-instance-public-ip>
```

---

### 🧱 3. Set Up the Server Environment

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

---

### 🔑 4. Enable GitHub Access via SSH

Generate SSH key on the server:

```bash
ssh-keygen -t ed25519 -C "oracle-vm"
cat ~/.ssh/id_ed25519.pub
```

- Go to GitHub → Settings → **SSH and GPG keys**
- Click "New SSH key" → paste the contents

---

### 📦 5. Clone the Repository

```bash
git clone git@github.com:fgomecs/nvidia-job-bot.git
cd nvidia-job-bot
```

---

### 🐍 6. Create and Activate Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 🦊 7. Install Firefox and Headless Browser Dependencies

```bash
sudo apt install -y firefox libdbus-glib-1-2 libgtk-3-0 libx11-xcb1 libxt6 libxss1 libasound2 libnss3 libxrandr2
```

Make sure `job_alert.py` includes this headless option (it should already be in there):

```python
options.add_argument("--headless")
```

---

### 📧 8. Configure Email with `.env`

Create a `.env` file in the root directory of the project:

```env
SENDER_EMAIL=your@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com
```

> 🔐 If using Gmail, [create an App Password](https://myaccount.google.com/apppasswords). You must have 2FA enabled.

---

### ⏱️ 9. Automate Execution with Cron

Install and start `cron`:

```bash
sudo apt install -y cron
sudo systemctl enable cron
sudo systemctl start cron
```

Edit the crontab:

```bash
crontab -e
```

Add the following lines to run every hour and at reboot:

```cron
0 * * * * cd /home/ubuntu/nvidia-job-bot && /home/ubuntu/nvidia-job-bot/venv/bin/python job_alert.py >> job_alert.log 2>&1
@reboot cd /home/ubuntu/nvidia-job-bot && /home/ubuntu/nvidia-job-bot/venv/bin/python job_alert.py >> reboot_run.log 2>&1
```

---

## 🔮 Future Enhancements

### ☁️ Serverless Option (Recommended for Cost and Scale)
Move this bot to a serverless function like:
- **AWS Lambda**
- **Google Cloud Functions**
- **Oracle Functions**

Advantages:
- No server management
- Scales automatically
- You only pay when the code runs

### 📥 Alternate Notification Channels

Send job alerts via:
- **Slack** (Slack webhook)
- **Discord** (Discord webhook)
- **Telegram Bot**

### 🧠 Better Job Matching

Add keyword ranking, NLP-based scoring, or location filtering to improve match accuracy.

### 💾 Store to Google Sheets or DB

Instead of using flat files, log seen jobs to:
- Google Sheets (via `gspread`)
- SQLite or PostgreSQL

### 📊 Monitoring + Logs

Use services like:
- `logrotate` (local)
- Papertrail, CloudWatch, or Loggly (remote)

---

## 🎉 You're Done

You now have a fully automated job alert bot running hourly and on system reboot. For questions or improvements, feel free to fork this repo or open an issue!
