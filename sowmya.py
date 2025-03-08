import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import difflib

try:
    import pytesseract
    from skimage.filters import sobel
    import fitz  # PyMuPDF
except ImportError as e:
    st.warning(f"Missing Library: {e}. Some features may not work.")

def process_image(image, mode):
    img = ImageOps.grayscale(image)
    img_array = np.array(img)
    if mode == "Grayscale":
        return img
    elif mode == "Edge Detection":
        edges = sobel(img_array)
        return Image.fromarray((edges * 255).astype(np.uint8))
    elif mode == "Color Inversion":
        inverted_img = ImageOps.invert(image.convert("RGB"))
        return inverted_img
    return image

def extract_text(image):
    try:
        return pytesseract.image_to_string(image)
    except:
        return "Text extraction not available."

def compare_text(original, modified):
    diff = difflib.ndiff(original.split(), modified.split())
    changes = '\n'.join([word for word in diff if word.startswith('+ ') or word.startswith('- ')])
    return changes if changes else "No modifications detected."

def verify_certificate(text, reference_text):
    return "Certificate is ORIGINAL." if text == reference_text else "Certificate is FAKE! Details mismatch."

st.title("📄 Digital Document Authenticator and Verification Tool")

uploaded_file = st.file_uploader("Upload a document (Image/PDF)", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "pdf":
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            pages = [page.get_pixmap() for page in doc]
            images = [Image.frombytes("RGB", [p.width, p.height], p.samples) for p in pages]
            selected_page = st.selectbox("Select a page for verification", list(range(1, len(images) + 1)))
            image = images[selected_page - 1]
        except:
            st.error("PDF processing not available.")
            image = None
    else:
        image = Image.open(uploaded_file)

    if image:
        st.image(image, caption="Selected Document Page", use_column_width=True)
        mode = st.selectbox("Select Image Processing Mode", ["Original", "Grayscale", "Edge Detection", "Color Inversion"])
        processed_img = process_image(image, mode)
        st.image(processed_img, caption=f"{mode} Output", use_column_width=True)
        extracted_text = extract_text(image)
        st.subheader("Extracted Text")
        st.text_area("Text from Document", extracted_text, height=200)
        original_text = st.text_area("Paste Original Text for Verification", height=200)
        if st.button("Verify Text Authenticity") and original_text:
            differences = compare_text(original_text, extracted_text)
            st.subheader("Text Differences")
            st.text_area("Detected Changes", differences, height=200)
        if st.button("Verify Certificate Authenticity"):
            reference_text = st.text_area("Enter Expected Certificate Details", height=200)
            result = verify_certificate(extracted_text, reference_text)
            st.subheader("Certificate Verification Result")
            st.write(result)
