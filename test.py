from google.cloud import aiplatform
from google.cloud import aiplatform_v1
from google.cloud.aiplatform import gapic
import vertexai

project_id = "senri-insta-auto"

vertexai.init(project=project_id, location="us-central1")

model = GenerativeModel(model_name="gemini-1.0-pro-vision-001")

response = model.generate_content(
    [
        Part.from_uri(
            "gs://cloud-samples-data/generative-ai/image/scones.jpg",
            mime_type="downloaded_images/May_31.jpg",
        ),
        "What is shown in this image?",
    ]
)

print(response.text)