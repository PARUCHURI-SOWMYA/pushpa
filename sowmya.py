import streamlit as st
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import difflib

# Function to extract text from a PDF (Basic Extraction)
def extract_text_from_pdf(file):
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text if text.strip() else "No text found."
    except ImportError:
        return "PDF processing is unavailable. Install PyPDF2 for better results."
    except Exception as e:
        return f"Error extracting text: {e}"

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
    return "✅ Certificate is Original" if similarity > 0.85 else "❌ Certificate is Fake or Mismatched!"

# Streamlit UI
st.title("📜 Certificate & Document Verification Tool")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    st.text_area("Extracted Text from PDF", extracted_text, height=200)
    
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
