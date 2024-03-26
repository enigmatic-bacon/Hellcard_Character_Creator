import cv2
import numpy as np
import pytesseract
from PIL import Image


def process_image(input_filename, result_filename="result.png"):
    """
    Applies Gaussian thresholding to an image and saves the result.

    Parameters:
    input_filename (str): The filename of the input image.
    output_filename (str): The filename to save the thresholded image to.

    Returns:
    str: The filename of the saved thresholded image.
    """
    # Read the image
    image = cv2.imread(input_filename)

    # Check if the image is loaded properly
    if image is None:
        print(f"Error: Unable to load image '{input_filename}'.")
        return None

    # Grayscale reduces 3-channel info into 1, making it easier to work on
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("grayscale.png", gray)

    # Gaussian Blur gives better results when thresholding to reduce edges from noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    cv2.imwrite("blur.png", blur)

    # Otsu's Threshold, in charge of splitting foreground from background in an image
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cv2.imwrite("thresh.png", thresh)

    # Remove noise
    # https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
    # Morph open performs:
    #    an errosion to get rid of orphaned pixels/noise
    #    followed by a dilation to restore the rest
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    cv2.imwrite("opening.png", opening)

    cv2.imwrite(result_filename, opening)


def match_template(img, template, debug=False, threshold=0.8, distance_threshold=10):
    img = cv2.imread(img)
    template = cv2.imread(template)
    w, h = template.shape[:-1]

    correlation = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(correlation >= threshold)
    if debug:
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        cv2.imwrite("debug/template_matching.png", img)

    # Poor man's Non-Maximum Suppression
    filtered_points = []
    for pt in zip(*loc[::-1]):  # Switch x and y coordinates
        too_close = any(
            np.linalg.norm(np.array(pt) - np.array(prev_pt)) < distance_threshold
            for prev_pt in filtered_points
        )
        if not too_close:
            filtered_points.append(pt)

    return filtered_points


def ocr(filename):
    """Perform OCR on an image

    Args:
        filename (string): The name of the file to OCR

    Returns:
    str: The text extracted from the captured area.
    """
    try:
        # Perform OCR on the saved image file
        text = pytesseract.image_to_string(
            # Page segmentation modes:
            #   0    Orientation and script detection (OSD) only.
            #   1    Automatic page segmentation with OSD.
            #   2    Automatic page segmentation, but no OSD, or OCR. (not implemented)
            #   3    Fully automatic page segmentation, but no OSD. (Default)
            #   4    Assume a single column of text of variable sizes.
            #   5    Assume a single uniform block of vertically aligned text.
            #   6    Assume a single uniform block of text.
            #   7    Treat the image as a single text line.
            #   8    Treat the image as a single word.
            #   9    Treat the image as a single word in a circle.
            #  10    Treat the image as a single character.
            #  11    Sparse text. Find as much text as possible in no particular order.
            #  12    Sparse text with OSD.
            #  13    Raw line. Treat the image as a single text line,
            Image.open(filename),
            lang="eng",
            config="--psm 11",
        )
        return text
    except pytesseract.TesseractError as error:
        print(f"An error occurred during OCR: {error}")
        return ""
