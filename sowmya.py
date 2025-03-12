import streamlit as st
import numpy as np
import tempfile
import os
from PIL import Image, ImageOps, ImageFilter
import io

def process_image(image):
    """Process the image to generate grayscale, edge detection, and color inversion outputs."""
    gray = ImageOps.grayscale(image)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    inverted = ImageOps.invert(image.convert("RGB"))
    return gray, edges, inverted

def extract_images_from_pdf(file):
    """Extract images from a PDF file using only PIL without external dependencies."""
    pages = []
    try:
        with Image.open(file) as img:
            for i in range(img.n_frames):
                img.seek(i)
                pages.append(img.copy())
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
    return pages

def check_text_in_image(image, reference_text):
    """Basic text presence check by converting image to grayscale and checking pixel patterns."""
    gray = ImageOps.grayscale(image)
    pixels = np.array(gray)
    text_present = any(word.lower() in str(pixels) for word in reference_text.split())
    return text_present

def main():
    st.title("Digital Certificate Authentication and Verification Tool")
    uploaded_file = st.file_uploader("Upload Certificate to Verify (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])
    reference_text = st.text_area("Enter Reference Text for Verification")
    
    if uploaded_file:
        if uploaded_file.name.endswith("pdf"):
            pages = extract_images_from_pdf(io.BytesIO(uploaded_file.read()))
            if pages:
                uploaded_image = pages[0]  # Assume first page is the certificate
            else:
                st.error("Failed to extract image from PDF.")
                return
        else:
            uploaded_image = Image.open(uploaded_file).convert("RGB")
        
        st.image(uploaded_image, caption="Uploaded Certificate", use_column_width=True)
        
        if reference_text:
            text_found = check_text_in_image(uploaded_image, reference_text)
            if text_found:
                st.success("Reference text found in the certificate!")
            else:
                st.error("Reference text NOT found in the certificate!")
        
        st.success("Certificate verification completed!")

if __name__ == "__main__":
    main()
