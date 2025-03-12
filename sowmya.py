import streamlit as st
import numpy as np
import tempfile
import os
from PIL import Image, ImageOps, ImageFilter
import pdf2image  # Alternative to PyMuPDF

def process_image(image):
    """Process the image to generate grayscale, edge detection, and color inversion outputs."""
    gray = ImageOps.grayscale(image)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    inverted = ImageOps.invert(image.convert("RGB"))
    return gray, edges, inverted

def load_pdf(file):
    """Convert uploaded PDF into images, one per page."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(file.read())
        temp_pdf_path = temp_pdf.name
    
    pages = pdf2image.convert_from_path(temp_pdf_path)
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
            image = pages[selected_page - 1]
            
            st.image(image, caption=f"Original Page {selected_page}", use_column_width=True)
            
            gray, edges, inverted = process_image(image)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(gray, caption="Grayscale", use_column_width=True)
            with col2:
                st.image(edges, caption="Edge Detection", use_column_width=True)
            with col3:
                st.image(inverted, caption="Color Inversion", use_column_width=True)
            
            st.success("Page verification completed! Check the visual indicators for tampering detection.")

if __name__ == "__main__":
    main()
