import streamlit as st

# import firebase_admin
# from firebase_admin import credentials, storage
from google.oauth2 import service_account
from google.cloud import storage
import os
import numpy as np

# Inject CSS
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1506744038136-46273834b3fb");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create credentials object from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["GCP"]
)

client = storage.Client(credentials=credentials, project=st.secrets["GCP"]["project_id"])
bucket = client.bucket(st.secrets["GCP"]["storage_bucket"])


def upload_image(image_data, folder_name, file_name, metadata=None):

    blob_path = f"{folder_name}/{file_name}"
    blob = bucket.blob(blob_path)

    if metadata:
        blob.metadata = metadata
    # Upload the file
    image_data.seek(0)  # Reset file pointer to the beginning
    blob.upload_from_file(image_data, content_type=image_data.type)
    # Make URL accessible (optional)
    # blob.make_public()

    print(f"File uploaded to {blob_path}")
    print(f"Public URL: {blob.public_url}")
    return blob.public_url


st.title("Testing")


st.write("Take a picture to upload so we can remember this special day!")

upload_package = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png", "heic"], key="image_uploader")

comment = st.text_area("Add a note with this image", placeholder="Add a note here...", key="image_note")

if st.button("Upload Image"):
    if upload_package is not None:
        # Upload the image
        public_url = upload_image(upload_package, "test_folder", f"testing{np.random.random()}.png", metadata={"note": comment})
        st.success(f"Image uploaded successfully!")
    else:
        st.error("Please upload an image file.")

