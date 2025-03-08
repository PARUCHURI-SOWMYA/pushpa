import streamlit as st

# Try importing libraries and handle errors if they are missing
missing_libs = []

try:
    import numpy as np
except ImportError:
    missing_libs.append("numpy")

try:
    import pytesseract
except ImportError:
    missing_libs.append("pytesseract")

try:
    from PIL import Image, ImageOps
except ImportError:
    missing_libs.append("Pillow")

try:
    import difflib
except ImportError:
    missing_libs.append("difflib")

try:
    from skimage.filters import sobel
except ImportError:
    missing_libs.append("scikit-image")

# Show warning if any library is missing
if missing_libs:
    st.warning(f"⚠️ Some required libraries are missing: {', '.join(missing_libs)}. "
               f"Please install them using `pip install {' '.join(missing_libs)}`.")

# Function to process image
def process_image(image, mode):
    try:
        if "Pillow" in missing_libs or "numpy" in missing_libs or "scikit-image" in missing_libs:
            return image  # Return original if libraries are missing

        img = ImageOps.grayscale(image)  # Convert to grayscale using PIL
        img_array = np.array(img)  # Convert to NumPy array for processing

        if mode == "Grayscale":
            return img
        elif mode == "Edge Detection":
            edges = sobel(img_array)
            return Image.fromarray((edges * 255).astype(np.uint8))  # Normalize and convert back to image
        elif mode == "Color Inversion":
            inverted_img = ImageOps.invert(image.convert("RGB"))
            return inverted_img
        return image
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return image

# Function to extract text using Tesseract OCR
def extract_text(image):
    try:
        if "pytesseract" in missing_libs:
            return "⚠️ Text extraction is unavailable (pytesseract not installed)."
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"❌ Error extracting text: {e}"

# Function to compare text
def compare_text(original, modified):
    try:
        if "difflib" in missing_libs:
            return "⚠️ Text comparison is unavailable (difflib not installed)."
        diff = difflib.ndiff(original.split(), modified.split())
        changes = '\n'.join([word for word in diff if word.startswith('+ ') or word.startswith('- ')])
        return changes if changes else "✅ No modifications detected."
    except Exception as e:
        return f"❌ Error comparing text: {e}"

# Streamlit UI
st.title("📄 Digital Document Authentication and Verification Tool")

uploaded_file = st.file_uploader("Upload an Image Document (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Document", use_column_width=True)

        # Image Processing Options
        mode = st.selectbox("Select Image Processing Mode", ["Original", "Grayscale", "Edge Detection", "Color Inversion"])
        processed_img = process_image(image, mode)
        st.image(processed_img, caption=f"{mode} Output", use_column_width=True)

        # Text Extraction and Authentication
        extracted_text = extract_text(image)
        st.subheader("Extracted Text")
        st.text_area("Text from Image", extracted_text, height=200)

        # User-provided original text for comparison
        original_text = st.text_area("Paste Original Text for Verification", height=200)
        if st.button("Verify Text Authenticity") and original_text:
            differences = compare_text(original_text, extracted_text)
            st.subheader("Text Differences")
            st.text_area("Detected Changes", differences, height=200)

    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
