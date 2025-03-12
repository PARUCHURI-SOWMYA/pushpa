import streamlit as st
import os
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Set up the upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def convert_pdf_to_images(pdf_path):
    """Convert PDF pages to images and return their file paths."""
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(UPLOAD_FOLDER, f'page_{i + 1}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths

def process_image(image_path):
    """Apply grayscale, edge detection, and color inversion."""
    image = cv2.imread(image_path)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(grayscale, 100, 200)
    inverted = cv2.bitwise_not(image)
    
    return grayscale, edges, inverted

def extract_text(image_path):
    """Extract text from an image using Tesseract OCR."""
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Streamlit UI
st.title("📜 Digital Document Authentication & Verification Tool")

uploaded_file = st.file_uploader("Upload a PDF Document", type=["pdf"])

if uploaded_file is not None:
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("File uploaded successfully!")
    
    # Convert PDF to images
    page_images = convert_pdf_to_images(file_path)
    if page_images:
        selected_page = st.selectbox("Select a page to verify:", [f"Page {i+1}" for i in range(len(page_images))])
        page_index = int(selected_page.split()[1]) - 1
        selected_page_path = page_images[page_index]
        
        # Display original page
        st.image(selected_page_path, caption="Original Document Page", use_column_width=True)
        
        # Process selected page
        grayscale, edges, inverted = process_image(selected_page_path)
        
        # Display processed images
        st.image(grayscale, caption="Grayscale Version", use_column_width=True)
        st.image(edges, caption="Edge Detection", use_column_width=True)
        st.image(inverted, caption="Color Inversion", use_column_width=True)
        
        # Extract and verify text
        extracted_text = extract_text(selected_page_path)
        st.subheader("Extracted Text:")
        st.text_area("", extracted_text, height=150)
        
        st.success("Processing complete! Verify the extracted text and image variations for tampering detection.")
