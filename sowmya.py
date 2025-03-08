import streamlit as st
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import difflib

# Try importing PDF library
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Try importing OCR library
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Function to extract text from a specific PDF page
def extract_text_from_page(file, page_number):
    try:
        if file.name.endswith(".pdf") and PDF_AVAILABLE:
            with pdfplumber.open(file) as pdf:
                if page_number < len(pdf.pages):
                    page = pdf.pages[page_number]
                    text = page.extract_text() or "No text found on this page."
                    return text
                else:
                    return "Invalid page number."
        else:
            return "PDF processing is unavailable or invalid file."
    except Exception as e:
        return f"Error extracting text: {e}"

# Function to extract images from a specific PDF page
def extract_images_from_page(file, page_number):
    images = []
    try:
        if PDF_AVAILABLE:
            with pdfplumber.open(file) as pdf:
                if page_number < len(pdf.pages):
                    page = pdf.pages[page_number]
                    for img in page.images:
                        image = page.to_image()
                        images.append(image.original)
    except Exception as e:
        st.error(f"Error extracting images: {e}")
    return images

# Function to apply image transformations
def process_image(image, mode):
    if mode == "Grayscale":
        return ImageOps.grayscale(image)
    elif mode == "Edge Detection":
        return image.convert("L").filter(ImageFilter.FIND_EDGES)
    elif mode == "Color Inversion":
        return ImageOps.invert(image.convert("RGB"))
    return image

# Function to compare text and highlight differences
def highlight_differences(original, extracted):
    diff = difflib.ndiff(original.split(), extracted.split())
    changes = [word for word in diff if word.startswith("+ ") or word.startswith("- ")]
    return "\n".join(changes) if changes else "No modifications detected."

# Certificate verification function
def verify_certificate(extracted_text, reference_text):
    if extracted_text.strip() == "":
        return "No text detected. Unable to verify."
    similarity = difflib.SequenceMatcher(None, extracted_text.lower(), reference_text.lower()).ratio()
    if similarity > 0.85:
        return "✅ Certificate is Original"
    else:
        return "❌ Certificate is Fake or Mismatched!"

# Streamlit UI
st.title("📜 Certificate & Document Verification Tool")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    # Extract total pages
    with pdfplumber.open(uploaded_file) as pdf:
        total_pages = len(pdf.pages)
    
    st.subheader("Select Page for Verification")
    page_number = st.number_input("Page Number", min_value=0, max_value=total_pages - 1, value=0)
    
    extracted_text = extract_text_from_page(uploaded_file, page_number)
    st.text_area("Extracted Text from Page", extracted_text, height=200)
    
    images = extract_images_from_page(uploaded_file, page_number)
    if images:
        st.subheader("Extracted Images from Page")
        selected_image = st.selectbox("Select an Image to Process", range(len(images)))
        image = images[selected_image]
        st.image(image, caption="Original Image", use_column_width=True)
        
        mode = st.selectbox("Select Image Processing Mode", ["Original", "Grayscale", "Edge Detection", "Color Inversion"])
        processed_img = process_image(image, mode)
        st.image(processed_img, caption=f"{mode} Output", use_column_width=True)
    else:
        st.write("No images found on this page.")
    
    doc_type = st.radio("Select Document Type", ["General Document", "Certificate Verification"])
    if doc_type == "General Document":
        reference_text = st.text_area("Paste Original Text for Verification", height=200)
        if st.button("Check for Tampering"):
            differences = highlight_differences(reference_text, extracted_text)
            st.subheader("Detected Changes")
            st.text_area("Highlighted Differences", differences, height=200)
    else:
        reference_certificate_text = st.text_area("Paste Expected Certificate Details", height=200)
        if st.button("Verify Certificate"):
            verification_result = verify_certificate(extracted_text, reference_certificate_text)
            st.subheader("Verification Result")
            st.write(verification_result)
