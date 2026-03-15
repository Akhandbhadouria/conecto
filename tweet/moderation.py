"""
Image Moderation Module
Uses NudeNet (ONNX-based) for real-time NSFW content detection.
Runs locally — no external API calls needed.
"""

import os
import logging
import tempfile
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

# Lazy-load the detector (heavy model, load once)
_detector = None


def _get_detector():
    """Lazy-load NudeDetector singleton to avoid startup overhead."""
    global _detector
    if _detector is None:
        from nudenet import NudeDetector
        _detector = NudeDetector()
        logger.info("NudeNet detector loaded successfully.")
    return _detector


# NudeNet label classes considered UNSAFE
UNSAFE_LABELS = {
    'FEMALE_BREAST_EXPOSED',
    'FEMALE_GENITALIA_EXPOSED',
    'MALE_GENITALIA_EXPOSED',
    'BUTTOCKS_EXPOSED',
    'ANUS_EXPOSED',
    'MALE_BREAST_EXPOSED',
}

# Confidence threshold — detections below this are ignored
CONFIDENCE_THRESHOLD = 0.45


def check_image(image_file):
    """
    Analyze an uploaded image file for NSFW content.
    
    Args:
        image_file: Django InMemoryUploadedFile or TemporaryUploadedFile
        
    Returns:
        dict: {
            'is_safe': bool,
            'detections': list of detected unsafe labels,
            'message': str description of result
        }
    """
    try:
        # Save the uploaded file to a temporary location for NudeNet
        # (NudeNet requires a file path, not a file object)
        image_file.seek(0)
        
        # Validate it's actually an image first
        try:
            img = Image.open(image_file)
            img.verify()
            image_file.seek(0)
        except Exception:
            return {
                'is_safe': False,
                'detections': ['INVALID_IMAGE'],
                'message': 'The uploaded file is not a valid image.'
            }
        
        # Write to temp file for NudeNet processing
        suffix = os.path.splitext(image_file.name)[1] if image_file.name else '.jpg'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            for chunk in image_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        try:
            detector = _get_detector()
            detections = detector.detect(tmp_path)
            
            # Filter for unsafe labels above confidence threshold
            unsafe_detections = [
                d for d in detections
                if d['class'] in UNSAFE_LABELS and d['score'] >= CONFIDENCE_THRESHOLD
            ]
            
            if unsafe_detections:
                labels = list(set(d['class'] for d in unsafe_detections))
                max_confidence = max(d['score'] for d in unsafe_detections)
                
                logger.warning(
                    f"NSFW content detected: {labels} "
                    f"(max confidence: {max_confidence:.2f})"
                )
                
                return {
                    'is_safe': False,
                    'detections': labels,
                    'message': (
                        'Your upload contains content that violates our '
                        'community guidelines. This action has been recorded.'
                    )
                }
            
            return {
                'is_safe': True,
                'detections': [],
                'message': 'Image passed moderation check.'
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"Image moderation error: {e}", exc_info=True)
        # Fail open — allow the image if moderation crashes
        # Change to fail-closed (return is_safe=False) for stricter policy
        return {
            'is_safe': True,
            'detections': [],
            'message': 'Moderation check skipped due to an internal error.'
        }


def preload_model():
    """
    Pre-load the NudeNet model at server startup.
    Call this from AppConfig.ready() for zero-latency on first upload.
    """
    try:
        _get_detector()
        logger.info("NudeNet model pre-loaded.")
    except Exception as e:
        logger.error(f"Failed to pre-load NudeNet model: {e}")
