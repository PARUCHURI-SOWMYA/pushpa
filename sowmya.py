import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
import difflib
from skimage.filters import sobel

# Set Tesseract path if needed (Modify for your system)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to process image
def process_image(image, mode):
    img = np.array(image)
    if mode == "Grayscale":
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    elif mode == "Edge Detection":
        return sobel(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
    elif mode == "Color Inversion":
        return cv2.bitwise_not(img)
    return img

# Function to extract text
def extract_text(image):
    return pytesseract.image_to_string(image)

# Function to compare text
def compare_text(original, modified):
    diff = difflib.ndiff(original.split(), modified.split())
    changes = '\n'.join([word for word in diff if word.startswith('+ ') or word.startswith('- ')])
    return changes if changes else "No modifications detected."

# Streamlit UI
st.title("📄 Digital Document Authenticator and Verification Tool")

uploaded_file = st.file_uploader("Upload a document (Image/PDF)", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Document", use_column_width=True)
    
    # Image Processing Options
    mode = st.selectbox("Select Image Processing Mode", ["Original", "Grayscale", "Edge Detection", "Color Inversion"])
    processed_img = process_image(image, mode)
    st.image(processed_img, caption=f"{mode} Output", use_column_width=True, clamp=True)
    
    # Text Extraction and Authentication
    extracted_text = extract_text(image)
    st.subheader("Extracted Text")
    st.text_area("Text from Image", extracted_text, height=200)
    
    # User-provided original text for comparison
    original_text = st.text_area("Paste Original Text for Verification", height=200)
    if st.button("Verify Text Authenticity") and original_text:
        differences = compare_text(original_text, extracted_text)
        st.subheader("Text Differences")
        st.text_area("Detected Changes", differences, height=200)
