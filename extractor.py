import pytesseract
import fitz
from PIL import Image 
from typing import Union, List, Optional

def extract_text_from_image(image_path: Optional[str]):
    # Load the image 
    if not image_path:
        image_path = "images/img_0"
    image = Image.open(image_path)

    # Preform OCR using pyttesseract 
    extracted_text = pytesseract.image_to_string(image)

    return extracted_text

def extract_text_from_pdf(
    pdf_path: str,
    start: Optional[int]=None, 
    stop: Optional[int]=None
    ) -> List[str]:
    text = []
    n = 0
    
    # Create a range if we want to loop over it
    pages: Optional[List] = None
    if start and stop:
        pages = list(range(start - 1, stop))
    
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            #print(f'Page ({n + 1})')
            # Skip if not in range
            if pages and n not in pages:
                n += 1
                continue
            n += 1
            
            # Append to text obj
            text.append(page.get_text("text") + "\n")
    return text