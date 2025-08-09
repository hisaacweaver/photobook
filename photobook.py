import streamlit as st

# import firebase_admin
# from firebase_admin import credentials, storage
from google.oauth2 import service_account
from google.cloud import storage
import os
import numpy as np
from datetime import timedelta
import random
from datetime import datetime

st.markdown("""

<style>
            .stAppHeader {display: none;}
            a[href^="https://streamlit.io/cloud"] {display: none;}
            a[href^="https://share.streamlit.io/user/hisaacweaver"] {display: none;}
            
</style>

""", unsafe_allow_html=True)


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


st.title("Benjamin and Emmy Wedding Photobook")

if st.query_params.get("view"):
    show_view_tab = True
else:
    show_view_tab = False

tab_titles = ["Upload Image"]
if show_view_tab:
    tab_titles.append("View Images")



wedding_words = [
    "bride", "groom", "ceremony", "reception", "vows", "rings", "bouquet",
    "flowers", "cake", "dance", "toast", "love", "celebration", "marriage",
    "honeymoon", "guests", "invitation", "dress", "tuxedo", "veil", "aisle",
    "altar", "bridesmaids", "groomsmen", "photographer", "music", "first dance",
    "champagne", "confetti", "decorations", "centerpiece", "wedding party",
    "wedding planner", "engagement", "proposal", "unity", "bliss", "commitment"
]

if not show_view_tab:
    

    st.write("Take a few pictures to upload so we can remember this special day!")

    upload_package = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png", "heic"], key="image_uploader", accept_multiple_files=True)

    adding_note = st.toggle("Add a note with this image", key="add_note")
    comment = ""
    if adding_note:
        comment = st.text_area("", placeholder="Add a note here...", key="image_note")

    if st.button("Upload Image"):
        if upload_package:
            if not isinstance(upload_package, list):
                upload_package = [upload_package]
            for idx, image_file in enumerate(upload_package):
                random_word = random.choice(wedding_words)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{timestamp}_{random_word}_{idx}.png"
                public_url = upload_image(image_file, "Benjamin_Emmy_Wedding", file_name, metadata={"note": comment})
            st.success(f"{len(upload_package)} image{'' if len(upload_package) == 1 else 's'} uploaded successfully!")
        else:
            st.error("Please upload at least one image file.")

else:
    tabs = st.tabs(tab_titles)
    with tabs[0]:
            

        st.write("Take a few pictures to upload so we can remember this special day!")

        upload_package = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png", "heic"], key="image_uploader", accept_multiple_files=True)

        adding_note = st.toggle("Add a note with this image", key="add_note")
        comment = ""
        if adding_note:
            comment = st.text_area("", placeholder="Add a note here...", key="image_note")

        if st.button("Upload Image"):
            if upload_package:
                if not isinstance(upload_package, list):
                    upload_package = [upload_package]
                for idx, image_file in enumerate(upload_package):
                    random_word = random.choice(wedding_words)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_name = f"{timestamp}_{random_word}_{idx}.png"
                    public_url = upload_image(image_file, "Benjamin_Emmy_Wedding", file_name, metadata={"note": comment})
                st.success(f"{len(upload_package)} image{'' if len(upload_package) == 1 else 's'} uploaded successfully!")
            else:
                st.error("Please upload at least one image file.")



    

    with tabs[1]:
        st.write("View your uploaded images here.")
        if st.button("Refresh Image List"):
            st.cache_data.clear()
            st.rerun()

        # List all blobs in the bucket
        @st.cache_data()
        def get_image_names():
            blobs = bucket.list_blobs(prefix="Benjamin_Emmy_Wedding/")
            return [blob.name for blob in blobs]
        
        names = get_image_names()
        # for n in names:
        #     st.write(n)

        def get_image_url(blob_name):
            blob = bucket.blob(blob_name)
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=60),
                method="GET"
            )
            return url
        
            
        urls = [get_image_url(name) for name in names]


        cols_per_row = 4  # Number of images per row
        cols = st.columns(cols_per_row)

        for idx, url in enumerate(urls):
            col = cols[idx % cols_per_row]
            # Display smaller image tile (adjust width as needed)
            col.image(url, width=150)
