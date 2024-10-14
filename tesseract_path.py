import os
import pytesseract


# local Tesseract
# os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Live Tesseract
# os.environ['TESSDATA_PREFIX'] = '/usr/local/share/tessdata/'
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'