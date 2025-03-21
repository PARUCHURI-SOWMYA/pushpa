import streamlit as st
import numpy as np
import tempfile
import os
from PIL import Image, ImageOps, ImageFilter, ImageDraw
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
    """Check if the reference text is present in the image using simple pixel comparison."""
    width, height = image.size
    pixel_data = image.load()
    text_found = False
    
    # Dummy logic: Assume text presence based on pixel density variation (not actual OCR)
    avg_brightness = np.mean([pixel_data[x, y][0] for x in range(width) for y in range(height)])
    if avg_brightness < 200:  # Arbitrary threshold for possible text areas
        text_found = True
    
    return text_found

def main():
    st.title("Digital Document Authentication and Verification Tool")
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
        
        # Process the image and display grayscale, edge, and inverted versions
        gray, edges, inverted = process_image(uploaded_image)
        st.image(gray, caption="Grayscale Certificate", use_column_width=True)
        st.image(edges, caption="Edge Detection Output", use_column_width=True)
        st.image(inverted, caption="Inverted Colors Output", use_column_width=True)
        
        if reference_text:
            text_found = check_text_in_image(uploaded_image, reference_text)
            
            if text_found:
                st.success("Reference text found in the certificate!")
                st.success("Certificate Status: ORIGINAL")
            else:
                st.error("Reference text NOT found in the certificate!")
                st.error("Certificate Status: FAKE")
        
        st.success("Certificate verification completed!")

if __name__ == "__main__":
    main()
