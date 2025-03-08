import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import difflib

# Attempt to import libraries and handle missing ones
try:
    import pytesseract
    from skimage.filters import sobel
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False

# Function to process image
def process_image(image, mode):
    if not LIBS_AVAILABLE:
        return image
    img = ImageOps.grayscale(image)
    img_array = np.array(img)
    
    if mode == "Grayscale":
        return img
    elif mode == "Edge Detection":
        edges = sobel(img_array)
        return Image.fromarray((edges * 255).astype(np.uint8))
    elif mode == "Color Inversion":
        return ImageOps.invert(image.convert("RGB"))
    return image

# Function to extract text
def extract_text(image):
    if LIBS_AVAILABLE:
        return pytesseract.image_to_string(image)
    return "Text extraction unavailable due to missing libraries."

# Function to compare text
def compare_text(original, modified):
    diff = difflib.ndiff(original.split(), modified.split())
    changes = '\n'.join([word for word in diff if word.startswith('+ ') or word.startswith('- ')])
    return changes if changes else "No modifications detected."

# Streamlit UI
st.title("📄 Digital Document Authenticator and Verification Tool")

uploaded_file = st.file_uploader("Upload a document (Image/PDF)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Document", use_column_width=True)
    
    mode = st.selectbox("Select Image Processing Mode", ["Original", "Grayscale", "Edge Detection", "Color Inversion"])
    processed_img = process_image(image, mode)
    st.image(processed_img, caption=f"{mode} Output", use_column_width=True)
    
    extracted_text = extract_text(image)
    st.subheader("Extracted Text")
    st.text_area("Text from Image", extracted_text, height=200)
    
    original_text = st.text_area("Paste Original Text for Verification", height=200)
    if st.button("Verify Text Authenticity") and original_text:
        differences = compare_text(original_text, extracted_text)
        st.subheader("Text Differences")
        st.text_area("Detected Changes", differences, height=200)
