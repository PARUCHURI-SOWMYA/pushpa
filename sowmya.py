import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import difflib

# Try importing required libraries and handle errors
try:
    import fitz  # PyMuPDF for PDFs
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import pytesseract  # OCR for text extraction
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Function to extract text from PDF or Image
def extract_text(file):
    text = ""
    try:
        if file.name.endswith(".pdf"):
            if PDF_AVAILABLE:
                with fitz.open(stream=file.read(), filetype="pdf") as doc:
                    text = "\n".join(page.get_text("text") for page in doc)
            else:
                st.warning("PDF processing is not available. Install `PyMuPDF` to enable it.")
        else:
            image = Image.open(file)
            if OCR_AVAILABLE:
                text = pytesseract.image_to_string(image)
            else:
                st.warning("OCR (Tesseract) is not available. Install `pytesseract` for text extraction.")
    except Exception as e:
        st.error(f"Error extracting text: {e}")
    return text

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

uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
if uploaded_file:
    st.subheader("Extracted Text from Document")
    extracted_text = extract_text(uploaded_file)
    st.text_area("Extracted Text", extracted_text, height=200)

    doc_type = st.radio("Select Document Type", ["General Document", "Certificate Verification"])
    
    if doc_type == "General Document":
        reference_text = st.text_area("Paste Original Text for Verification", height=200)
        if st.button("Check for Tampering"):
            differences = highlight_differences(reference_text, extracted_text)
            st.subheader("Detected Changes")
            st.text_area("Highlighted Differences", differences, height=200)

    else:  # Certificate Verification
        reference_certificate_text = st.text_area("Paste Expected Certificate Details", height=200)
        if st.button("Verify Certificate"):
            verification_result = verify_certificate(extracted_text, reference_certificate_text)
            st.subheader("Verification Result")
            st.write(verification_result)
