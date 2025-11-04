# Email Drafter - README

## What It Does

AI-powered cold email generator that creates personalized Gmail drafts using Google's Gemini API.

Enter recipient details → AI generates professional email → Saves as Gmail draft → Review and send

---

## Features

✅ AI-generated personalized emails using Gemini  
✅ Automatically creates Gmail drafts  
✅ Regenerate emails until you like them  
✅ One-time setup (saves API key & Gmail auth)  
✅ 100% free to use  

---

## Quick Setup

### 1. Install Dependencies
```bash
pip install google-generativeai google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get Gemini API Key
- Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create API key and copy it

### 3. Set Up Gmail API
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create project → Enable Gmail API
- Create OAuth credentials (Desktop app)
- Download as `credentials.json`

### 4. Run
```bash
python3 email_drafter.py
```

First run: paste API key, authenticate Gmail (one-time)

---

## Usage

```
Recipient Email: john@example.com
Recipient Name: John Doe
Source Link: https://johndoe.com/project
Additional Context: Saw your work on AI tools

[AI generates email]

Options:
[1] Create Gmail draft
[2] Regenerate email
[3] Start new email
[4] Quit
```

---

## File Structure

```
email-drafter/
├── email_drafter.py       # Main script
├── credentials.json       # OAuth config (you download)
├── api_key.txt           # Auto-saved on first run
├── token.pickle          # Auto-saved Gmail token
└── .gitignore            # Keeps secrets safe
```

---

## Security

🔒 **Never commit:**
- `api_key.txt`
- `credentials.json`  
- `token.pickle`

These are in `.gitignore`

---

## Customization

Edit the AI prompt in `generate_email()` (line ~70) to change email style:
- Tone (casual/formal)
- Length
- Structure

---

## Requirements

- Python 3.7+
- Google account
- Internet connection

---

Built with Google Gemini API & Gmail API
