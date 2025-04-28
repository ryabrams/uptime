# Uptime Monitor

## Description

This tool monitors a website's availability by periodically checking its HTTP status. If the website is down, it sends an email notification via Gmail.  It is designed to be run as a GitHub Action.

## Features

* **Regular Checks:** Pings a specified website URL every 30 minutes.
* **Downtime Detection:** Performs a secondary check after an initial failure to confirm downtime.
* **Email Notification (Downtime):** Sends an email notification when downtime is confirmed.
* **Email Notification (Recovery):** Sends an email notification when the website comes back online.
* **Gmail Integration:** Uses Gmail's SMTP server to send emails.
* **Credential Security:** Uses GitHub Secrets to store Gmail credentials securely.
* **Execution via GitHub Actions:** Runs checks and sends notifications using GitHub Actions.
* **Retry Mechanism:** Retries the website check a configurable number of times to handle transient errors.
* **Detailed Logging:** Provides detailed logging of the check process, including timestamps and error messages.

## Project Structure

```
uptime/
├── .github/workflows/
│   └── uptime.yml
├── uptime.py
├── README.md
├── requirements.txt
└── LICENSE
```

## Setup

### Prerequisites

* A Gmail account.
* A GitHub repository to host the code.
* GitHub Actions enabled for your repository.

### Instructions

1.  **Configure the Website URL:**
    * In your GitHub repository, go to "Settings" -> "Actions" -> "Secrets and variables" -> "Repository secrets".
    * Click "New repository secret".
    * Set the "Name" to `WEBSITE_URL` and the "Value" to the URL of the website you want to monitor (e.g., `https://www.example.com`).

2.  **Add Gmail Credentials as GitHub Secrets:**
    * **Important:** For security, it is highly recommended to use an **App Password** instead of your regular Gmail password. You can generate an App Password in your Google Account settings:
        * Go to your Google Account settings.
        * Navigate to "Security".
        * Enable "2-Step Verification" (if it's not already enabled).
        * Under "2-Step Verification," find "App passwords".
        * Create an App Password with a descriptive name (e.g., "GitHub Actions uptime").
        * **Use this App Password** in the next step, **not** your regular Gmail password.
    * In your GitHub repository's "Secrets" settings (as described in step 1), add the following secrets:
        * Name: `GMAIL_EMAIL`
        * Value: Your Gmail address (e.g., `your_email@gmail.com`)
        * Name: `GMAIL_PASSWORD`
        * Value: **Your Gmail App Password** (the one you generated in the previous step).
        * Name: `RECIPIENT_EMAIL`
        * Value: The email address where you want to receive notifications (this can be the same as your Gmail address, or a different one).

3.  **Create the GitHub Actions Workflow:**
    * In your GitHub repository, create a new file at `.github/workflows/uptime.yml` (the filename is important).
    * Copy and paste the following YAML configuration into the file:

    ```yaml
    name: uptime

    on:
      schedule:
        - cron: "*/30 * * * *"  # Runs every 30 minutes

    jobs:
      monitor:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout code
            uses: actions/checkout@v4
          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: '3.9'  # Or any version you prefer
          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install requests
          - name: Run website check
            env:
              WEBSITE_URL: ${{ secrets.WEBSITE_URL }}
              GMAIL_EMAIL: ${{ secrets.GMAIL_EMAIL }}
              GMAIL_PASSWORD: ${{ secrets.GMAIL_PASSWORD }}
              RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
              PREVIOUSLY_DOWN: false # Initialize
            run: python uptime.py
    ```

4.  **Commit and Push:**
    * Commit the `uptime.py` script, the `.github/workflows/uptime.yml` file, the `README.md`, the `requirements.txt`, and the `LICENSE` file to your GitHub repository.

##  Explanation

###   Logic for Downtime Detection and Recovery Notification

1.  **Downtime Detection:**
    * The `check_website_status` function makes an HTTP request to the specified URL.
    * If the initial check returns a status code indicating an error (4xx or 5xx) or times out, the script retries the check.
    * If all retries fail, the script considers the website to be down and sends a downtime notification email. The `PREVIOUSLY_DOWN` environment variable is set to "true".
2.  **Recovery Notification:**
    * If a subsequent check after a downtime event is successful (returns a 2xx status code), and the `PREVIOUSLY_DOWN` environment variable is "true", the script sends a recovery notification email.
    * The `PREVIOUSLY_DOWN` environment variable is reset to "false".

This approach prevents false alarms due to temporary network glitches by requiring consecutive failed checks before declaring a website as down. The use of the `PREVIOUSLY_DOWN` environment variable ensures that a recovery email is sent only after a confirmed downtime event.

##  Troubleshooting

* **Email Notifications Not Received:**
    * Double-check that you have correctly configured the `GMAIL_EMAIL`, `GMAIL_PASSWORD`, and `RECIPIENT_EMAIL` secrets in your GitHub repository.
    * Ensure that you are using an **App Password** for the `GMAIL_PASSWORD` secret, not your regular Gmail password.
    * Check your Gmail spam folder.
    * Verify that your Gmail account allows "less secure app access" (though this is generally discouraged in favor of App Passwords, and may not be available for accounts with advanced security).
    * Check the GitHub Actions logs for any error messages related to sending emails.
* **Website Always Reported as Down:**
    * Double-check that the `WEBSITE_URL` secret is set correctly and the URL is accessible.
    * Check the GitHub Actions logs for any error messages related to checking the website status.
    * Try accessing the website from your local machine to verify its availability.
* **GitHub Actions Workflow Fails:**
    * Check the GitHub Actions logs for any error messages.
    * Ensure that the `uptime.yml` file is in the correct location (`.github/workflows/`).
    * Verify that your GitHub repository has Actions enabled.
* **Intermittent failures:**
    * The script includes a retry mechanism to handle these. Check the number of retries and the delay.
    * Check the website's server logs for intermittent errors.

##  Customization

* **Check Frequency:** Change the `cron` expression in the `.github/workflows/uptime.yml` file to adjust how often the website is checked. The current setting is `*/30 * * * *` (every 30 minutes).
* **Email Content:** Modify the `send_email` function in the `uptime.py` script to customize the subject and body of the email notifications.
* **Timeout and Retries:** Adjust the `TIMEOUT_SECONDS`, `RETRY_DELAY_SECONDS`, and `MAX_RETRIES` constants in the `uptime.py` script to change the timeout for website checks and the retry behavior.
* **Logging:** The script uses the `logging` module. You can configure it to log to a file instead of or in addition to the console by adding a `logging.FileHandler` to the handlers list.

## License

This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.