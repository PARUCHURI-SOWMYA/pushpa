import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import difflib

# Try importing OCR and PDF libraries
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import PyPDF2  # Replacing fitz with PyPDF2 for PDF processing
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Function to extract text from PDF or Image
def extract_text(file):
    text = ""
    try:
        if file.name.endswith(".pdf"):
            if PDF_AVAILABLE:
                pdf_reader = PyPDF2.PdfReader(file)
                text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
            else:
                st.warning("PDF processing not available. Install PyPDF2 for better results.")
        else:
            image = Image.open(file)
            if OCR_AVAILABLE:
                text = pytesseract.image_to_string(image)
            else:
                st.warning("OCR (Tesseract) not available. Text extraction may not work.")
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
    else:
        reference_certificate_text = st.text_area("Paste Expected Certificate Details", height=200)
        if st.button("Verify Certificate"):
            verification_result = verify_certificate(extracted_text, reference_certificate_text)
            st.subheader("Verification Result")
            st.write(verification_result)
