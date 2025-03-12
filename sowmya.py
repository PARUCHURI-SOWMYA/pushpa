import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from PIL import Image
import fitz  # PyMuPDF

def process_image(image):
    """Process the image to generate grayscale, edge detection, and color inversion outputs."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    inverted = cv2.bitwise_not(image)
    return gray, edges, inverted

def load_pdf(file):
    """Convert uploaded PDF into images, one per page."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(file.read())
        temp_pdf_path = temp_pdf.name
    
    doc = fitz.open(temp_pdf_path)
    pages = []
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(img)
    
    doc.close()
    os.unlink(temp_pdf_path)  # Cleanup temporary file
    return pages

def main():
    st.title("Digital Document Authentication and Verification Tool")
    uploaded_file = st.file_uploader("Upload a PDF Document", type=["pdf"])
    
    if uploaded_file is not None:
        pages = load_pdf(uploaded_file)
        
        if pages:
            page_options = list(range(1, len(pages) + 1))
            selected_page = st.selectbox("Select a page to verify:", page_options)
            image = np.array(pages[selected_page - 1])
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            st.image(pages[selected_page - 1], caption=f"Original Page {selected_page}", use_column_width=True)
            
            gray, edges, inverted = process_image(image)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(gray, caption="Grayscale", use_column_width=True, channels="GRAY")
            with col2:
                st.image(edges, caption="Edge Detection", use_column_width=True, channels="GRAY")
            with col3:
                st.image(inverted, caption="Color Inversion", use_column_width=True)
            
            st.success("Page verification completed! Check the visual indicators for tampering detection.")

if __name__ == "__main__":
    main()
