import io, os, tempfile
import fitz
from PIL import Image
import pytesseract

def _ocr_image(img):
    try:
        return pytesseract.image_to_string(img)
    except Exception:
        return ""

def extract_text_from_upload(uploaded_file):
    data = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        doc = fitz.open(stream=data, filetype="pdf")
        texts=[]
        for page in doc:
            txt = page.get_text("text")
            if not txt.strip():
                pix = page.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False)
                img = Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
                txt = _ocr_image(img)
            texts.append(txt)
        return "\n\n".join(texts), len(texts)
    img=Image.open(io.BytesIO(data)).convert("RGB")
    return _ocr_image(img), 1
