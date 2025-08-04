import pytesseract
from PIL import Image
import os
import re
from flask import current_app

class OCRProcessor:
    def __init__(self):
        # Configure Tesseract path if needed (Windows)
        if os.name == 'nt':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            current_app.logger.error(f"OCR Error: {e}")
            return ""
    
    def extract_invoice_data(self, text):
        """Extract common invoice fields from OCR text"""
        invoice_data = {
            'invoice_number': None,
            'amount': None,
            'date': None,
            'vendor': None
        }
        
        # Extract invoice number
        invoice_patterns = [
            r'invoice\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'inv\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'#\s*([A-Z0-9\-]+)'
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_data['invoice_number'] = match.group(1)
                break
        
        # Extract amount
        amount_patterns = [
            r'total\s*:?\s*\$?([0-9,]+\.?[0-9]*)',
            r'amount\s*:?\s*\$?([0-9,]+\.?[0-9]*)',
            r'\$([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    invoice_data['amount'] = float(amount_str)
                    break
                except ValueError:
                    continue
        
        # Extract date
        date_patterns = [
            r'date\s*:?\s*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})',
            r'([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_data['date'] = match.group(1)
                break
        
        # Extract vendor (first line that looks like a company name)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and not re.match(r'^[0-9\/\-\$\s]+$', line):
                invoice_data['vendor'] = line
                break
        
        return invoice_data
    
    def process_receipt(self, image_path):
        """Process receipt and return extracted data"""
        text = self.extract_text_from_image(image_path)
        if text:
            return self.extract_invoice_data(text)
        return None