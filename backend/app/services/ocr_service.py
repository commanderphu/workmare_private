"""
OCR Service using Tesseract
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
from typing import Optional
import numpy as np


class OCRService:
    """Service for extracting text from images using Tesseract OCR"""

    def __init__(self):
        # Configure Tesseract (assumes it's installed in the system)
        # For German language support
        self.languages = 'deu+eng'

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results

        Applies:
        - Grayscale conversion
        - Contrast enhancement
        - Noise reduction (light denoising)
        - Sharpening

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)  # Increase contrast by 50%

        # Denoise - light median filter to reduce noise while preserving edges
        image = image.filter(ImageFilter.MedianFilter(size=3))

        # Sharpen to improve text edges
        image = image.filter(ImageFilter.SHARPEN)

        # Optional: Increase brightness slightly
        brightness_enhancer = ImageEnhance.Brightness(image)
        image = brightness_enhancer.enhance(1.1)

        return image

    def extract_text(self, image_path: Path, preprocess: bool = True) -> tuple[str, float]:
        """
        Extract text from an image file

        Args:
            image_path: Path to the image file
            preprocess: Whether to apply image preprocessing (default: True)

        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            # Open image
            image = Image.open(image_path)

            # Apply preprocessing if enabled
            if preprocess:
                image = self.preprocess_image(image)

            # Get detailed OCR data for confidence
            data = pytesseract.image_to_data(
                image,
                lang=self.languages,
                output_type=pytesseract.Output.DICT
            )

            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=self.languages
            )

            # Calculate average confidence (excluding -1 values)
            confidences = [
                float(conf) for conf in data['conf']
                if conf != -1
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return text.strip(), avg_confidence / 100.0  # Normalize to 0-1

        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    def extract_from_pdf(self, pdf_path: Path) -> tuple[str, float]:
        """
        Extract text from PDF (first page only for now)

        Args:
            pdf_path: Path to the PDF file

        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            from pdf2image import convert_from_path

            # Convert first page to image
            images = convert_from_path(pdf_path, first_page=1, last_page=1)

            if not images:
                return "", 0.0

            # OCR the first page
            return self.extract_text_from_pil_image(images[0])

        except ImportError:
            raise Exception("pdf2image not installed. Install: pip install pdf2image")
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")

    def extract_text_from_pil_image(self, image: Image, preprocess: bool = True) -> tuple[str, float]:
        """
        Extract text from PIL Image object

        Args:
            image: PIL Image object
            preprocess: Whether to apply image preprocessing (default: True)

        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            # Apply preprocessing if enabled
            if preprocess:
                image = self.preprocess_image(image)

            # Get detailed OCR data for confidence
            data = pytesseract.image_to_data(
                image,
                lang=self.languages,
                output_type=pytesseract.Output.DICT
            )

            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=self.languages
            )

            # Calculate average confidence
            confidences = [
                float(conf) for conf in data['conf']
                if conf != -1
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return text.strip(), avg_confidence / 100.0

        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
