import streamlit as st
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import difflib
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Function to extract text from a PDF and split into pages
def extract_text_from_pdf(file):
    if pdfplumber:
        with pdfplumber.open(file) as pdf:
            return [page.extract_text() or "" for page in pdf.pages]
    return []

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
    pages_text = extract_text_from_pdf(uploaded_file)
    if pages_text:
        selected_page = st.selectbox("Select Page for Verification", range(1, len(pages_text) + 1))
        extracted_text = pages_text[selected_page - 1]
        st.text_area(f"Extracted Text from Page {selected_page}", extracted_text, height=200)
    
    # Image Processing Options
    mode = st.selectbox("Select Image Processing Mode", ["Original", "Grayscale", "Edge Detection", "Color Inversion"])
    image = Image.new('RGB', (400, 300), (255, 255, 255))  # Placeholder image
    processed_image = process_image(image, mode)
    st.image(processed_image, caption=f"{mode} Output", use_container_width=True)
    
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
