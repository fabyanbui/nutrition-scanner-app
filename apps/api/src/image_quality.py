import io
from PIL import Image

def analyze_image_quality(image_bytes: bytes) -> list:
    warnings = []
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        
        # Resolution check
        if width < 300 or height < 300:
            warnings.append("Low resolution image. Please move camera closer or use a higher quality image.")
            
        # Optional brightness heuristic (very basic grayscale mean)
        img_gray = img.convert("L")
        stat = img_gray.getextrema()
        # just a basic placeholder heuristic to not slow things down
        
        file_size_kb = len(image_bytes) / 1024
        if file_size_kb < 20:
            warnings.append("Image file size is very small, might be compressed or blurry.")
            
    except Exception as e:
        warnings.append("Could not fully analyze image quality.")
        
    return warnings
