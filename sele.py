import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from instagrapi import Client
import os
import io
from PIL import Image
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime
import openai
from google.cloud import aiplatform
import base64


# Setup WebDriver
class LoginPage:
    def __init__(self, browser):
        self.browser = browser

    def login(self, username, password):
        username_input = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        password_input = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()
        sleep(5)


class HomePage:
    def __init__(self, browser):
        self.browser = browser
        self.browser.get('https://www.instagram.com/')

    def go_to_login_page(self):
        try:
            login_element = WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='Log in']"))
            )
            self.browser.execute_script("arguments[0].click();", login_element)
        except Exception as e:
            print(f"Exception occurred: {e}")
        sleep(2)
        return LoginPage(self.browser)


browser = webdriver.Firefox()
browser.implicitly_wait(5)

home_page = HomePage(browser)
login_page = home_page.go_to_login_page()
login_page.login("", "")#hidden

# Define the scopes and the credentials file
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = 'credentials.json'

creds = None
if os.path.exists('token.json'):
    print('Token file exists.')
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except google.auth.exceptions.RefreshError:
        print('Token refresh error, setting creds to None.')
        creds = None

if not creds or not creds.valid:
    print('Need to obtain new credentials.')
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except google.auth.exceptions.RefreshError as e:
            print(f"Token refresh error: {e}")
            creds = None
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('drive', 'v3', credentials=creds)

folder_id = ''#hidden
current_date = datetime.now()
file_name = f"{current_date.strftime('%B_%d')}.jpg"
print('Filename to obtain is', file_name)

# Simplify query to list all files in the folder
query = f"'{folder_id}' in parents"
print('Query:', query)
results = service.files().list(q=query, spaces='drive', fields='files(id, name, mimeType)').execute()
items = results.get('files', [])

# Print query results for debugging
print('Query results:', items)

file_path = None
if not items:
    print('No files found.')
else:
    for item in items:
        file_name_trimmed = item['name'].strip()  # Trim the name to remove leading/trailing spaces
        print(f"Found file: {file_name_trimmed} with MIME type: {item['mimeType']}")
        if file_name_trimmed == file_name:
            file_id = item['id']
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join('downloaded_images', file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f'Download {int(status.progress() * 100)}%.')
            print(f'File downloaded to {file_path}')

if not file_path:
    print('File path not defined, exiting.')
    exit(1)

# Ensure ADC is set up
try:
    google.auth.default()
    print("ADC is set up correctly.")
except google.auth.exceptions.DefaultCredentialsError:
    print("ADC is not set up. Please run 'gcloud auth application-default login'.")

# Set up Vertex AI client
aiplatform.init(project='senri-insta-auto')


def resize_image(image_path, output_path, max_size_bytes=1499999):
    with Image.open(image_path) as img:
        img_format = img.format
        width, height = img.size

        # Initial resizing to max width or height of 1024 if necessary
        if width > 1024 or height > 1024:
            img.thumbnail((1024, 1024))

        # Compress image until it is below max_size_bytes
        quality = 85
        while True:
            img.save(output_path, format=img_format, quality=quality)
            size = os.path.getsize(output_path)
            print(f"Trying with quality {quality}: size {size} bytes")
            if size <= max_size_bytes or quality <= 10:
                break
            quality -= 5

        return output_path


def get_image_description(image_path, resized_image_name):
    resized_image_path = resize_image(image_path, os.path.join('downloaded_images', resized_image_name))
    final_image_size = os.path.getsize(resized_image_path)
    print(f"Final image size: {final_image_size} bytes")  # Print the final image size

    # Check if the image size is less than 1.5MB before making the request
    if final_image_size > 1499999:
        print("Image size exceeds 1.5MB after resizing. Cannot proceed with the request.")
        return "Image size too large to process."
    else:
        with open(resized_image_path, 'rb') as image_file:
            image_content = image_file.read()
            image_content_base64 = base64.b64encode(image_content).decode('utf-8')
        print(f"Sending request with image size: {final_image_size} bytes")  # Debug print to confirm size
        endpoint = aiplatform.Endpoint(
            endpoint_name='')#hidden
        response = endpoint.predict(instances=[{"content": image_content_base64}])

        # Debug print to inspect the response
        print("Response from Vertex AI:", response)

        labels = response.predictions
        description = ', '.join([label['displayName'] for label in labels if 'displayName' in label])
    return description


openai.api_key = "" #hidden


def send_pic_to_gpt(prompt):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message["content"].strip()
        except openai.error.RateLimitError as e:
            print(f"Rate limit exceeded. Retrying in {2 ** attempt} seconds...")
            time.sleep(2 ** attempt)
        except openai.error.OpenAIError as e:
            print(f"OpenAI error: {e}")
            break
    return "Failed to generate a caption."


resized_image_name = f"resized_{file_name}"
image_description = get_image_description(file_path, resized_image_name)
if image_description != "Image size too large to process.":
    caption_prompt = f"Generate an Instagram caption for an image described as: {image_description}"
    print("caption_prompt", caption_prompt)
    caption = send_pic_to_gpt(caption_prompt)
    print(f"Generated caption: {caption}")

    cl = Client()
    cl.login(username="automatedbites", password="master5510")
    image_path = file_path

    cl.photo_upload(image_path, caption)
