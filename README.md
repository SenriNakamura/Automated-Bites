# Automated Bites - Instagram Content Automation

**Automated Bites** is a Python-based automation bot designed to simplify cooking journaling by integrating cutting-edge APIs and artificial intelligence. The bot automates the entire workflow from image retrieval, analysis, caption generation, and Instagram posting. 

⚠️ **Project Discontinued**: The project has been discontinued as the usage costs of Vertex AI API exceeded the budget for personal development.

---

## Features
- **Image Retrieval:** Automatically fetches food images stored on Google Drive using the Google Drive API.
- **Image Analysis:** Utilizes Cloud Vision AI and Vertex AI for analyzing the content of images.
- **Caption Generation:** Leverages OpenAI API to generate context-aware, creative Instagram captions based on image analysis.
- **Automated Posting:** Posts images and captions directly to Instagram using the Instagram API.
- **Dynamic Interaction:** Employs Selenium for browser automation to manage dynamic actions on Instagram.

---

## Technologies Used
- **Programming Language:** Python
- **APIs:**
  - Google Drive API
  - Cloud Vision AI
  - OpenAI API
  - Vertex AI (Generative Models)
  - Instagram API
- **Automation Tool:** Selenium
- **Additional Libraries:**
  - `instagrapi`
  - `google-auth`
  - `google-api-python-client`
  - `Pillow` (for image processing)

---

## How It Works
1. **Image Retrieval:** Fetches the latest image from a specific folder in Google Drive.
2. **Image Resizing and Analysis:**
   - Compresses images to meet API size constraints using `Pillow`.
   - Analyzes the image using Vertex AI and Cloud Vision to generate descriptive labels.
3. **Caption Generation:**
   - Sends image analysis results to OpenAI API for generating captions.
   - Ensures engaging and context-aware captions are produced for Instagram.
4. **Automated Posting:**
   - Logs into Instagram using Selenium for browser automation.
   - Uploads the image and posts it with the generated caption.

---

## Why It Was Discontinued
While the project demonstrated a successful integration of APIs and AI tools, the cost of using Vertex AI API for image analysis and generative modeling exceeded personal budget constraints. Open-source or lower-cost alternatives may be explored for future versions.

---

## Future Plans
This project provides a framework for social media automation that can be extended or adapted:
- Replace Vertex AI with open-source or free tools for image analysis.
- Extend the bot to support other social media platforms.
- Add more robust error handling and logging for long-term scalability.
