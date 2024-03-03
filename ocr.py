import pytesseract as ocr
from PIL import Image, ImageEnhance


def image_to_text(filepath: str) -> str:
    """ Converts image to a string using optical character recognition (OCR).
    :param filepath: filepath of the image
    :return:         string contents of the image
    """
    return ocr.image_to_string(filepath)


def enhance_image(filepath: str, contrast: float = 2.0, sharpness: float = 2.0) -> str:
    """ Enhances the image to be easier to OCR.
    :param filepath:  filepath of the image
    :param contrast:  contrast ratio (default 2.0)
    :param sharpness: sharpness ratio (default 2.0)
    :return:          image filepath
    """
    image = Image.open(filepath)

    # convert to greyscale
    image = image.convert('L')

    # enhance image and contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)

    image.save('enhanced_image.png', "PNG")

    return filepath
