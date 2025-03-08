import streamlit as st
import numpy as np
from PIL import Image, ImageOps
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

# Function to extract text from PDF
def extract_text(file):
    text = ""
    try:
        if file.name.endswith(".pdf"):
            if PDF_AVAILABLE:
                with pdfplumber.open(file) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    if not text.strip():
                        return "No extractable text found in the PDF."
            else:
                return "PDF processing is unavailable. Install pdfplumber for better results."
        else:
            return "Unsupported file type. Please upload a PDF."
    except Exception as e:
        return f"Error extracting text: {e}"
    return text

# Function to extract images from PDF
def extract_images(file):
    images = []
    try:
        if PDF_AVAILABLE:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
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
    st.subheader("Extracted Text from Document")
    extracted_text = extract_text(uploaded_file)
    st.text_area("Extracted Text", extracted_text, height=200)

    images = extract_images(uploaded_file)
    if images:
        st.subheader("Extracted Images from Document")
        selected_image = st.selectbox("Select an Image to Process", range(len(images)))
        image = images[selected_image]
        st.image(image, caption="Original Image", use_column_width=True)
        
        mode = st.selectbox("Select Image Processing Mode", ["Original", "Grayscale", "Edge Detection", "Color Inversion"])
        processed_img = process_image(image, mode)
        st.image(processed_img, caption=f"{mode} Output", use_column_width=True)
    else:
        st.write("No images found in the document.")

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
