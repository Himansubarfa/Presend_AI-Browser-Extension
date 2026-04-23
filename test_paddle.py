# test_paddle.py (run once from project root, then delete)
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='en', use_angle_cls=False)
result = ocr.ocr("This is a test image with text to detect.")
print("PaddleOCR is installed and working!")