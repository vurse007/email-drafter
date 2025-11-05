import google.generativeai as genai #using gemini to write emails
from google.oauth2.credentials import Credentials #logging into google api
from google_auth_oauthlib.flow import InstalledAppFlow #browser popup to login
from google.auth.transport.requests import Request #refresh expired tokens
from googleapiclient.discovery import build #gmail api service
import base64 #encodes emails into gmail's desired format
import os #filesystem (local)
import pickle #saving and loading python objects (e.g. credentials) to files
from email.mime.text import MIMEText #create properly formatted email messages
import datetime
import calendar #for consistent dates in the email

now = datetime.datetime.now()
current_month = now.month
current_year = now.year

#config
SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
] #permission to create drafts and read a spreadsheet
API_KEY_FILE = 'api_key.txt'
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json' #stored information to connect accounts and services

def load_api_key():
    #load the saved api key or prompt for a new one
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            return f.read().strip()
    else:
        print("\n first time setup: enter your google ai studio api key")
        print("get it from makersuite.google.com/app/apikey ")
        api_key = input("API Key: ").strip()
        with open(API_KEY_FILE, 'w') as f:
            f.write(api_key)
        print("api key was saved successfully.")
        return api_key
    
def connect_google_services():
    #load existing credentials
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    #check if credentials are valid
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            print("refreshing gmail access...")
            creds.refresh(Request())

        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"\n ERROR: {CREDENTIALS_FILE} not found.")
                print("\nDownload it from Google Cloud Console:")
                print("1. Go to console.cloud.google.com")
                print("2. APIs & Services > Credentials")
                print("3. Download OAuth 2.0 Client ID")
                print(f"4. Save as '{CREDENTIALS_FILE}' in this folder\n")
                return None, None
            
            print("\n opening browser for gmail authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        #save creds
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print("connected to gmail successfully.")

    #build both services
    gmail_service = build('gmail', 'v1', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    return gmail_service, sheets_service

def generate_email(api_key, recipient_name, source_link, additional_context=""):
    #generate the email using the gemini api:
    print("\n generating email using gemini...")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')

        prompt = f"""You are an expert academic outreach writer skilled in crafting personalized, professional cold emails for high school students seeking research opportunities.

You have:
- Professor Name: {recipient_name}
- Research Source Link: {source_link}
- Additional Context: {additional_context if additional_context else 'None'}

Use the professor's name directly in the greeting and analyze the research source to create personalized content.

Write a concise, polite, and well-formatted email using this exact structure:

---
Hello [Professor Name],

I hope you are having a great day. We recently read about your research on [specific topic from the source link]. We were particularly intrigued by [provide a detailed, two-sentence analysis that demonstrates deep understanding - mention specific methodologies, findings, implications, or applications].

Our names are Pranav Kolli and Ayush Patel, and we are juniors at Arnold O. Beckman High School with a strong interest in conducting research in [related field from the knowledge source]. We both share a deep passion for scientific exploration and have completed rigorous coursework including AP Biology, AP Chemistry, and Human Body Systems.

We would be incredibly grateful for the opportunity to gain research experience under your guidance. We would love to work with you from {calendar.month_name[current_month]} of {current_year} through our high school graduation in June of 2027.

We would be honored to meet with you to discuss this opportunity further.

Best regards,
Pranav Kolli and Ayush Patel
Juniors at Arnold O. Beckman High School
---

CRITICAL Guidelines for the research overview section:
- Write 2-3 sentences that demonstrate thorough understanding of their work
- Reference specific methodologies, experimental approaches, or analytical techniques mentioned
- Mention concrete findings, results, or implications from their research
- Use appropriate scientific terminology from their field
- Show understanding of how their work addresses important problems or advances the field
- If available, reference specific papers, grants, or collaborations mentioned
- Connect their research to broader scientific trends or applications

General Guidelines:
- Use the exact professor name provided in the greeting
- Replace [bracketed sections] with specific, accurate details drawn from the knowledge source
- Maintain a respectful, academic tone that shows scientific maturity
- Keep the total length under 220 words
- Ensure the message sounds genuine and demonstrates real engagement with their work
- If detailed information is limited, focus on the most substantive aspects available
- Do not include links, citations, or unnecessary jargon — aim for informed accessibility

Format the response as plain text ready to copy paste like:
[email body]"""

        try:
            response = model.generate_content(prompt)
        except Exception as e:
            print(f"\n error using gemini-2.5-pro: {e}")
            print("\n proceeding using gemini-2.0-flash...")
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)

        generated_text = response.text

        #parse
        body = generated_text

        return body
    
    except Exception as e:
        print(f"error generating email: {e}")
        return None
    
def read_sheet(service, spreadsheet_id, range_name):
    #read data from google sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    rows = result.get('values', [])
    return rows #returns a list of lists [['john@...', 'John', 'https://...'], ...]
    
def create_gmail_draft(service, recipient_email, body):
    #create a draft in gmail
    try:
        message = MIMEText(body)
        message['to'] = recipient_email
        message['cc'] = 'pranavsaikolli@gmail.com'
        message['subject'] = 'Research Opportunity Inquiry'

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        draft = service.users().drafts().create(
            userId = 'me',
            body = {'message': {'raw': raw_message}}
        ).execute()

        print("\n gmail draft created successfully.")
        print("check your drafts folder to review and send. \n")
        return True
    
    except Exception as e:
        print(f"error in creating a gmail draft: {e}\n")
        return False
    
def main():
    print("+ " * 30)
    print(" welcome to the automated cold email drafter utility ")
    print("+ " * 30)

    #load api key
    api_key = load_api_key()

    #connect to gmail
    print("\n connecting to gmail...")
    gmail_service, sheets_service = connect_google_services()

    if not gmail_service or not sheets_service:
        print("failed to connect to gmail or sheets. continuing without autodraft and autoread.")
        gmail_service = None
        sheets_service = None

    sheets_int = input("use google sheets integration? (ENTER for Y, n for N): ").strip().lower()

    if sheets_int == 'n':
        #main loop - manual input
        print("\n starting manual input loop...")
        while True:
            print("\n" + "-" * 60)
            print("enter email details (or quit to exit)")
            print("-" * 60)

            #get recipient email
            recipient_email = input("\nrecipient email: ").strip()
            if recipient_email.lower() == 'quit':
                print("user-specified termination")
                break

            #get recipient name
            recipient_name = input("recipient name: ").strip()
            if recipient_name.lower() == 'quit':
                print("user-specified termination")
                break

            #get source link
            source_link = input("research source link: ").strip()
            if source_link.lower() == 'quit':
                print("user-specified termination")
                break

            #get additional context (OPTIONAL)
            print("optional additional context (press ENTER to skip): ")
            additional_context = input().strip()
            if additional_context.lower() == 'quit':
                print("user-specified termination")
                break

            #generate email
            body = generate_email(api_key, recipient_name, source_link, additional_context)

            if not body:
                continue

            #diplay generated email
            print("\n" + "-" * 60)
            print(" generated email")
            print("-" * 60)
            print(body)
            print("-" * 60)

            #next steps
            while True:
                print("\n next steps:")
                print(" ENTER: create gmail draft")
                print(" A: regenerate email")
                print(" B: quit")

                choice = input("> ").strip()

                if choice == '':
                    if gmail_service:
                        create_gmail_draft(gmail_service, recipient_email, body)
                        break
                    else:
                        print("gmail isn't connected - reconnect gmail service to regain access to autodraft.")

                elif choice.lower() == 'a':
                    body = generate_email(api_key, recipient_name, source_link, additional_context)
                    if body:
                        print("\n" + "-" * 60)
                        print(" regenerated email")
                        print("-" * 60)
                        print(body)
                        print("-" * 60)
                    else:
                        break

                elif choice.lower() == 'b':
                    print("user-specified termination")
                    return
                
                else:
                    print("invalid choice - please enter one of the options.")
    
    else:
        print("\n starting google sheets integration...")
        sheet_id = None
        if os.path.exists('sheet_id.txt'):
            with open('sheet_id.txt', 'r') as f:
                sheet_id = f.read().strip()
        else:
            sheet_id = input("enter the google sheet id (the long string in the sheet url): ").strip()
            with open('sheet_id.txt', 'w') as f:
                f.write(sheet_id)

        #read all rows from the sheet
        rows = read_sheet(sheets_service, sheet_id, 'v2!A2:D') #uses sheets_services
        # v2 (name of sheet tab) ! (separator) A2:D (range - columns A to D, starting from row 2 to skip header)

        drafted_email_count = 0

        for row in rows:
            if len(row) < 3:
                print(f"\n skipping incomplete row: {row}")
                continue
            recipient_name = row[0].strip() #column A of each row in the list of rows (2d array/nested lists)
            recipient_email = row[1].strip()  #column B
            source_link = row[2].strip()     #column C
            additional_context = row[3].strip() if len(row) >= 4 else "" #column D (optional - may not have data)

            body = generate_email(api_key, recipient_name, source_link, additional_context)

            if not body:
                continue

            if gmail_service:
                success = create_gmail_draft(gmail_service, recipient_email, body)

            if success:
                drafted_email_count += 1

        print(f"\n generated and drafted {drafted_email_count} emails using google sheets integration.")
        print("data processed and outputs created. exiting...")
        os._exit(0)



if __name__ == "__main__":
    main()