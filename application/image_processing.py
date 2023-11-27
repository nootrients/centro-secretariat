from PIL import Image

import pytesseract

import cv2
import numpy as np

import re, io, logging

from django.core.files.uploadedfile import InMemoryUploadedFile



# CONSTANTS

# Only on local development
# Dockerfile will handle this on deployment
# pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

logging.basicConfig(level=logging.DEBUG)

def extract_id_info(national_id_content, national_id_name):
    if national_id_name:
        logging.debug(f'national_id name: {national_id_name}')
        
    if national_id_content:
        nparr = np.fromstring(national_id_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 

        if img is not None:
            bordered_img = cv2.copyMakeBorder(
                src=img,
                top=20,
                bottom=20,
                left=20,
                right=20,
                borderType=cv2.BORDER_CONSTANT,
                value=(255, 255, 255))

            # Remove Image Noise
            def noise_removal(image):
                kernel = np.ones((1, 1), np.uint8)
                image = cv2.dilate(image, kernel, iterations=1)
                kernel = np.ones((1, 1), np.uint8)
                image = cv2.erode(image, kernel, iterations=1)
                image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
                image = cv2.medianBlur(image, 3)

                return (image)

            inverted_image = cv2.bitwise_not(img)                                                   # Invert image, Omitted

            desired_dpi = 300

            original_width, original_height = img.shape[1], img.shape[0]
            new_width = int(original_width * (desired_dpi / 72.0))                                  # 72 DPI is the default DPI for most images
            new_height = int(original_height * (desired_dpi / 72.0))

            resized_image = cv2.resize(img, (new_width, new_height))                                # Resize image to 300 DPI, Omitted

            # Grayscaling
            def grayscale(image):
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            gray_image = grayscale(bordered_img)

            gau_image = cv2.GaussianBlur(src=gray_image, ksize=(3, 3), sigmaX=0, sigmaY=0)          # Applying Gaussian Blur, Omitted


            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))                           # Not in use, inaccurate
            clahe_img = clahe.apply(gray_image)

            thresh, im_bw = cv2.threshold(gray_image, 160, 240, type=cv2.THRESH_BINARY)             # Binarize Image
            
            no_noise = noise_removal(im_bw)                                                         # Removing Image noise

            # Dilation for font-thickening
            def thick_font(image):                                                                  
                image = cv2.bitwise_not(image)
                kernel = np.ones((1, 1), np.uint8)
                image = cv2.dilate(image, kernel, iterations=1)

                image = cv2.bitwise_not(image)

                return (image)

            dilated = thick_font(im_bw)                                                              # Not in use, inaccurate

            image_to_text = pytesseract.image_to_string(no_noise, lang='eng')
            
            logging.debug(f"Text Extracted: {image_to_text}")
            
            # Initializing variable (list) to store extracted data from the ID
            extracted_info = {
                'lastname': None,
                'firstname': None,
                'middlename': None
            }
            
            generic_pattern = r"([A-Z\s]+)(?=\s|$)"
            
            field_patterns = [
                ('lastname', [
                            'Apelyido/Last Name', 'Apelyido: Last Name', 'Apelyido/Last Name.', 'Apelyido: Last Name.', 'Apelyido/Last Name:', 'Apelyido: Last Name:', 
                            'Apelyido/Lost Name', 'Apelyido: Lost Name', 'Apelyido/Lost Name.', 'Apelyido: Lost Name.', 'Apelyido/Lost Name:', 'Apelyido: Lost Name:', 
                            'Apelyido/Last Nome', 'Apelyido: Last Nome', 'Apelyido/Last Nome.', 'Apelyido: Last Nome.', 'Apelyido/Last Nome:', 'Apelyido: Last Nome:', 
                            'Apelyido/Lost Nome', 'Apelyido: Lost Nome', 'Apelyido/Lost Nome.', 'Apelyido: Lost Nome.', 'Apelyido/Lost Nome:', 'Apelyido: Lost Nome:', 
                            'Apetyido/Last Name', 'Apetyido: Last Name', 'Apetyido/Last Name.', 'Apetyido: Last Name.', 'Apetyido/Last Name:', 'Apetyido: Last Name:', 
                            'Apetyido/Lost Name', 'Apetyido: Lost Name', 'Apetyido/Lost Name.', 'Apetyido: Lost Name.', 'Apetyido/Lost Name:', 'Apetyido: Lost Name:', 
                            'Apetyido/Last Nome', 'Apetyido: Last Nome', 'Apetyido/Last Nome.', 'Apetyido: Last Nome.', 'Apetyido/Last Nome:', 'Apetyido: Last Nome:', 
                            'Apetyido/Lost Nome', 'Apetyido: Lost Nome', 'Apetyido/Lost Nome.', 'Apetyido: Lost Nome.', 'Apetyido/Lost Nome:', 'Apetyido: Lost Nome:', 
                            'Apeiyido/Last Nome', 'Apeiyido: Last Nome', 'Apeiyido/Last Nome.', 'Apeiyido: Last Nome.', 'Apeiyido/Last Nome:', 'Apeiyido: Last Nome:', 
                            'Apeiyido/Lost Nome', 'Apeiyido: Lost Nome', 'Apeiyido/Lost Nome.', 'Apeiyido: Lost Nome.', 'Apeiyido/Lost Nome:', 'Apeiyido: Lost Nome:', 

                            'Apelyido/tast Name', 'Apelyido: tast Name', 'Apelyido/tast Name.', 'Apelyido: tast Name.', 'Apelyido/tast Name:', 'Apelyido: tast Name:', 
                            'Apelyido/tast Nome', 'Apelyido: tast Nome', 'Apelyido/tast Nome.', 'Apelyido: tast Nome.', 'Apelyido/tast Nome:', 'Apelyido: tast Nome:', 
                            'Apelyido/tost Name', 'Apelyido: tost Name', 'Apelyido/tost Name.', 'Apelyido: tost Name.', 'Apelyido/tost Name:', 'Apelyido: tost Name:', 
                            'Apelyido/tost Nome', 'Apelyido: tost Nome', 'Apelyido/tost Nome.', 'Apelyido: tost Nome.', 'Apelyido/tost Nome:', 'Apelyido: tost Nome:',
                            'Apetyido/tast Name', 'Apetyido: tast Name', 'Apetyido/tast Name.', 'Apetyido: tast Name.', 'Apetyido/tast Name:', 'Apetyido: tast Name:', 
                            'Apetyido/tast Nome', 'Apetyido: tast Nome', 'Apetyido/tast Nome.', 'Apetyido: tast Nome.', 'Apetyido/tast Nome:', 'Apetyido: tast Nome:', 
                            'Apetyido/tost Name', 'Apetyido: tost Name', 'Apetyido/tost Name.', 'Apetyido: tost Name.', 'Apetyido/tost Name:', 'Apetyido: tost Name:', 
                            'Apetyido/tost Nome', 'Apetyido: tost Nome', 'Apetyido/tost Nome.', 'Apetyido: tost Nome.', 'Apetyido/tost Nome:', 'Apetyido: tost Nome:', 
                            'Apeiyido/tast Name', 'Apeiyido: tast Name', 'Apeiyido/tast Name.', 'Apeiyido: tast Name.', 'Apeiyido/tast Name:', 'Apeiyido: tast Name:', 
                            'Apeiyido/tast Nome', 'Apeiyido: tast Nome', 'Apeiyido/tast Nome.', 'Apeiyido: tast Nome.', 'Apeiyido/tast Nome:', 'Apeiyido: tast Nome:', 
                            'Apeiyido/tost Name', 'Apeiyido: tost Name', 'Apeiyido/tost Name.', 'Apeiyido: tost Name.', 'Apeiyido/tost Name:', 'Apeiyido: tost Name:', 
                            'Apeiyido/tost Nome', 'Apeiyido: tost Nome', 'Apeiyido/tost Nome.', 'Apeiyido: tost Nome.', 'Apeiyido/tost Nome:', 'Apeiyido: tost Nome:', 

                            'Apeyido/Last Name', 'Apeyido: Last Name', 'Apeyido/Last Name.', 'Apeyido: Last Name.', 'Apeyido/Last Name:', 'Apeyido: Last Name:', 
                            'Apeyido/Lost Name', 'Apeyido: Lost Name', 'Apeyido/Lost Name.', 'Apeyido: Lost Name.', 'Apeyido/Lost Name:', 'Apeyido: Lost Name:', 
                            'Apeyido/Last Nome', 'Apeyido: Last Nome', 'Apeyido/Last Nome.', 'Apeyido: Last Nome.', 'Apeyido/Last Nome:', 'Apeyido: Last Nome:', 
                            'Apeyido/Lost Nome', 'Apeyido: Lost Nome', 'Apeyido/Lost Nome.', 'Apeyido: Lost Nome.', 'Apeyido/Lost Nome:', 'Apeyido: Lost Nome:', 
                            'Apeyido/tast Name', 'Apeyido: tast Name', 'Apeyido/tast Name.', 'Apeyido: tast Name.', 'Apeyido/tast Name:', 'Apeyido: tast Name:', 
                            'Apeyido/tost Name', 'Apeyido: tost Name', 'Apeyido/tost Name.', 'Apeyido: tost Name.', 'Apeyido/tost Name:', 'Apeyido: tost Name:', 
                            'Apeyido/tast Nome', 'Apeyido: tast Nome', 'Apeyido/tast Nome.', 'Apeyido: tast Nome.', 'Apeyido/tast Nome:', 'Apeyido: tast Nome:', 
                            'Apeyido/tost Nome', 'Apeyido: tost Nome', 'Apeyido/tost Nome.', 'Apeyido: tost Nome.', 'Apeyido/tost Nome:', 'Apeyido: tost Nome:', 
                            ]),

                ('firstname', ['Mga Pangalan/Given Names', 'Mga Pangalan: Given Names', 'Mga Pangalan/Given Names.', 'Mga Pangalan: Given Names.', 'Mga Pangalan/Given Names:', 'Mga Pangalan: Given Names:',
                            'Mga Pangalan/G:ven Names', 'Mga Pangalan: G:ven Names', 'Mga Pangalan/G:ven Names.', 'Mga Pangalan: G:ven Names.', 'Mga Pangalan/G:ven Names:', 'Mga Pangalan: G:ven Names:',
                            'Mga Pangalan/Given Nomes', 'Mga Pangalan: Given Nomes', 'Mga Pangalan/Given Nomes.', 'Mga Pangalan: Given Nomes.', 'Mga Pangalan/Given Nomes:', 'Mga Pangalan: Given Nomes:',
                            'Mga Pangalan/G:ven Nomes', 'Mga Pangalan: G:ven Nomes', 'Mga Pangalan/G:ven Nomes.', 'Mga Pangalan: G:ven Nomes.', 'Mga Pangalan/G:ven Nomes:', 'Mga Pangalan: G:ven Nomes:',
                            'Mga Pangatan/Given Names', 'Mga Pangatan: Given Names', 'Mga Pangatan/Given Names.', 'Mga Pangatan: Given Names.', 'Mga Pangatan/Given Names:', 'Mga Pangatan: Given Names:',
                            'Mga Pangatan/G:ven Names', 'Mga Pangatan: G:ven Names', 'Mga Pangatan/G:ven Names.', 'Mga Pangatan: G:ven Names.', 'Mga Pangatan/G:ven Names:', 'Mga Pangatan: G:ven Names:',
                            'Mga Pangatan/Given Nomes', 'Mga Pangatan: Given Nomes', 'Mga Pangatan/Given Nomes.', 'Mga Pangatan: Given Nomes.', 'Mga Pangatan/Given Nomes:', 'Mga Pangatan: Given Nomes:',
                            'Mga Pangatan/G:ven Nomes', 'Mga Pangatan: G:ven Nomes', 'Mga Pangatan/G:ven Nomes.', 'Mga Pangatan: G:ven Nomes.', 'Mga Pangatan/G:ven Nomes:', 'Mga Pangatan: G:ven Nomes:',
                        
                            'Mga Pangsian/Given Names', 'Mga Pangsian: Given Names', 'Mga Pangsian/Given Names.', 'Mga Pangsian: Given Names.', 'Mga Pangsian/Given Names:', 'Mga Pangsian: Given Names:', 
                            'Mga Pangsian/G:ven Names', 'Mga Pangsian: G:ven Names', 'Mga Pangsian/G:ven Names.', 'Mga Pangsian: G:ven Names.', 'Mga Pangsian/G:ven Names:', 'Mga Pangsian: G:ven Names:', 
                            'Mga Pangsian/Given Nomes', 'Mga Pangsian: Given Nomes', 'Mga Pangsian/Given Nomes.', 'Mga Pangsian: Given Nomes.', 'Mga Pangsian/Given Nomes:', 'Mga Pangsian: Given Nomes:', 
                            'Mga Pangsian/G:ven Nomes', 'Mga Pangsian: G:ven Nomes', 'Mga Pangsian/G:ven Nomes.', 'Mga Pangsian: G:ven Nomes.', 'Mga Pangsian/G:ven Nomes:', 'Mga Pangsian: G:ven Nomes:', 
                            'Mga Pangstan/Given Names', 'Mga Pangstan: Given Names', 'Mga Pangstan/Given Names.', 'Mga Pangstan: Given Names.', 'Mga Pangstan/Given Names:', 'Mga Pangstan: Given Names:', 
                            'Mga Pangstan/G:ven Names', 'Mga Pangstan: G:ven Names', 'Mga Pangstan/G:ven Names.', 'Mga Pangstan: G:ven Names.', 'Mga Pangstan/G:ven Names:', 'Mga Pangstan: G:ven Names:', 
                            'Mga Pangstan/Given Nomes', 'Mga Pangstan: Given Nomes', 'Mga Pangstan/Given Nomes.', 'Mga Pangstan: Given Nomes.', 'Mga Pangstan/Given Nomes:', 'Mga Pangstan: Given Nomes:', 
                            'Mga Pangstan/G:ven Nomes', 'Mga Pangstan: G:ven Nomes', 'Mga Pangstan/G:ven Nomes.', 'Mga Pangstan: G:ven Nomes.', 'Mga Pangstan/G:ven Nomes:', 'Mga Pangstan: G:ven Nomes:',

                            'Maa Pangalan/G:ven Nomes', 'Maa Pangalan: G:ven Nomes', 'Maa Pangalan/G:ven Nomes.', 'Maa Pangalan: G:ven Nomes.', 'Maa Pangalan/G:ven Nomes:', 'Maa Pangalan: G:ven Nomes:', 
                            'Maa Pangalan/Given Nomes', 'Maa Pangalan: Given Nomes', 'Maa Pangalan/Given Nomes.', 'Maa Pangalan: Given Nomes.', 'Maa Pangalan/Given Nomes:', 'Maa Pangalan: Given Nomes:',
                            'Maa Pangalan/G:ven Names', 'Maa Pangalan: G:ven Names', 'Maa Pangalan/G:ven Names.', 'Maa Pangalan: G:ven Names.', 'Maa Pangalan/G:ven Names:', 'Maa Pangalan: G:ven Names:',
                            'Maa Pangalan/Given Names', 'Maa Pangalan: Given Names', 'Maa Pangalan/Given Names.', 'Maa Pangalan: Given Names.', 'Maa Pangalan/Given Names:', 'Maa Pangalan: Given Names:',
                            'Maa Pangatan/G:ven Nomes', 'Maa Pangatan: G:ven Nomes', 'Maa Pangatan/G:ven Nomes.', 'Maa Pangatan: G:ven Nomes.', 'Maa Pangatan/G:ven Nomes:', 'Maa Pangatan: G:ven Nomes:',
                            'Maa Pangatan/Given Nomes', 'Maa Pangatan: Given Nomes', 'Maa Pangatan/Given Nomes.', 'Maa Pangatan: Given Nomes.', 'Maa Pangatan/Given Nomes:', 'Maa Pangatan: Given Nomes:', 
                            'Maa Pangatan/G:ven Names', 'Maa Pangatan: G:ven Names', 'Maa Pangatan/G:ven Names.', 'Maa Pangatan: G:ven Names.', 'Maa Pangatan/G:ven Names:', 'Maa Pangatan: G:ven Names:',
                            'Maa Pangatan/Given Names', 'Maa Pangatan: Given Names', 'Maa Pangatan/Given Names.', 'Maa Pangatan: Given Names.', 'Maa Pangatan/Given Names:', 'Maa Pangatan: Given Names:',
                                
                            'Mega Pangalan/Given Names', 'Mega Pangalan: Given Names', 'Mega Pangalan/Given Names.', 'Mega Pangalan: Given Names.', 'Mega Pangalan/Given Names:', 'Mega Pangalan: Given Names:',
                            'Mega Pangalan/G:ven Names', 'Mega Pangalan: G:ven Names', 'Mega Pangalan/G:ven Names.', 'Mega Pangalan: G:ven Names.', 'Mega Pangalan/G:ven Names:', 'Mega Pangalan: G:ven Names:',
                            'Mega Pangalan/Given Nomes', 'Mega Pangalan: Given Nomes', 'Mega Pangalan/Given Nomes.', 'Mega Pangalan: Given Nomes.', 'Mega Pangalan/Given Nomes:', 'Mega Pangalan: Given Nomes:',
                            'Mega Pangalan/G:ven Nomes', 'Mega Pangalan: G:ven Nomes', 'Mega Pangalan/G:ven Nomes.', 'Mega Pangalan: G:ven Nomes.', 'Mega Pangalan/G:ven Nomes:', 'Mega Pangalan: G:ven Nomes:', 
                            'Mega Pangatan/Given Names', 'Mega Pangatan: Given Names', 'Mega Pangatan/Given Names.', 'Mega Pangatan: Given Names.', 'Mega Pangatan/Given Names:', 'Mega Pangatan: Given Names:',
                            'Mega Pangatan/G:ven Names', 'Mega Pangatan: G:ven Names', 'Mega Pangatan/G:ven Names.', 'Mega Pangatan: G:ven Names.', 'Mega Pangatan/G:ven Names:', 'Mega Pangatan: G:ven Names:',
                            'Mega Pangatan/Given Nomes', 'Mega Pangatan: Given Nomes', 'Mega Pangatan/Given Nomes.', 'Mega Pangatan: Given Nomes.', 'Mega Pangatan/Given Nomes:', 'Mega Pangatan: Given Nomes:',
                            'Mega Pangatan/G:ven Nomes', 'Mega Pangatan: G:ven Nomes', 'Mega Pangatan/G:ven Nomes.', 'Mega Pangatan: G:ven Nomes.', 'Mega Pangatan/G:ven Nomes:', 'Mega Pangatan: G:ven Nomes:',

                            'Miga Pangalan/Given Names', 'Miga Pangalan: Given Names', 'Miga Pangalan/Given Names.', 'Miga Pangalan: Given Names.', 'Miga Pangalan/Given Names:', 'Miga Pangalan: Given Names:', 
                            'Miga Pangalan/G:ven Names', 'Miga Pangalan: G:ven Names', 'Miga Pangalan/G:ven Names.', 'Miga Pangalan: G:ven Names.', 'Miga Pangalan/G:ven Names:', 'Miga Pangalan: G:ven Names:', 
                            'Miga Pangalan/Given Nomes', 'Miga Pangalan: Given Nomes', 'Miga Pangalan/Given Nomes.', 'Miga Pangalan: Given Nomes.', 'Miga Pangalan/Given Nomes:', 'Miga Pangalan: Given Nomes:', 
                            'Miga Pangalan/G:ven Nomes', 'Miga Pangalan: G:ven Nomes', 'Miga Pangalan/G:ven Nomes.', 'Miga Pangalan: G:ven Nomes.', 'Miga Pangalan/G:ven Nomes:', 'Miga Pangalan: G:ven Nomes:', 
                            'Miga Pangatan/Given Names', 'Miga Pangatan: Given Names', 'Miga Pangatan/Given Names.', 'Miga Pangatan: Given Names.', 'Miga Pangatan/Given Names:', 'Miga Pangatan: Given Names:', 
                            'Miga Pangatan/G:ven Names', 'Miga Pangatan: G:ven Names', 'Miga Pangatan/G:ven Names.', 'Miga Pangatan: G:ven Names.', 'Miga Pangatan/G:ven Names:', 'Miga Pangatan: G:ven Names:', 
                            'Miga Pangatan/Given Nomes', 'Miga Pangatan: Given Nomes', 'Miga Pangatan/Given Nomes.', 'Miga Pangatan: Given Nomes.', 'Miga Pangatan/Given Nomes:', 'Miga Pangatan: Given Nomes:',
                            'Miga Pangatan/G:ven Nomes', 'Miga Pangatan: G:ven Nomes', 'Miga Pangatan/G:ven Nomes.', 'Miga Pangatan: G:ven Nomes.', 'Miga Pangatan/G:ven Nomes:', 'Miga Pangatan: G:ven Nomes:',

                            'Niga Pangalan/Given Names', 'Niga Pangalan: Given Names', 'Niga Pangalan/Given Names.', 'Niga Pangalan: Given Names.', 'Niga Pangalan/Given Names:', 'Niga Pangalan: Given Names:',
                            'Niga Pangalan/G:ven Names', 'Niga Pangalan: G:ven Names', 'Niga Pangalan/G:ven Names.', 'Niga Pangalan: G:ven Names.', 'Niga Pangalan/G:ven Names:', 'Niga Pangalan: G:ven Names:', 
                            'Niga Pangalan/Given Nomes', 'Niga Pangalan: Given Nomes', 'Niga Pangalan/Given Nomes.', 'Niga Pangalan: Given Nomes.', 'Niga Pangalan/Given Nomes:', 'Niga Pangalan: Given Nomes:',
                            'Niga Pangalan/G:ven Nomes', 'Niga Pangalan: G:ven Nomes', 'Niga Pangalan/G:ven Nomes.', 'Niga Pangalan: G:ven Nomes.', 'Niga Pangalan/G:ven Nomes:', 'Niga Pangalan: G:ven Nomes:', 
                            'Niga Pangatan/Given Names', 'Niga Pangatan: Given Names', 'Niga Pangatan/Given Names.', 'Niga Pangatan: Given Names.', 'Niga Pangatan/Given Names:', 'Niga Pangatan: Given Names:',
                            'Niga Pangatan/G:ven Names', 'Niga Pangatan: G:ven Names', 'Niga Pangatan/G:ven Names.', 'Niga Pangatan: G:ven Names.', 'Niga Pangatan/G:ven Names:', 'Niga Pangatan: G:ven Names:', 
                            'Niga Pangatan/Given Nomes', 'Niga Pangatan: Given Nomes', 'Niga Pangatan/Given Nomes.', 'Niga Pangatan: Given Nomes.', 'Niga Pangatan/Given Nomes:', 'Niga Pangatan: Given Nomes:',
                            'Niga Pangatan/G:ven Nomes', 'Niga Pangatan: G:ven Nomes', 'Niga Pangatan/G:ven Nomes.', 'Niga Pangatan: G:ven Nomes.', 'Niga Pangatan/G:ven Nomes:', 'Niga Pangatan: G:ven Nomes:',

                            'Viga Pangalan/Given Names', 'Viga Pangalan: Given Names', 'Viga Pangalan/Given Names.', 'Viga Pangalan: Given Names.', 'Viga Pangalan/Given Names:', 'Viga Pangalan: Given Names:',
                            'Viga Pangalan/G:ven Names', 'Viga Pangalan: G:ven Names', 'Viga Pangalan/G:ven Names.', 'Viga Pangalan: G:ven Names.', 'Viga Pangalan/G:ven Names:', 'Viga Pangalan: G:ven Names:', 
                            'Viga Pangalan/Given Nomes', 'Viga Pangalan: Given Nomes', 'Viga Pangalan/Given Nomes.', 'Viga Pangalan: Given Nomes.', 'Viga Pangalan/Given Nomes:', 'Viga Pangalan: Given Nomes:',
                            'Viga Pangalan/G:ven Nomes', 'Viga Pangalan: G:ven Nomes', 'Viga Pangalan/G:ven Nomes.', 'Viga Pangalan: G:ven Nomes.', 'Viga Pangalan/G:ven Nomes:', 'Viga Pangalan: G:ven Nomes:',
                            'Viga Pangatan/Given Names', 'Viga Pangatan: Given Names', 'Viga Pangatan/Given Names.', 'Viga Pangatan: Given Names.', 'Viga Pangatan/Given Names:', 'Viga Pangatan: Given Names:',
                            'Viga Pangatan/G:ven Names', 'Viga Pangatan: G:ven Names', 'Viga Pangatan/G:ven Names.', 'Viga Pangatan: G:ven Names.', 'Viga Pangatan/G:ven Names:', 'Viga Pangatan: G:ven Names:', 
                            'Viga Pangatan/Given Nomes', 'Viga Pangatan: Given Nomes', 'Viga Pangatan/Given Nomes.', 'Viga Pangatan: Given Nomes.', 'Viga Pangatan/Given Nomes:', 'Viga Pangatan: Given Nomes:',
                            'Viga Pangatan/G:ven Nomes', 'Viga Pangatan: G:ven Nomes', 'Viga Pangatan/G:ven Nomes.', 'Viga Pangatan: G:ven Nomes.', 'Viga Pangatan/G:ven Nomes:', 'Viga Pangatan: G:ven Nomes:',
                            ]),

                ('middlename', ['Gitnang Apelyido/Middle Name', 'Gitnang Apelyido: Middle Name', 'Gitnang Apelyido/Middle Name.', 'Gitnang Apelyido: Middle Name.', 'Gitnang Apelyido/Middle Name:', 'Gitnang Apelyido: Middle Name:',
                                'G:tnang Apelyido/Middle Name', 'G:tnang Apelyido: Middle Name', 'G:tnang Apelyido/Middle Name.', 'G:tnang Apelyido: Middle Name.', 'G:tnang Apelyido/Middle Name:', 'G:tnang Apelyido: Middle Name:',
                                'Gitnang Apely:do/Middle Name', 'Gitnang Apely:do: Middle Name', 'Gitnang Apely:do/Middle Name.', 'Gitnang Apely:do: Middle Name.', 'Gitnang Apely:do/Middle Name:', 'Gitnang Apely:do: Middle Name:',
                                'Gitnang Apelyido/M:ddle Name', 'Gitnang Apelyido: M:ddle Name', 'Gitnang Apelyido/M:ddle Name.', 'Gitnang Apelyido: M:ddle Name.', 'Gitnang Apelyido/M:ddle Name:', 'Gitnang Apelyido: M:ddle Name:',
                                'G:tnang Apely:do/Middle Name', 'G:tnang Apely:do: Middle Name', 'G:tnang Apely:do/Middle Name.', 'G:tnang Apely:do: Middle Name.', 'G:tnang Apely:do/Middle Name:', 'G:tnang Apely:do: Middle Name:',
                                'Gitnang Apely:do/M:ddle Name', 'Gitnang Apely:do: M:ddle Name', 'Gitnang Apely:do/M:ddle Name.', 'Gitnang Apely:do: M:ddle Name.', 'Gitnang Apely:do/M:ddle Name:', 'Gitnang Apely:do: M:ddle Name:',
                                'Gitnang Apelyido/Middle Nome', 'Gitnang Apelyido: Middle Nome', 'Gitnang Apelyido/Middle Nome.', 'Gitnang Apelyido: Middle Nome.', 'Gitnang Apelyido/Middle Nome:', 'Gitnang Apelyido: Middle Nome:',
                                'G:tnang Apelyido/Middle Nome', 'G:tnang Apelyido: Middle Nome', 'G:tnang Apelyido/Middle Nome.', 'G:tnang Apelyido: Middle Nome.', 'G:tnang Apelyido/Middle Nome:', 'G:tnang Apelyido: Middle Nome:',
                                'Gitnang Apely:do/Middle Nome', 'Gitnang Apely:do: Middle Nome', 'Gitnang Apely:do/Middle Nome.', 'Gitnang Apely:do: Middle Nome.', 'Gitnang Apely:do/Middle Nome:', 'Gitnang Apely:do: Middle Nome:',
                                'Gitnang Apelyido/M:ddle Nome', 'Gitnang Apelyido: M:ddle Nome', 'Gitnang Apelyido/M:ddle Nome.', 'Gitnang Apelyido: M:ddle Nome.', 'Gitnang Apelyido/M:ddle Nome:', 'Gitnang Apelyido: M:ddle Nome:',
                                'G:tnang Apely:do/Middle Nome', 'G:tnang Apely:do: Middle Nome', 'G:tnang Apely:do/Middle Nome.', 'G:tnang Apely:do: Middle Nome.', 'G:tnang Apely:do/Middle Nome:', 'G:tnang Apely:do: Middle Nome:',
                                'Gitnang Apely:do/M:ddle Nome', 'Gitnang Apely:do: M:ddle Nome', 'Gitnang Apely:do/M:ddle Nome.', 'Gitnang Apely:do: M:ddle Nome.', 'Gitnang Apely:do/M:ddle Nome:', 'Gitnang Apely:do: M:ddle Nome:',

                                'Gitnang Apelyido/Middie Name', 'Gitnang Apelyido: Middie Name', 'Gitnang Apelyido/Middie Name.', 'Gitnang Apelyido: Middie Name.', 'Gitnang Apelyido/Middie Name:', 'Gitnang Apelyido: Middie Name:',
                                'Gitnang Apeiyido/Middie Name', 'Gitnang Apeiyido: Middie Name', 'Gitnang Apeiyido/Middie Name.', 'Gitnang Apeiyido: Middie Name.', 'Gitnang Apeiyido/Middie Name:', 'Gitnang Apeiyido: Middie Name:',
                                'Gitnang Apelyido/Middie Nome', 'Gitnang Apelyido: Middie Nome', 'Gitnang Apelyido/Middie Nome.', 'Gitnang Apelyido: Middie Nome.', 'Gitnang Apelyido/Middie Nome:', 'Gitnang Apelyido: Middie Nome:',
                                'Gitnang Apeiyido/Middie Nome', 'Gitnang Apeiyido: Middie Nome', 'Gitnang Apeiyido/Middie Nome.', 'Gitnang Apeiyido: Middie Nome.', 'Gitnang Apeiyido/Middie Nome:', 'Gitnang Apeiyido: Middie Nome:',
                                'Gilnang Apelyido/Middie Name', 'Gilnang Apelyido: Middie Name', 'Gilnang Apelyido/Middie Name.', 'Gilnang Apelyido: Middie Name.', 'Gilnang Apelyido/Middie Name:', 'Gilnang Apelyido: Middie Name:',
                                'Gilnang Apeiyido/Middie Name', 'Gilnang Apeiyido: Middie Name', 'Gilnang Apeiyido/Middie Name.', 'Gilnang Apeiyido: Middie Name.', 'Gilnang Apeiyido/Middie Name:', 'Gilnang Apeiyido: Middie Name:',
                                'Gilnang Apelyido/Middie Nome', 'Gilnang Apelyido: Middie Nome', 'Gilnang Apelyido/Middie Nome.', 'Gilnang Apelyido: Middie Nome.', 'Gilnang Apelyido/Middie Nome:', 'Gilnang Apelyido: Middie Nome:',
                                'Gilnang Apeiyido/Middie Nome', 'Gilnang Apeiyido: Middie Nome', 'Gilnang Apeiyido/Middie Nome.', 'Gilnang Apeiyido: Middie Nome.', 'Gilnang Apeiyido/Middie Nome:', 'Gilnang Apeiyido: Middie Nome:',
                                'G:tnang Apelyido/Middie Name', 'G:tnang Apelyido: Middie Name', 'G:tnang Apelyido/Middie Name.', 'G:tnang Apelyido: Middie Name.', 'G:tnang Apelyido/Middie Name:', 'G:tnang Apelyido: Middie Name:',
                                'G:tnang Apeiyido/Middie Name', 'G:tnang Apeiyido: Middie Name', 'G:tnang Apeiyido/Middie Name.', 'G:tnang Apeiyido: Middie Name.', 'G:tnang Apeiyido/Middie Name:', 'G:tnang Apeiyido: Middie Name:',
                                'G:tnang Apelyido/Middie Nome', 'G:tnang Apelyido: Middie Nome', 'G:tnang Apelyido/Middie Nome.', 'G:tnang Apelyido: Middie Nome.', 'G:tnang Apelyido/Middie Nome:', 'G:tnang Apelyido: Middie Nome:',
                                'G:tnang Apeiyido/Middie Nome', 'G:tnang Apeiyido: Middie Nome', 'G:tnang Apeiyido/Middie Nome.', 'G:tnang Apeiyido: Middie Nome.', 'G:tnang Apeiyido/Middie Nome:', 'G:tnang Apeiyido: Middie Nome:',
                                'G:lnang Apelyido/Middie Name', 'G:lnang Apelyido: Middie Name', 'G:lnang Apelyido/Middie Name.', 'G:lnang Apelyido: Middie Name.', 'G:lnang Apelyido/Middie Name:', 'G:lnang Apelyido: Middie Name:',
                                'G:lnang Apeiyido/Middie Name', 'G:lnang Apeiyido: Middie Name', 'G:lnang Apeiyido/Middie Name.', 'G:lnang Apeiyido: Middie Name.', 'G:lnang Apeiyido/Middie Name:', 'G:lnang Apeiyido: Middie Name:',
                                'G:lnang Apelyido/Middie Nome', 'G:lnang Apelyido: Middie Nome', 'G:lnang Apelyido/Middie Nome.', 'G:lnang Apelyido: Middie Nome.', 'G:lnang Apelyido/Middie Nome:', 'G:lnang Apelyido: Middie Nome:',
                                'G:lnang Apeiyido/Middie Nome', 'G:lnang Apeiyido: Middie Nome', 'G:lnang Apeiyido/Middie Nome.', 'G:lnang Apeiyido: Middie Nome.', 'G:lnang Apeiyido/Middie Nome:', 'G:lnang Apeiyido: Middie Nome:',
                                'G:tnang Apely:do/Middie Name', 'G:tnang Apely:do: Middie Name', 'G:tnang Apely:do/Middie Name.', 'G:tnang Apely:do: Middie Name.', 'G:tnang Apely:do/Middie Name:', 'G:tnang Apely:do: Middie Name:',
                                'G:tnang Apeiy:do/Middie Name', 'G:tnang Apeiy:do: Middie Name', 'G:tnang Apeiy:do/Middie Name.', 'G:tnang Apeiy:do: Middie Name.', 'G:tnang Apeiy:do/Middie Name:', 'G:tnang Apeiy:do: Middie Name:',
                                'G:tnang Apely:do/Middie Nome', 'G:tnang Apely:do: Middie Nome', 'G:tnang Apely:do/Middie Nome.', 'G:tnang Apely:do: Middie Nome.', 'G:tnang Apely:do/Middie Nome:', 'G:tnang Apely:do: Middie Nome:',
                                'G:tnang Apeiy:do/Middie Nome', 'G:tnang Apeiy:do: Middie Nome', 'G:tnang Apeiy:do/Middie Nome.', 'G:tnang Apeiy:do: Middie Nome.', 'G:tnang Apeiy:do/Middie Nome:', 'G:tnang Apeiy:do: Middie Nome:',
                                'G:lnang Apely:do/Middie Name', 'G:lnang Apely:do: Middie Name', 'G:lnang Apely:do/Middie Name.', 'G:lnang Apely:do: Middie Name.', 'G:lnang Apely:do/Middie Name:', 'G:lnang Apely:do: Middie Name:',
                                'G:lnang Apeiy:do/Middie Name', 'G:lnang Apeiy:do: Middie Name', 'G:lnang Apeiy:do/Middie Name.', 'G:lnang Apeiy:do: Middie Name.', 'G:lnang Apeiy:do/Middie Name:', 'G:lnang Apeiy:do: Middie Name:',
                                'G:lnang Apely:do/Middie Nome', 'G:lnang Apely:do: Middie Nome', 'G:lnang Apely:do/Middie Nome.', 'G:lnang Apely:do: Middie Nome.', 'G:lnang Apely:do/Middie Nome:', 'G:lnang Apely:do: Middie Nome:',
                                'G:lnang Apeiy:do/Middie Nome', 'G:lnang Apeiy:do: Middie Nome', 'G:lnang Apeiy:do/Middie Nome.', 'G:lnang Apeiy:do: Middie Nome.', 'G:lnang Apeiy:do/Middie Nome:', 'G:lnang Apeiy:do: Middie Nome:',
                                
                                'Gitnang Apelyrdo/Middie Name', 'Gitnang Apelyrdo: Middie Name', 'Gitnang Apelyrdo/Middie Name.', 'Gitnang Apelyrdo: Middie Name.', 'Gitnang Apelyrdo/Middie Name:', 'Gitnang Apelyrdo: Middie Name:', 
                                'Gitnang Apeiyrdo/Middie Name', 'Gitnang Apeiyrdo: Middie Name', 'Gitnang Apeiyrdo/Middie Name.', 'Gitnang Apeiyrdo: Middie Name.', 'Gitnang Apeiyrdo/Middie Name:', 'Gitnang Apeiyrdo: Middie Name:', 
                                'Gitnang Apelyrdo/Middie Nome', 'Gitnang Apelyrdo: Middie Nome', 'Gitnang Apelyrdo/Middie Nome.', 'Gitnang Apelyrdo: Middie Nome.', 'Gitnang Apelyrdo/Middie Nome:', 'Gitnang Apelyrdo: Middie Nome:', 
                                'Gitnang Apeiyrdo/Middie Nome', 'Gitnang Apeiyrdo: Middie Nome', 'Gitnang Apeiyrdo/Middie Nome.', 'Gitnang Apeiyrdo: Middie Nome.', 'Gitnang Apeiyrdo/Middie Nome:', 'Gitnang Apeiyrdo: Middie Nome:', 
                                'Gilnang Apelyrdo/Middie Name', 'Gilnang Apelyrdo: Middie Name', 'Gilnang Apelyrdo/Middie Name.', 'Gilnang Apelyrdo: Middie Name.', 'Gilnang Apelyrdo/Middie Name:', 'Gilnang Apelyrdo: Middie Name:', 
                                'Gilnang Apeiyrdo/Middie Name', 'Gilnang Apeiyrdo: Middie Name', 'Gilnang Apeiyrdo/Middie Name.', 'Gilnang Apeiyrdo: Middie Name.', 'Gilnang Apeiyrdo/Middie Name:', 'Gilnang Apeiyrdo: Middie Name:', 
                                'Gilnang Apelyrdo/Middie Nome', 'Gilnang Apelyrdo: Middie Nome', 'Gilnang Apelyrdo/Middie Nome.', 'Gilnang Apelyrdo: Middie Nome.', 'Gilnang Apelyrdo/Middie Nome:', 'Gilnang Apelyrdo: Middie Nome:', 
                                'Gilnang Apeiyrdo/Middie Nome', 'Gilnang Apeiyrdo: Middie Nome', 'Gilnang Apeiyrdo/Middie Nome.', 'Gilnang Apeiyrdo: Middie Nome.', 'Gilnang Apeiyrdo/Middie Nome:', 'Gilnang Apeiyrdo: Middie Nome:', 

                                'Gitnang Apelyido/Midalie Name', 'Gitnang Apelyido: Midalie Name', 'Gitnang Apelyido/Midalie Name.', 'Gitnang Apelyido: Midalie Name.', 'Gitnang Apelyido/Midalie Name:', 'Gitnang Apelyido: Midalie Name:',
                                'Gitnang Apeiyido/Midalie Name', 'Gitnang Apeiyido: Midalie Name', 'Gitnang Apeiyido/Midalie Name.', 'Gitnang Apeiyido: Midalie Name.', 'Gitnang Apeiyido/Midalie Name:', 'Gitnang Apeiyido: Midalie Name:',
                                'Gitnang Apelyido/Midalie Nome', 'Gitnang Apelyido: Midalie Nome', 'Gitnang Apelyido/Midalie Nome.', 'Gitnang Apelyido: Midalie Nome.', 'Gitnang Apelyido/Midalie Nome:', 'Gitnang Apelyido: Midalie Nome:',
                                'Gitnang Apeiyido/Midalie Nome', 'Gitnang Apeiyido: Midalie Nome', 'Gitnang Apeiyido/Midalie Nome.', 'Gitnang Apeiyido: Midalie Nome.', 'Gitnang Apeiyido/Midalie Nome:', 'Gitnang Apeiyido: Midalie Nome:',
                                'Gilnang Apelyido/Midalie Name', 'Gilnang Apelyido: Midalie Name', 'Gilnang Apelyido/Midalie Name.', 'Gilnang Apelyido: Midalie Name.', 'Gilnang Apelyido/Midalie Name:', 'Gilnang Apelyido: Midalie Name:',
                                'Gilnang Apeiyido/Midalie Name', 'Gilnang Apeiyido: Midalie Name', 'Gilnang Apeiyido/Midalie Name.', 'Gilnang Apeiyido: Midalie Name.', 'Gilnang Apeiyido/Midalie Name:', 'Gilnang Apeiyido: Midalie Name:',
                                'Gilnang Apelyido/Midalie Nome', 'Gilnang Apelyido: Midalie Nome', 'Gilnang Apelyido/Midalie Nome.', 'Gilnang Apelyido: Midalie Nome.', 'Gilnang Apelyido/Midalie Nome:', 'Gilnang Apelyido: Midalie Nome:',
                                'Gilnang Apeiyido/Midalie Nome', 'Gilnang Apeiyido: Midalie Nome', 'Gilnang Apeiyido/Midalie Nome.', 'Gilnang Apeiyido: Midalie Nome.', 'Gilnang Apeiyido/Midalie Nome:', 'Gilnang Apeiyido: Midalie Nome:',
                                'Gitnang Apetyido/Midalie Name', 'Gitnang Apetyido: Midalie Name', 'Gitnang Apetyido/Midalie Name.', 'Gitnang Apetyido: Midalie Name.', 'Gitnang Apetyido/Midalie Name:', 'Gitnang Apetyido: Midalie Name:',
                                'Gitnang Apetyido/Midalie Nome', 'Gitnang Apetyido: Midalie Nome', 'Gitnang Apetyido/Midalie Nome.', 'Gitnang Apetyido: Midalie Nome.', 'Gitnang Apetyido/Midalie Nome:', 'Gitnang Apetyido: Midalie Nome:',
                                'Gilnang Apetyido/Midalie Name', 'Gilnang Apetyido: Midalie Name', 'Gilnang Apetyido/Midalie Name.', 'Gilnang Apetyido: Midalie Name.', 'Gilnang Apetyido/Midalie Name:', 'Gilnang Apetyido: Midalie Name:',
                                'Gilnang Apetyido/Midalie Nome', 'Gilnang Apetyido: Midalie Nome', 'Gilnang Apetyido/Midalie Nome.', 'Gilnang Apetyido: Midalie Nome.', 'Gilnang Apetyido/Midalie Nome:', 'Gilnang Apetyido: Midalie Nome:',

                                'Gitnang Apelyido/Midale Name', 'Gitnang Apelyido: Midale Name', 'Gitnang Apelyido/Midale Name.', 'Gitnang Apelyido: Midale Name.', 'Gitnang Apelyido/Midale Name:', 'Gitnang Apelyido: Midale Name:',
                                'Gitnang Apeiyido/Midale Name', 'Gitnang Apeiyido: Midale Name', 'Gitnang Apeiyido/Midale Name.', 'Gitnang Apeiyido: Midale Name.', 'Gitnang Apeiyido/Midale Name:', 'Gitnang Apeiyido: Midale Name:',
                                'Gitnang Apetyido/Midale Name', 'Gitnang Apetyido: Midale Name', 'Gitnang Apetyido/Midale Name.', 'Gitnang Apetyido: Midale Name.', 'Gitnang Apetyido/Midale Name:', 'Gitnang Apetyido: Midale Name:',
                                'Gitnang Apelyido/Midale Nome', 'Gitnang Apelyido: Midale Nome', 'Gitnang Apelyido/Midale Nome.', 'Gitnang Apelyido: Midale Nome.', 'Gitnang Apelyido/Midale Nome:', 'Gitnang Apelyido: Midale Nome:',
                                'Gitnang Apeiyido/Midale Nome', 'Gitnang Apeiyido: Midale Nome', 'Gitnang Apeiyido/Midale Nome.', 'Gitnang Apeiyido: Midale Nome.', 'Gitnang Apeiyido/Midale Nome:', 'Gitnang Apeiyido: Midale Nome:',
                                'Gitnang Apetyido/Midale Nome', 'Gitnang Apetyido: Midale Nome', 'Gitnang Apetyido/Midale Nome.', 'Gitnang Apetyido: Midale Nome.', 'Gitnang Apetyido/Midale Nome:', 'Gitnang Apetyido: Midale Nome:', 
                                'Gilnang Apelyido/Midale Name', 'Gilnang Apelyido: Midale Name', 'Gilnang Apelyido/Midale Name.', 'Gilnang Apelyido: Midale Name.', 'Gilnang Apelyido/Midale Name:', 'Gilnang Apelyido: Midale Name:',
                                'Gilnang Apeiyido/Midale Name', 'Gilnang Apeiyido: Midale Name', 'Gilnang Apeiyido/Midale Name.', 'Gilnang Apeiyido: Midale Name.', 'Gilnang Apeiyido/Midale Name:', 'Gilnang Apeiyido: Midale Name:',
                                'Gilnang Apetyido/Midale Name', 'Gilnang Apetyido: Midale Name', 'Gilnang Apetyido/Midale Name.', 'Gilnang Apetyido: Midale Name.', 'Gilnang Apetyido/Midale Name:', 'Gilnang Apetyido: Midale Name:',
                                'Gilnang Apelyido/Midale Nome', 'Gilnang Apelyido: Midale Nome', 'Gilnang Apelyido/Midale Nome.', 'Gilnang Apelyido: Midale Nome.', 'Gilnang Apelyido/Midale Nome:', 'Gilnang Apelyido: Midale Nome:',
                                'Gilnang Apeiyido/Midale Nome', 'Gilnang Apeiyido: Midale Nome', 'Gilnang Apeiyido/Midale Nome.', 'Gilnang Apeiyido: Midale Nome.', 'Gilnang Apeiyido/Midale Nome:', 'Gilnang Apeiyido: Midale Nome:',
                                'Gilnang Apetyido/Midale Nome', 'Gilnang Apetyido: Midale Nome', 'Gilnang Apetyido/Midale Nome.', 'Gilnang Apetyido: Midale Nome.', 'Gilnang Apetyido/Midale Nome:', 'Gilnang Apetyido: Midale Nome:',

                                'aitnang Apelyido/Middle Name', 'aitnang Apelyido: Middle Name', 'aitnang Apelyido/Middle Name.', 'aitnang Apelyido: Middle Name.', 'aitnang Apelyido/Middle Name:', 'aitnang Apelyido: Middle Name:',
                                'a:tnang Apelyido/Middle Name', 'a:tnang Apelyido: Middle Name', 'a:tnang Apelyido/Middle Name.', 'a:tnang Apelyido: Middle Name.', 'a:tnang Apelyido/Middle Name:', 'a:tnang Apelyido: Middle Name:',
                                'aitnang Apely:do/Middle Name', 'aitnang Apely:do: Middle Name', 'aitnang Apely:do/Middle Name.', 'aitnang Apely:do: Middle Name.', 'aitnang Apely:do/Middle Name:', 'aitnang Apely:do: Middle Name:',
                                'aitnang Apelyido/M:ddle Name', 'aitnang Apelyido: M:ddle Name', 'aitnang Apelyido/M:ddle Name.', 'aitnang Apelyido: M:ddle Name.', 'aitnang Apelyido/M:ddle Name:', 'aitnang Apelyido: M:ddle Name:',
                                'a:tnang Apely:do/Middle Name', 'a:tnang Apely:do: Middle Name', 'a:tnang Apely:do/Middle Name.', 'a:tnang Apely:do: Middle Name.', 'a:tnang Apely:do/Middle Name:', 'a:tnang Apely:do: Middle Name:',
                                'aitnang Apely:do/M:ddle Name', 'aitnang Apely:do: M:ddle Name', 'aitnang Apely:do/M:ddle Name.', 'aitnang Apely:do: M:ddle Name.', 'aitnang Apely:do/M:ddle Name:', 'aitnang Apely:do: M:ddle Name:',
                                'aitnang Apelyido/Middle Nome', 'aitnang Apelyido: Middle Nome', 'aitnang Apelyido/Middle Nome.', 'aitnang Apelyido: Middle Nome.', 'aitnang Apelyido/Middle Nome:', 'aitnang Apelyido: Middle Nome:',
                                'a:tnang Apelyido/Middle Nome', 'a:tnang Apelyido: Middle Nome', 'a:tnang Apelyido/Middle Nome.', 'a:tnang Apelyido: Middle Nome.', 'a:tnang Apelyido/Middle Nome:', 'a:tnang Apelyido: Middle Nome:',
                                'aitnang Apely:do/Middle Nome', 'aitnang Apely:do: Middle Nome', 'aitnang Apely:do/Middle Nome.', 'aitnang Apely:do: Middle Nome.', 'aitnang Apely:do/Middle Nome:', 'aitnang Apely:do: Middle Nome:',
                                'aitnang Apelyido/M:ddle Nome', 'aitnang Apelyido: M:ddle Nome', 'aitnang Apelyido/M:ddle Nome.', 'aitnang Apelyido: M:ddle Nome.', 'aitnang Apelyido/M:ddle Nome:', 'aitnang Apelyido: M:ddle Nome:',
                                'a:tnang Apely:do/Middle Nome', 'a:tnang Apely:do: Middle Nome', 'a:tnang Apely:do/Middle Nome.', 'a:tnang Apely:do: Middle Nome.', 'a:tnang Apely:do/Middle Nome:', 'a:tnang Apely:do: Middle Nome:',
                                'aitnang Apely:do/M:ddle Nome', 'aitnang Apely:do: M:ddle Nome', 'aitnang Apely:do/M:ddle Nome.', 'aitnang Apely:do: M:ddle Nome.', 'aitnang Apely:do/M:ddle Nome:', 'aitnang Apely:do: M:ddle Nome:',

                                'aitnang Apelyido/Middie Name', 'aitnang Apelyido: Middie Name', 'aitnang Apelyido/Middie Name.', 'aitnang Apelyido: Middie Name.', 'aitnang Apelyido/Middie Name:', 'aitnang Apelyido: Middie Name:',
                                'aitnang Apeiyido/Middie Name', 'aitnang Apeiyido: Middie Name', 'aitnang Apeiyido/Middie Name.', 'aitnang Apeiyido: Middie Name.', 'aitnang Apeiyido/Middie Name:', 'aitnang Apeiyido: Middie Name:',
                                'aitnang Apelyido/Middie Nome', 'aitnang Apelyido: Middie Nome', 'aitnang Apelyido/Middie Nome.', 'aitnang Apelyido: Middie Nome.', 'aitnang Apelyido/Middie Nome:', 'aitnang Apelyido: Middie Nome:',
                                'aitnang Apeiyido/Middie Nome', 'aitnang Apeiyido: Middie Nome', 'aitnang Apeiyido/Middie Nome.', 'aitnang Apeiyido: Middie Nome.', 'aitnang Apeiyido/Middie Nome:', 'aitnang Apeiyido: Middie Nome:',
                                'ailnang Apelyido/Middie Name', 'ailnang Apelyido: Middie Name', 'ailnang Apelyido/Middie Name.', 'ailnang Apelyido: Middie Name.', 'ailnang Apelyido/Middie Name:', 'ailnang Apelyido: Middie Name:',
                                'ailnang Apeiyido/Middie Name', 'ailnang Apeiyido: Middie Name', 'ailnang Apeiyido/Middie Name.', 'ailnang Apeiyido: Middie Name.', 'ailnang Apeiyido/Middie Name:', 'ailnang Apeiyido: Middie Name:',
                                'ailnang Apelyido/Middie Nome', 'ailnang Apelyido: Middie Nome', 'ailnang Apelyido/Middie Nome.', 'ailnang Apelyido: Middie Nome.', 'ailnang Apelyido/Middie Nome:', 'ailnang Apelyido: Middie Nome:',
                                'ailnang Apeiyido/Middie Nome', 'ailnang Apeiyido: Middie Nome', 'ailnang Apeiyido/Middie Nome.', 'ailnang Apeiyido: Middie Nome.', 'ailnang Apeiyido/Middie Nome:', 'ailnang Apeiyido: Middie Nome:',
                                'a:tnang Apelyido/Middie Name', 'a:tnang Apelyido: Middie Name', 'a:tnang Apelyido/Middie Name.', 'a:tnang Apelyido: Middie Name.', 'a:tnang Apelyido/Middie Name:', 'a:tnang Apelyido: Middie Name:',
                                'a:tnang Apeiyido/Middie Name', 'a:tnang Apeiyido: Middie Name', 'a:tnang Apeiyido/Middie Name.', 'a:tnang Apeiyido: Middie Name.', 'a:tnang Apeiyido/Middie Name:', 'a:tnang Apeiyido: Middie Name:',
                                'a:tnang Apelyido/Middie Nome', 'a:tnang Apelyido: Middie Nome', 'a:tnang Apelyido/Middie Nome.', 'a:tnang Apelyido: Middie Nome.', 'a:tnang Apelyido/Middie Nome:', 'a:tnang Apelyido: Middie Nome:',
                                'a:tnang Apeiyido/Middie Nome', 'a:tnang Apeiyido: Middie Nome', 'a:tnang Apeiyido/Middie Nome.', 'a:tnang Apeiyido: Middie Nome.', 'a:tnang Apeiyido/Middie Nome:', 'a:tnang Apeiyido: Middie Nome:',
                                'a:lnang Apelyido/Middie Name', 'a:lnang Apelyido: Middie Name', 'a:lnang Apelyido/Middie Name.', 'a:lnang Apelyido: Middie Name.', 'a:lnang Apelyido/Middie Name:', 'a:lnang Apelyido: Middie Name:',
                                'a:lnang Apeiyido/Middie Name', 'a:lnang Apeiyido: Middie Name', 'a:lnang Apeiyido/Middie Name.', 'a:lnang Apeiyido: Middie Name.', 'a:lnang Apeiyido/Middie Name:', 'a:lnang Apeiyido: Middie Name:',
                                'a:lnang Apelyido/Middie Nome', 'a:lnang Apelyido: Middie Nome', 'a:lnang Apelyido/Middie Nome.', 'a:lnang Apelyido: Middie Nome.', 'a:lnang Apelyido/Middie Nome:', 'a:lnang Apelyido: Middie Nome:',
                                'a:lnang Apeiyido/Middie Nome', 'a:lnang Apeiyido: Middie Nome', 'a:lnang Apeiyido/Middie Nome.', 'a:lnang Apeiyido: Middie Nome.', 'a:lnang Apeiyido/Middie Nome:', 'a:lnang Apeiyido: Middie Nome:',
                                'a:tnang Apely:do/Middie Name', 'a:tnang Apely:do: Middie Name', 'a:tnang Apely:do/Middie Name.', 'a:tnang Apely:do: Middie Name.', 'a:tnang Apely:do/Middie Name:', 'a:tnang Apely:do: Middie Name:',
                                'a:tnang Apeiy:do/Middie Name', 'a:tnang Apeiy:do: Middie Name', 'a:tnang Apeiy:do/Middie Name.', 'a:tnang Apeiy:do: Middie Name.', 'a:tnang Apeiy:do/Middie Name:', 'a:tnang Apeiy:do: Middie Name:',
                                'a:tnang Apely:do/Middie Nome', 'a:tnang Apely:do: Middie Nome', 'a:tnang Apely:do/Middie Nome.', 'a:tnang Apely:do: Middie Nome.', 'a:tnang Apely:do/Middie Nome:', 'a:tnang Apely:do: Middie Nome:',
                                'a:tnang Apeiy:do/Middie Nome', 'a:tnang Apeiy:do: Middie Nome', 'a:tnang Apeiy:do/Middie Nome.', 'a:tnang Apeiy:do: Middie Nome.', 'a:tnang Apeiy:do/Middie Nome:', 'a:tnang Apeiy:do: Middie Nome:',
                                'a:lnang Apely:do/Middie Name', 'a:lnang Apely:do: Middie Name', 'a:lnang Apely:do/Middie Name.', 'a:lnang Apely:do: Middie Name.', 'a:lnang Apely:do/Middie Name:', 'a:lnang Apely:do: Middie Name:',
                                'a:lnang Apeiy:do/Middie Name', 'a:lnang Apeiy:do: Middie Name', 'a:lnang Apeiy:do/Middie Name.', 'a:lnang Apeiy:do: Middie Name.', 'a:lnang Apeiy:do/Middie Name:', 'a:lnang Apeiy:do: Middie Name:',
                                'a:lnang Apely:do/Middie Nome', 'a:lnang Apely:do: Middie Nome', 'a:lnang Apely:do/Middie Nome.', 'a:lnang Apely:do: Middie Nome.', 'a:lnang Apely:do/Middie Nome:', 'a:lnang Apely:do: Middie Nome:',
                                'a:lnang Apeiy:do/Middie Nome', 'a:lnang Apeiy:do: Middie Nome', 'a:lnang Apeiy:do/Middie Nome.', 'a:lnang Apeiy:do: Middie Nome.', 'a:lnang Apeiy:do/Middie Nome:', 'a:lnang Apeiy:do: Middie Nome:',
                                
                                'aitnang Apelyrdo/Middie Name', 'aitnang Apelyrdo: Middie Name', 'aitnang Apelyrdo/Middie Name.', 'aitnang Apelyrdo: Middie Name.', 'aitnang Apelyrdo/Middie Name:', 'aitnang Apelyrdo: Middie Name:', 
                                'aitnang Apeiyrdo/Middie Name', 'aitnang Apeiyrdo: Middie Name', 'aitnang Apeiyrdo/Middie Name.', 'aitnang Apeiyrdo: Middie Name.', 'aitnang Apeiyrdo/Middie Name:', 'aitnang Apeiyrdo: Middie Name:', 
                                'aitnang Apelyrdo/Middie Nome', 'aitnang Apelyrdo: Middie Nome', 'aitnang Apelyrdo/Middie Nome.', 'aitnang Apelyrdo: Middie Nome.', 'aitnang Apelyrdo/Middie Nome:', 'aitnang Apelyrdo: Middie Nome:', 
                                'aitnang Apeiyrdo/Middie Nome', 'aitnang Apeiyrdo: Middie Nome', 'aitnang Apeiyrdo/Middie Nome.', 'aitnang Apeiyrdo: Middie Nome.', 'aitnang Apeiyrdo/Middie Nome:', 'aitnang Apeiyrdo: Middie Nome:', 
                                'ailnang Apelyrdo/Middie Name', 'ailnang Apelyrdo: Middie Name', 'ailnang Apelyrdo/Middie Name.', 'ailnang Apelyrdo: Middie Name.', 'ailnang Apelyrdo/Middie Name:', 'ailnang Apelyrdo: Middie Name:', 
                                'ailnang Apeiyrdo/Middie Name', 'ailnang Apeiyrdo: Middie Name', 'ailnang Apeiyrdo/Middie Name.', 'ailnang Apeiyrdo: Middie Name.', 'ailnang Apeiyrdo/Middie Name:', 'ailnang Apeiyrdo: Middie Name:', 
                                'ailnang Apelyrdo/Middie Nome', 'ailnang Apelyrdo: Middie Nome', 'ailnang Apelyrdo/Middie Nome.', 'ailnang Apelyrdo: Middie Nome.', 'ailnang Apelyrdo/Middie Nome:', 'ailnang Apelyrdo: Middie Nome:', 
                                'ailnang Apeiyrdo/Middie Nome', 'ailnang Apeiyrdo: Middie Nome', 'ailnang Apeiyrdo/Middie Nome.', 'ailnang Apeiyrdo: Middie Nome.', 'ailnang Apeiyrdo/Middie Nome:', 'ailnang Apeiyrdo: Middie Nome:', 

                                'aitnang Apelyido/Midalie Name', 'aitnang Apelyido: Midalie Name', 'aitnang Apelyido/Midalie Name.', 'aitnang Apelyido: Midalie Name.', 'aitnang Apelyido/Midalie Name:', 'aitnang Apelyido: Midalie Name:',
                                'aitnang Apeiyido/Midalie Name', 'aitnang Apeiyido: Midalie Name', 'aitnang Apeiyido/Midalie Name.', 'aitnang Apeiyido: Midalie Name.', 'aitnang Apeiyido/Midalie Name:', 'aitnang Apeiyido: Midalie Name:',
                                'aitnang Apelyido/Midalie Nome', 'aitnang Apelyido: Midalie Nome', 'aitnang Apelyido/Midalie Nome.', 'aitnang Apelyido: Midalie Nome.', 'aitnang Apelyido/Midalie Nome:', 'aitnang Apelyido: Midalie Nome:',
                                'aitnang Apeiyido/Midalie Nome', 'aitnang Apeiyido: Midalie Nome', 'aitnang Apeiyido/Midalie Nome.', 'aitnang Apeiyido: Midalie Nome.', 'aitnang Apeiyido/Midalie Nome:', 'aitnang Apeiyido: Midalie Nome:',
                                'ailnang Apelyido/Midalie Name', 'ailnang Apelyido: Midalie Name', 'ailnang Apelyido/Midalie Name.', 'ailnang Apelyido: Midalie Name.', 'ailnang Apelyido/Midalie Name:', 'ailnang Apelyido: Midalie Name:',
                                'ailnang Apeiyido/Midalie Name', 'ailnang Apeiyido: Midalie Name', 'ailnang Apeiyido/Midalie Name.', 'ailnang Apeiyido: Midalie Name.', 'ailnang Apeiyido/Midalie Name:', 'ailnang Apeiyido: Midalie Name:',
                                'ailnang Apelyido/Midalie Nome', 'ailnang Apelyido: Midalie Nome', 'ailnang Apelyido/Midalie Nome.', 'ailnang Apelyido: Midalie Nome.', 'ailnang Apelyido/Midalie Nome:', 'ailnang Apelyido: Midalie Nome:',
                                'ailnang Apeiyido/Midalie Nome', 'ailnang Apeiyido: Midalie Nome', 'ailnang Apeiyido/Midalie Nome.', 'ailnang Apeiyido: Midalie Nome.', 'ailnang Apeiyido/Midalie Nome:', 'ailnang Apeiyido: Midalie Nome:',
                                'aitnang Apetyido/Midalie Name', 'aitnang Apetyido: Midalie Name', 'aitnang Apetyido/Midalie Name.', 'aitnang Apetyido: Midalie Name.', 'aitnang Apetyido/Midalie Name:', 'aitnang Apetyido: Midalie Name:',
                                'aitnang Apetyido/Midalie Nome', 'aitnang Apetyido: Midalie Nome', 'aitnang Apetyido/Midalie Nome.', 'aitnang Apetyido: Midalie Nome.', 'aitnang Apetyido/Midalie Nome:', 'aitnang Apetyido: Midalie Nome:',
                                'ailnang Apetyido/Midalie Name', 'ailnang Apetyido: Midalie Name', 'ailnang Apetyido/Midalie Name.', 'ailnang Apetyido: Midalie Name.', 'ailnang Apetyido/Midalie Name:', 'ailnang Apetyido: Midalie Name:',
                                'ailnang Apetyido/Midalie Nome', 'ailnang Apetyido: Midalie Nome', 'ailnang Apetyido/Midalie Nome.', 'ailnang Apetyido: Midalie Nome.', 'ailnang Apetyido/Midalie Nome:', 'ailnang Apetyido: Midalie Nome:',

                                'aitnang Apelyido/Midale Name', 'aitnang Apelyido: Midale Name', 'aitnang Apelyido/Midale Name.', 'aitnang Apelyido: Midale Name.', 'aitnang Apelyido/Midale Name:', 'aitnang Apelyido: Midale Name:',
                                'aitnang Apeiyido/Midale Name', 'aitnang Apeiyido: Midale Name', 'aitnang Apeiyido/Midale Name.', 'aitnang Apeiyido: Midale Name.', 'aitnang Apeiyido/Midale Name:', 'aitnang Apeiyido: Midale Name:',
                                'aitnang Apetyido/Midale Name', 'aitnang Apetyido: Midale Name', 'aitnang Apetyido/Midale Name.', 'aitnang Apetyido: Midale Name.', 'aitnang Apetyido/Midale Name:', 'aitnang Apetyido: Midale Name:',
                                'aitnang Apelyido/Midale Nome', 'aitnang Apelyido: Midale Nome', 'aitnang Apelyido/Midale Nome.', 'aitnang Apelyido: Midale Nome.', 'aitnang Apelyido/Midale Nome:', 'aitnang Apelyido: Midale Nome:',
                                'aitnang Apeiyido/Midale Nome', 'aitnang Apeiyido: Midale Nome', 'aitnang Apeiyido/Midale Nome.', 'aitnang Apeiyido: Midale Nome.', 'aitnang Apeiyido/Midale Nome:', 'aitnang Apeiyido: Midale Nome:',
                                'aitnang Apetyido/Midale Nome', 'aitnang Apetyido: Midale Nome', 'aitnang Apetyido/Midale Nome.', 'aitnang Apetyido: Midale Nome.', 'aitnang Apetyido/Midale Nome:', 'aitnang Apetyido: Midale Nome:', 
                                'ailnang Apelyido/Midale Name', 'ailnang Apelyido: Midale Name', 'ailnang Apelyido/Midale Name.', 'ailnang Apelyido: Midale Name.', 'ailnang Apelyido/Midale Name:', 'ailnang Apelyido: Midale Name:',
                                'ailnang Apeiyido/Midale Name', 'ailnang Apeiyido: Midale Name', 'ailnang Apeiyido/Midale Name.', 'ailnang Apeiyido: Midale Name.', 'ailnang Apeiyido/Midale Name:', 'ailnang Apeiyido: Midale Name:',
                                'ailnang Apetyido/Midale Name', 'ailnang Apetyido: Midale Name', 'ailnang Apetyido/Midale Name.', 'ailnang Apetyido: Midale Name.', 'ailnang Apetyido/Midale Name:', 'ailnang Apetyido: Midale Name:',
                                'ailnang Apelyido/Midale Nome', 'ailnang Apelyido: Midale Nome', 'ailnang Apelyido/Midale Nome.', 'ailnang Apelyido: Midale Nome.', 'ailnang Apelyido/Midale Nome:', 'ailnang Apelyido: Midale Nome:',
                                'ailnang Apeiyido/Midale Nome', 'ailnang Apeiyido: Midale Nome', 'ailnang Apeiyido/Midale Nome.', 'ailnang Apeiyido: Midale Nome.', 'ailnang Apeiyido/Midale Nome:', 'ailnang Apeiyido: Midale Nome:',
                                'ailnang Apetyido/Midale Nome', 'ailnang Apetyido: Midale Nome', 'ailnang Apetyido/Midale Nome.', 'ailnang Apetyido: Midale Nome.', 'ailnang Apetyido/Midale Nome:', 'ailnang Apetyido: Midale Nome:',
                            ]),
            ]

            # Iterate through the field patterns and their associated patterns
            for field_name, patterns in field_patterns:
                for pattern in patterns:
                    match = re.search(f"{pattern}\s+{generic_pattern}", image_to_text, flags=re.DOTALL)
                    if match:
                        extracted_info[field_name] = match.group(1).strip()
                        break
            print(f"Image Processing Extracted Info: {extracted_info}")

            img = None

            return extracted_info

        else:
            logging.error(f'Failed to read image')
            return None
    else:
        logging.error('national_id is not a File object')
        return None


def extract_applicant_voters(voter_certificate_content, voter_certificate_name):
    if voter_certificate_name:
        logging.debug(f'voter_certificate name: {voter_certificate_name}')
        
    if voter_certificate_content:
        nparr = np.fromstring(voter_certificate_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 

        if img is not None:
            #============================================================================
            # Rescaling Image
            desired_dpi = 300

            original_width, original_height = img.shape[1], img.shape[0]
            new_width = int(original_width * (desired_dpi / 72.0))                                  # 72 DPI is the default DPI for most images
            new_height = int(original_height * (desired_dpi / 72.0))

            resized_image = cv2.resize(img, (new_width, new_height))
            #============================================================================

            #============================================================================
            # Add borders to the image
            def add_border(image):
                return cv2.copyMakeBorder(
                    src=image,
                    top=20,
                    bottom=20,
                    left=20,
                    right=20,
                    borderType=cv2.BORDER_CONSTANT,
                    value=(255, 255, 255))

            bordered_image = add_border(img)
            #============================================================================

            #============================================================================
            # Image Binarization
            def grayscale(image):
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            gray_image = grayscale(img)

            # Apply Blur to reduce noise
            def apply_blur(image):
                return cv2.GaussianBlur(image, (3, 3), sigmaX=0, sigmaY=0)

            gau_image = apply_blur(gray_image)

            # Binarize
            thresh, im_bw = cv2.threshold(gau_image, 160, 240, cv2.THRESH_BINARY)
            #============================================================================

            #============================================================================
            # Dilation for font-thickening
            def thick_font(image):
                image = cv2.bitwise_not(image)
                kernel = np.ones((1, 1), np.uint8)
                image = cv2.dilate(image, kernel, iterations=1)

                image = cv2.bitwise_not(image)

                return (image)

            dilated = thick_font(im_bw)
            #============================================================================

            image_to_text = pytesseract.image_to_string(dilated, lang='eng')

            logging.debug(f"Text Extracted: {image_to_text}")

            # Initializing variable (list) to store extracted data from the ID
            extracted_info = {
                'years_of_residency': None,
                'voters_issued_at': None,
                'voters_issuance_date': None
            }
            
            residency_pattern = r"(\d+ year\(s\))"
            voters_issued_at_pattern = r"\s+(.+?)(?=\n|$)"
            voters_issuance_date_pattern = r"(\d{2}/\d{2}/\d{4})"
            
            residency_field_pattern = [
                    'Municipality : ', 'Municipality ; ', 'Municipality . ',
                    'Mun:cipality : ', 'Mun:cipality ; ', 'Mun:cipality . ',
                    'Munic:pality : ', 'Munic:pality ; ', 'Munic:pality . ',
                    'Municipal:ty : ', 'Municipal:ty ; ', 'Municipal:ty . ',
                    'Municipatity : ', 'Municipatity ; ', 'Municipatity . ',
                    'Mun:cipatity : ', 'Mun:cipatity ; ', 'Mun:cipatity . ',
                    'Munic:patity : ', 'Munic:patity ; ', 'Munic:patity . ',
                    'Municipat:ty : ', 'Municipat:ty ; ', 'Municipat:ty . ',
                    'Municipalily : ', 'Municipalily ; ', 'Municipalily . ',
                    'Mun:cipalily : ', 'Mun:cipalily ; ', 'Mun:cipalily . ',
                    'Munic:palily : ', 'Munic:palily ; ', 'Munic:palily . ',
                    'Municipal:ly : ', 'Municipal:ly ; ', 'Municipal:ly . ',
                    'Municipaliiy : ', 'Municipaliiy ; ', 'Municipaliiy . ',
                    'Mun:cipaliiy : ', 'Mun:cipaliiy ; ', 'Mun:cipaliiy . ',
                    'Munic:paliiy : ', 'Munic:paliiy ; ', 'Munic:paliiy . ',
                    'Municipal:iy : ', 'Municipal:iy ; ', 'Municipal:iy . ',
                    'Municipaity : ', 'Municipaity ; ', 'Municipaity . ', 
                    'Mun:cipaity : ', 'Mun:cipaity ; ', 'Mun:cipaity . ', 
                    'Munic:paity : ', 'Munic:paity ; ', 'Munic:paity . ',
                    'Municipa:ty : ', 'Municipa:ty ; ', 'Municipa:ty . ',
                    'Municipaily : ', 'Municipaily ; ', 'Municipaily . ',
                    'Mun:cipaily : ', 'Mun:cipaily ; ', 'Mun:cipaily . ',
                    'Munic:paily : ', 'Munic:paily ; ', 'Munic:paily . ',
                    'Municipa:ly : ', 'Municipa:ly ; ', 'Municipa:ly . ',
                    'Municipaiiy : ', 'Municipaiiy ; ', 'Municipaiiy . ',
                    'Mun:cipaiiy : ', 'Mun:cipaiiy ; ', 'Mun:cipaiiy . ',
                    'Munic:paiiy : ', 'Munic:paiiy ; ', 'Munic:paiiy . ',
                    'Municipa:iy : ', 'Municipa:iy ; ', 'Municipa:iy . ',
                    'Municipai:y : ', 'Municipai:y ; ', 'Municipai:y . ', 
                    'Municipatiiy : ', 'Municipatiiy ; ', 'Municipatiiy . ', 
                    'Mun:cipatiiy : ', 'Mun:cipatiiy ; ', 'Mun:cipatiiy . ', 
                    'Munic:patiiy : ', 'Munic:patiiy ; ', 'Munic:patiiy . ', 
                    'Municipat:iy : ', 'Municipat:iy ; ', 'Municipat:iy . ', 
                    'Municipali:y : ', 'Municipali:y ; ', 'Municipali:y . ',
                    'Mun:cipali:y : ', 'Mun:cipali:y ; ', 'Mun:cipali:y . ',
                    'Munic:pali:y : ', 'Munic:pali:y ; ', 'Munic:pali:y . ',
                    'Municipal::y : ', 'Municipal::y ; ', 'Municipal::y . ',
                    'Mun:cipai:y : ', 'Mun:cipai:y ; ', 'Mun:cipai:y . ', 
                    'Munic:pai:y : ', 'Munic:pai:y ; ', 'Munic:pai:y . ',
                    'Municipa::y : ', 'Municipa::y ; ', 'Municipa::y . ',
                    'Municipal:ity : ', 'Municipal:ity ; ', 'Municipal:ity . ',

                    'Niunicipality : ', 'Niunicipality ; ', 'Niunicipality . ',
                    'Niun:cipality : ', 'Niun:cipality ; ', 'Niun:cipality . ',
                    'Niunic:pality : ', 'Niunic:pality ; ', 'Niunic:pality . ',
                    'Niunicipal:ty : ', 'Niunicipal:ty ; ', 'Niunicipal:ty . ',
                    'Niunicipatity : ', 'Niunicipatity ; ', 'Niunicipatity . ',
                    'Niun:cipatity : ', 'Niun:cipatity ; ', 'Niun:cipatity . ',
                    'Niunic:patity : ', 'Niunic:patity ; ', 'Niunic:patity . ',
                    'Niunicipat:ty : ', 'Niunicipat:ty ; ', 'Niunicipat:ty . ',
                    'Niunicipalily : ', 'Niunicipalily ; ', 'Niunicipalily . ',
                    'Niun:cipalily : ', 'Niun:cipalily ; ', 'Niun:cipalily . ',
                    'Niunic:palily : ', 'Niunic:palily ; ', 'Niunic:palily . ',
                    'Niunicipal:ly : ', 'Niunicipal:ly ; ', 'Niunicipal:ly . ',
                    'Niunicipaity : ', 'Niunicipaity ; ', 'Niunicipaity . ',
                    'Niun:cipaity : ', 'Niun:cipaity ; ', 'Niun:cipaity . ',
                    'Niunic:paity : ', 'Niunic:paity ; ', 'Niunic:paity . ',
                    'Niunicipa:ty : ', 'Niunicipa:ty ; ', 'Niunicipa:ty . ',
                    'Niunicipaily : ', 'Niunicipaily ; ', 'Niunicipaily . ',
                    'Niun:cipaily : ', 'Niun:cipaily ; ', 'Niun:cipaily . ',
                    'Niunic:paily : ', 'Niunic:paily ; ', 'Niunic:paily . ',
                    'Niunicipa:ly : ', 'Niunicipa:ly ; ', 'Niunicipa:ly . ',
                    'Niunicipaliiy : ', 'Niunicipaliiy ; ', 'Niunicipaliiy . ',
                    'Niunicipal:iy : ', 'Niunicipal:iy ; ', 'Niunicipal:iy . ', 
                    'Niunicipatiiy : ', 'Niunicipatiiy ; ', 'Niunicipatiiy . ',
                    'Niun:cipatiiy : ', 'Niun:cipatiiy ; ', 'Niun:cipatiiy . ',
                    'Niunic:patiiy : ', 'Niunic:patiiy ; ', 'Niunic:patiiy . ',
                    'Niunicipat:iy : ', 'Niunicipat:iy ; ', 'Niunicipat:iy . ', 
                    'Niunicipali:y : ', 'Niunicipali:y ; ', 'Niunicipali:y . ',
                    'Niun:cipaliiy : ', 'Niun:cipaliiy ; ', 'Niun:cipaliiy . ',
                    'Niunic:paliiy : ', 'Niunic:paliiy ; ', 'Niunic:paliiy . ',
                    'Niunicipal::y : ', 'Niunicipal::y ; ', 'Niunicipal::y . ', 
                    'Niunicipaiiy : ', 'Niunicipaiiy ; ', 'Niunicipaiiy . ',
                    'Niunicipa:iy : ', 'Niunicipa:iy ; ', 'Niunicipa:iy . ', 
                    'Niunicipai:y : ', 'Niunicipai:y ; ', 'Niunicipai:y . ',
                    'Niun:cipaiiy : ', 'Niun:cipaiiy ; ', 'Niun:cipaiiy . ',
                    'Niunic:paiiy : ', 'Niunic:paiiy ; ', 'Niunic:paiiy . ',
                    'Niunicipa::y : ', 'Niunicipa::y ; ', 'Niunicipa::y . ', 
                    'Niunicipal:ity : ', 'Niunicipal:ity ; ', 'Niunicipal:ity . ',

                    'Viunicipality : ', 'Viunicipality ; ', 'Viunicipality . ',
                    'Viun:cipality : ', 'Viun:cipality ; ', 'Viun:cipality . ',
                    'Viunic:pality : ', 'Viunic:pality ; ', 'Viunic:pality . ',
                    'Viunicipal:ty : ', 'Viunicipal:ty ; ', 'Viunicipal:ty . ', 
                    'Viunicipatity : ', 'Viunicipatity ; ', 'Viunicipatity . ',
                    'Viun:cipatity : ', 'Viun:cipatity ; ', 'Viun:cipatity . ',
                    'Viunic:patity : ', 'Viunic:patity ; ', 'Viunic:patity . ',
                    'Viunicipat:ty : ', 'Viunicipat:ty ; ', 'Viunicipat:ty . ', 
                    'Viunicipalily : ', 'Viunicipalily ; ', 'Viunicipalily . ',
                    'Viun:cipalily : ', 'Viun:cipalily ; ', 'Viun:cipalily . ',
                    'Viunic:palily : ', 'Viunic:palily ; ', 'Viunic:palily . ',
                    'Viunicipal:ly : ', 'Viunicipal:ly ; ', 'Viunicipal:ly . ', 
                    'Viunicipaity : ', 'Viunicipaity ; ', 'Viunicipaity . ',
                    'Viun:cipaity : ', 'Viun:cipaity ; ', 'Viun:cipaity . ',
                    'Viunic:paity : ', 'Viunic:paity ; ', 'Viunic:paity . ',
                    'Viunicipa:ty : ', 'Viunicipa:ty ; ', 'Viunicipa:ty . ', 
                    'Viunicipaily : ', 'Viunicipaily ; ', 'Viunicipaily . ',
                    'Viun:cipaily : ', 'Viun:cipaily ; ', 'Viun:cipaily . ',
                    'Viunic:paily : ', 'Viunic:paily ; ', 'Viunic:paily . ',
                    'Viunicipa:ly : ', 'Viunicipa:ly ; ', 'Viunicipa:ly . ', 
                    'Viunicipaliiy : ', 'Viunicipaliiy ; ', 'Viunicipaliiy . ', 
                    'Viunicipatiiy : ', 'Viunicipatiiy ; ', 'Viunicipatiiy . ',
                    'Viun:cipatiiy : ', 'Viun:cipatiiy ; ', 'Viun:cipatiiy . ',
                    'Viunic:patiiy : ', 'Viunic:patiiy ; ', 'Viunic:patiiy . ',
                    'Viunicipat:iy : ', 'Viunicipat:iy ; ', 'Viunicipat:iy . ', 
                    'Viun:cipaliiy : ', 'Viun:cipaliiy ; ', 'Viun:cipaliiy . ',
                    'Viunic:paliiy : ', 'Viunic:paliiy ; ', 'Viunic:paliiy . ',
                    'Viunicipal:iy : ', 'Viunicipal:iy ; ', 'Viunicipal:iy . ', 
                    'Viunicipaiiy : ', 'Viunicipaiiy ; ', 'Viunicipaiiy . ',
                    'Viun:cipaiiy : ', 'Viun:cipaiiy ; ', 'Viun:cipaiiy . ',
                    'Viunic:paiiy : ', 'Viunic:paiiy ; ', 'Viunic:paiiy . ',
                    'Viunicipa:iy : ', 'Viunicipa:iy ; ', 'Viunicipa:iy . ', 
                    'Viunicipal:ity : ', 'Viunicipal:ity ; ', 'Viunicipal:ity . ',]
            voters_issued_at_field_pattern = [
                    'CITY OF', 'SITY OF', 'OITY OF', 'DITY OF', 'QITY OF', 
                    'ClTY OF', 'SlTY OF', 'OlTY OF', 'DlTY OF', 'QlTY OF',
                    'CITY DF', 'SITY DF', 'OITY DF', 'DITY DF', 'QITY DF',
                    'ClTY DF', 'SlTY DF', 'OlTY DF', 'DlTY DF', 'QlTY DF', 
                    'CITY 0F', 'SITY 0F', 'OITY 0F', 'DITY 0F', 'QITY 0F',
                    'ClTY 0F', 'SlTY 0F', 'OlTY 0F', 'DlTY 0F', 'QlTY 0F',]
            voters_issuance_date_field_pattern = [
                    'Date Issued : ', 'Date Issued ; ', 'Date Issued . ', 
                    'Dote Issued : ', 'Dote Issued ; ', 'Dote Issued . ', 
                    'Date lssued : ', 'Date lssued ; ', 'Date lssued . ', 
                    'Dote lssued : ', 'Dote lssued ; ', 'Dote lssued . ', 
                    'Dale Issued : ', 'Dale Issued ; ', 'Dale Issued . ', 
                    'Dale lssued : ', 'Dale lssued ; ', 'Dale lssued . ', 
                    'Dole Issued : ', 'Dole Issued ; ', 'Dole Issued . ', 
                    'Dole lssued : ', 'Dole lssued ; ', 'Dole lssued . ', 
                    'Oate Issued : ', 'Oate Issued ; ', 'Oate Issued . ', 
                    'Oate lssued : ', 'Oate lssued ; ', 'Oate lssued . ', 
                    'Oale Issued : ', 'Oale Issued ; ', 'Oale Issued . ', 
                    'Oale lssued : ', 'Oale lssued ; ', 'Oale lssued . ', 
                    'Oote Issued : ', 'Oote Issued ; ', 'Oote Issued . ', 
                    'Oote lssued : ', 'Oote lssued ; ', 'Oote lssued . ', 
                    'Oole Issued : ', 'Oole Issued ; ', 'Oole Issued . ', 
                    'Oole lssued : ', 'Oole lssued ; ', 'Oole lssued . ', 
                    
                    'Date Issued ', 'Date Issued ', 'Date Issued ', 
                    'Dote Issued ', 'Dote Issued ', 'Dote Issued ', 
                    'Date lssued ', 'Date lssued ', 'Date lssued ', 
                    'Dote lssued ', 'Dote lssued ', 'Dote lssued ', 
                    'Dale Issued ', 'Dale Issued ', 'Dale Issued ', 
                    'Dale lssued ', 'Dale lssued ', 'Dale lssued ', 
                    'Dole Issued ', 'Dole Issued ', 'Dole Issued ', 
                    'Dole lssued ', 'Dole lssued ', 'Dole lssued ', 
                    'Oate Issued ', 'Oate Issued ', 'Oate Issued ', 
                    'Oate lssued ', 'Oate lssued ', 'Oate lssued ', 
                    'Oale Issued ', 'Oale Issued ', 'Oale Issued ', 
                    'Oale lssued ', 'Oale lssued ', 'Oale lssued ', 
                    'Oote Issued ', 'Oote Issued ', 'Oote Issued ', 
                    'Oote lssued ', 'Oote lssued ', 'Oote lssued ', 
                    'Oole Issued ', 'Oole Issued ', 'Oole Issued ', 
                    'Oole lssued ', 'Oole lssued ', 'Oole lssued ', 
                ]
            

            # Appending Section
            # Iterate through the field patterns and their associated patterns
            for pattern in residency_field_pattern:
                match = re.search(f"{pattern}{residency_pattern}", image_to_text, flags=re.DOTALL)

                if match:
                    extracted_info['years_of_residency'] = match.group(1).strip()
                    break
                
            for pattern in voters_issued_at_field_pattern:
                match = re.search(f"{pattern}{voters_issued_at_pattern}", image_to_text, flags=re.DOTALL)

                if match:
                    extracted_info['voters_issued_at'] = match.group(1).strip()
                    break
            
            for pattern in voters_issuance_date_field_pattern:
                match = re.search(f"{pattern}{voters_issuance_date_pattern}", image_to_text, flags=re.DOTALL)

                if match:
                    extracted_info['voters_issuance_date'] = match.group(1).strip()
                    break
            
            img = None

            return extracted_info
        
        else:
            logging.error(f'Failed to read image')
            return None
    else:
        logging.error('voters_certificate is not a File object')
        return None

def extract_guardian_voters(guardians_voter_certificate_content, guardians_voter_certificate_name):
    if guardians_voter_certificate_name:
        logging.debug(f'guardians_voter_certificate name: {guardians_voter_certificate_name}')
        
    if guardians_voter_certificate_content:
        nparr = np.fromstring(guardians_voter_certificate_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 

        if img is not None:
            #============================================================================
            # Rescaling Image
            desired_dpi = 300

            original_width, original_height = img.shape[1], img.shape[0]
            new_width = int(original_width * (desired_dpi / 72.0))                                  # 72 DPI is the default DPI for most images
            new_height = int(original_height * (desired_dpi / 72.0))

            resized_image = cv2.resize(img, (new_width, new_height))
            #============================================================================

            #============================================================================
            # Add borders to the image
            def add_border(image):
                return cv2.copyMakeBorder(
                    src=image,
                    top=20,
                    bottom=20,
                    left=20,
                    right=20,
                    borderType=cv2.BORDER_CONSTANT,
                    value=(255, 255, 255))

            bordered_image = add_border(img)
            #============================================================================

            #============================================================================
            # Image Binarization
            def grayscale(image):
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            gray_image = grayscale(img)

            # Apply Blur to reduce noise
            def apply_blur(image):
                return cv2.GaussianBlur(image, (3, 3), sigmaX=0, sigmaY=0)

            gau_image = apply_blur(gray_image)

            # Binarize
            thresh, im_bw = cv2.threshold(gau_image, 160, 240, cv2.THRESH_BINARY)
            #============================================================================

            #============================================================================
            # Dilation for font-thickening
            def thick_font(image):
                image = cv2.bitwise_not(image)
                kernel = np.ones((1, 1), np.uint8)
                image = cv2.dilate(image, kernel, iterations=1)

                image = cv2.bitwise_not(image)

                return (image)

            dilated = thick_font(im_bw)
            #============================================================================

            image_to_text = pytesseract.image_to_string(dilated, lang='eng')

            # Initializing variable (list) to store extracted data from the ID
            extracted_guardian_info = {
                'guardians_years_of_residency': None,
                'guardians_voters_issued_at': None,
                'guardians_voters_issuance_date': None
            }
            
            residency_pattern = r"(\d+ year\(s\))"
            voters_issued_at_pattern = r"\s+(.+?)(?=\n|$)"
            voters_issuance_date_pattern = r"(\d{2}/\d{2}/\d{4})"
            
            residency_field_pattern = [
                    'Municipality : ', 'Municipality ; ', 'Municipality . ',
                    'Mun:cipality : ', 'Mun:cipality ; ', 'Mun:cipality . ',
                    'Munic:pality : ', 'Munic:pality ; ', 'Munic:pality . ',
                    'Municipal:ty : ', 'Municipal:ty ; ', 'Municipal:ty . ',
                    'Municipatity : ', 'Municipatity ; ', 'Municipatity . ',
                    'Mun:cipatity : ', 'Mun:cipatity ; ', 'Mun:cipatity . ',
                    'Munic:patity : ', 'Munic:patity ; ', 'Munic:patity . ',
                    'Municipat:ty : ', 'Municipat:ty ; ', 'Municipat:ty . ',
                    'Municipalily : ', 'Municipalily ; ', 'Municipalily . ',
                    'Mun:cipalily : ', 'Mun:cipalily ; ', 'Mun:cipalily . ',
                    'Munic:palily : ', 'Munic:palily ; ', 'Munic:palily . ',
                    'Municipal:ly : ', 'Municipal:ly ; ', 'Municipal:ly . ',
                    'Municipaliiy : ', 'Municipaliiy ; ', 'Municipaliiy . ',
                    'Mun:cipaliiy : ', 'Mun:cipaliiy ; ', 'Mun:cipaliiy . ',
                    'Munic:paliiy : ', 'Munic:paliiy ; ', 'Munic:paliiy . ',
                    'Municipal:iy : ', 'Municipal:iy ; ', 'Municipal:iy . ',
                    'Municipaity : ', 'Municipaity ; ', 'Municipaity . ', 
                    'Mun:cipaity : ', 'Mun:cipaity ; ', 'Mun:cipaity . ', 
                    'Munic:paity : ', 'Munic:paity ; ', 'Munic:paity . ',
                    'Municipa:ty : ', 'Municipa:ty ; ', 'Municipa:ty . ',
                    'Municipaily : ', 'Municipaily ; ', 'Municipaily . ',
                    'Mun:cipaily : ', 'Mun:cipaily ; ', 'Mun:cipaily . ',
                    'Munic:paily : ', 'Munic:paily ; ', 'Munic:paily . ',
                    'Municipa:ly : ', 'Municipa:ly ; ', 'Municipa:ly . ',
                    'Municipaiiy : ', 'Municipaiiy ; ', 'Municipaiiy . ',
                    'Mun:cipaiiy : ', 'Mun:cipaiiy ; ', 'Mun:cipaiiy . ',
                    'Munic:paiiy : ', 'Munic:paiiy ; ', 'Munic:paiiy . ',
                    'Municipa:iy : ', 'Municipa:iy ; ', 'Municipa:iy . ',
                    'Municipai:y : ', 'Municipai:y ; ', 'Municipai:y . ', 
                    'Municipatiiy : ', 'Municipatiiy ; ', 'Municipatiiy . ', 
                    'Mun:cipatiiy : ', 'Mun:cipatiiy ; ', 'Mun:cipatiiy . ', 
                    'Munic:patiiy : ', 'Munic:patiiy ; ', 'Munic:patiiy . ', 
                    'Municipat:iy : ', 'Municipat:iy ; ', 'Municipat:iy . ', 
                    'Municipali:y : ', 'Municipali:y ; ', 'Municipali:y . ',
                    'Mun:cipali:y : ', 'Mun:cipali:y ; ', 'Mun:cipali:y . ',
                    'Munic:pali:y : ', 'Munic:pali:y ; ', 'Munic:pali:y . ',
                    'Municipal::y : ', 'Municipal::y ; ', 'Municipal::y . ',
                    'Mun:cipai:y : ', 'Mun:cipai:y ; ', 'Mun:cipai:y . ', 
                    'Munic:pai:y : ', 'Munic:pai:y ; ', 'Munic:pai:y . ',
                    'Municipa::y : ', 'Municipa::y ; ', 'Municipa::y . ',
                    'Municipal:ity : ', 'Municipal:ity ; ', 'Municipal:ity . ',

                    'Niunicipality : ', 'Niunicipality ; ', 'Niunicipality . ',
                    'Niun:cipality : ', 'Niun:cipality ; ', 'Niun:cipality . ',
                    'Niunic:pality : ', 'Niunic:pality ; ', 'Niunic:pality . ',
                    'Niunicipal:ty : ', 'Niunicipal:ty ; ', 'Niunicipal:ty . ',
                    'Niunicipatity : ', 'Niunicipatity ; ', 'Niunicipatity . ',
                    'Niun:cipatity : ', 'Niun:cipatity ; ', 'Niun:cipatity . ',
                    'Niunic:patity : ', 'Niunic:patity ; ', 'Niunic:patity . ',
                    'Niunicipat:ty : ', 'Niunicipat:ty ; ', 'Niunicipat:ty . ',
                    'Niunicipalily : ', 'Niunicipalily ; ', 'Niunicipalily . ',
                    'Niun:cipalily : ', 'Niun:cipalily ; ', 'Niun:cipalily . ',
                    'Niunic:palily : ', 'Niunic:palily ; ', 'Niunic:palily . ',
                    'Niunicipal:ly : ', 'Niunicipal:ly ; ', 'Niunicipal:ly . ',
                    'Niunicipaity : ', 'Niunicipaity ; ', 'Niunicipaity . ',
                    'Niun:cipaity : ', 'Niun:cipaity ; ', 'Niun:cipaity . ',
                    'Niunic:paity : ', 'Niunic:paity ; ', 'Niunic:paity . ',
                    'Niunicipa:ty : ', 'Niunicipa:ty ; ', 'Niunicipa:ty . ',
                    'Niunicipaily : ', 'Niunicipaily ; ', 'Niunicipaily . ',
                    'Niun:cipaily : ', 'Niun:cipaily ; ', 'Niun:cipaily . ',
                    'Niunic:paily : ', 'Niunic:paily ; ', 'Niunic:paily . ',
                    'Niunicipa:ly : ', 'Niunicipa:ly ; ', 'Niunicipa:ly . ',
                    'Niunicipaliiy : ', 'Niunicipaliiy ; ', 'Niunicipaliiy . ',
                    'Niunicipal:iy : ', 'Niunicipal:iy ; ', 'Niunicipal:iy . ', 
                    'Niunicipatiiy : ', 'Niunicipatiiy ; ', 'Niunicipatiiy . ',
                    'Niun:cipatiiy : ', 'Niun:cipatiiy ; ', 'Niun:cipatiiy . ',
                    'Niunic:patiiy : ', 'Niunic:patiiy ; ', 'Niunic:patiiy . ',
                    'Niunicipat:iy : ', 'Niunicipat:iy ; ', 'Niunicipat:iy . ', 
                    'Niunicipali:y : ', 'Niunicipali:y ; ', 'Niunicipali:y . ',
                    'Niun:cipaliiy : ', 'Niun:cipaliiy ; ', 'Niun:cipaliiy . ',
                    'Niunic:paliiy : ', 'Niunic:paliiy ; ', 'Niunic:paliiy . ',
                    'Niunicipal::y : ', 'Niunicipal::y ; ', 'Niunicipal::y . ', 
                    'Niunicipaiiy : ', 'Niunicipaiiy ; ', 'Niunicipaiiy . ',
                    'Niunicipa:iy : ', 'Niunicipa:iy ; ', 'Niunicipa:iy . ', 
                    'Niunicipai:y : ', 'Niunicipai:y ; ', 'Niunicipai:y . ',
                    'Niun:cipaiiy : ', 'Niun:cipaiiy ; ', 'Niun:cipaiiy . ',
                    'Niunic:paiiy : ', 'Niunic:paiiy ; ', 'Niunic:paiiy . ',
                    'Niunicipa::y : ', 'Niunicipa::y ; ', 'Niunicipa::y . ', 
                    'Niunicipal:ity : ', 'Niunicipal:ity ; ', 'Niunicipal:ity . ',

                    'Viunicipality : ', 'Viunicipality ; ', 'Viunicipality . ',
                    'Viun:cipality : ', 'Viun:cipality ; ', 'Viun:cipality . ',
                    'Viunic:pality : ', 'Viunic:pality ; ', 'Viunic:pality . ',
                    'Viunicipal:ty : ', 'Viunicipal:ty ; ', 'Viunicipal:ty . ', 
                    'Viunicipatity : ', 'Viunicipatity ; ', 'Viunicipatity . ',
                    'Viun:cipatity : ', 'Viun:cipatity ; ', 'Viun:cipatity . ',
                    'Viunic:patity : ', 'Viunic:patity ; ', 'Viunic:patity . ',
                    'Viunicipat:ty : ', 'Viunicipat:ty ; ', 'Viunicipat:ty . ', 
                    'Viunicipalily : ', 'Viunicipalily ; ', 'Viunicipalily . ',
                    'Viun:cipalily : ', 'Viun:cipalily ; ', 'Viun:cipalily . ',
                    'Viunic:palily : ', 'Viunic:palily ; ', 'Viunic:palily . ',
                    'Viunicipal:ly : ', 'Viunicipal:ly ; ', 'Viunicipal:ly . ', 
                    'Viunicipaity : ', 'Viunicipaity ; ', 'Viunicipaity . ',
                    'Viun:cipaity : ', 'Viun:cipaity ; ', 'Viun:cipaity . ',
                    'Viunic:paity : ', 'Viunic:paity ; ', 'Viunic:paity . ',
                    'Viunicipa:ty : ', 'Viunicipa:ty ; ', 'Viunicipa:ty . ', 
                    'Viunicipaily : ', 'Viunicipaily ; ', 'Viunicipaily . ',
                    'Viun:cipaily : ', 'Viun:cipaily ; ', 'Viun:cipaily . ',
                    'Viunic:paily : ', 'Viunic:paily ; ', 'Viunic:paily . ',
                    'Viunicipa:ly : ', 'Viunicipa:ly ; ', 'Viunicipa:ly . ', 
                    'Viunicipaliiy : ', 'Viunicipaliiy ; ', 'Viunicipaliiy . ', 
                    'Viunicipatiiy : ', 'Viunicipatiiy ; ', 'Viunicipatiiy . ',
                    'Viun:cipatiiy : ', 'Viun:cipatiiy ; ', 'Viun:cipatiiy . ',
                    'Viunic:patiiy : ', 'Viunic:patiiy ; ', 'Viunic:patiiy . ',
                    'Viunicipat:iy : ', 'Viunicipat:iy ; ', 'Viunicipat:iy . ', 
                    'Viun:cipaliiy : ', 'Viun:cipaliiy ; ', 'Viun:cipaliiy . ',
                    'Viunic:paliiy : ', 'Viunic:paliiy ; ', 'Viunic:paliiy . ',
                    'Viunicipal:iy : ', 'Viunicipal:iy ; ', 'Viunicipal:iy . ', 
                    'Viunicipaiiy : ', 'Viunicipaiiy ; ', 'Viunicipaiiy . ',
                    'Viun:cipaiiy : ', 'Viun:cipaiiy ; ', 'Viun:cipaiiy . ',
                    'Viunic:paiiy : ', 'Viunic:paiiy ; ', 'Viunic:paiiy . ',
                    'Viunicipa:iy : ', 'Viunicipa:iy ; ', 'Viunicipa:iy . ', 
                    'Viunicipal:ity : ', 'Viunicipal:ity ; ', 'Viunicipal:ity . ',]
            voters_issued_at_field_pattern = [
                    'CITY OF', 'SITY OF', 'OITY OF', 'DITY OF', 'QITY OF', 
                    'ClTY OF', 'SlTY OF', 'OlTY OF', 'DlTY OF', 'QlTY OF',
                    'CITY DF', 'SITY DF', 'OITY DF', 'DITY DF', 'QITY DF',
                    'ClTY DF', 'SlTY DF', 'OlTY DF', 'DlTY DF', 'QlTY DF', 
                    'CITY 0F', 'SITY 0F', 'OITY 0F', 'DITY 0F', 'QITY 0F',
                    'ClTY 0F', 'SlTY 0F', 'OlTY 0F', 'DlTY 0F', 'QlTY 0F',]
            voters_issuance_date_field_pattern = [
                    'Date Issued : ', 'Date Issued ; ', 'Date Issued . ', 
                    'Dote Issued : ', 'Dote Issued ; ', 'Dote Issued . ', 
                    'Date lssued : ', 'Date lssued ; ', 'Date lssued . ', 
                    'Dote lssued : ', 'Dote lssued ; ', 'Dote lssued . ', 
                    'Dale Issued : ', 'Dale Issued ; ', 'Dale Issued . ', 
                    'Dale lssued : ', 'Dale lssued ; ', 'Dale lssued . ', 
                    'Dole Issued : ', 'Dole Issued ; ', 'Dole Issued . ', 
                    'Dole lssued : ', 'Dole lssued ; ', 'Dole lssued . ', 
                    'Oate Issued : ', 'Oate Issued ; ', 'Oate Issued . ', 
                    'Oate lssued : ', 'Oate lssued ; ', 'Oate lssued . ', 
                    'Oale Issued : ', 'Oale Issued ; ', 'Oale Issued . ', 
                    'Oale lssued : ', 'Oale lssued ; ', 'Oale lssued . ', 
                    'Oote Issued : ', 'Oote Issued ; ', 'Oote Issued . ', 
                    'Oote lssued : ', 'Oote lssued ; ', 'Oote lssued . ', 
                    'Oole Issued : ', 'Oole Issued ; ', 'Oole Issued . ', 
                    'Oole lssued : ', 'Oole lssued ; ', 'Oole lssued . ', 
                    
                    'Date Issued ', 'Date Issued ', 'Date Issued ', 
                    'Dote Issued ', 'Dote Issued ', 'Dote Issued ', 
                    'Date lssued ', 'Date lssued ', 'Date lssued ', 
                    'Dote lssued ', 'Dote lssued ', 'Dote lssued ', 
                    'Dale Issued ', 'Dale Issued ', 'Dale Issued ', 
                    'Dale lssued ', 'Dale lssued ', 'Dale lssued ', 
                    'Dole Issued ', 'Dole Issued ', 'Dole Issued ', 
                    'Dole lssued ', 'Dole lssued ', 'Dole lssued ', 
                    'Oate Issued ', 'Oate Issued ', 'Oate Issued ', 
                    'Oate lssued ', 'Oate lssued ', 'Oate lssued ', 
                    'Oale Issued ', 'Oale Issued ', 'Oale Issued ', 
                    'Oale lssued ', 'Oale lssued ', 'Oale lssued ', 
                    'Oote Issued ', 'Oote Issued ', 'Oote Issued ', 
                    'Oote lssued ', 'Oote lssued ', 'Oote lssued ', 
                    'Oole Issued ', 'Oole Issued ', 'Oole Issued ', 
                    'Oole lssued ', 'Oole lssued ', 'Oole lssued ', 
                ]
            
            # Appending Section
            # Iterate through the field patterns and their associated patterns
            for pattern in residency_field_pattern:
                match = re.search(f"{pattern}{residency_pattern}", image_to_text, flags=re.DOTALL)

                if match:
                    extracted_guardian_info['guardians_years_of_residency'] = match.group(1).strip()
                    break
                
            for pattern in voters_issued_at_field_pattern:
                match = re.search(f"{pattern}{voters_issued_at_pattern}", image_to_text, flags=re.DOTALL)

                if match:
                    extracted_guardian_info['guardians_voters_issued_at'] = match.group(1).strip()
                    break
            
            for pattern in voters_issuance_date_field_pattern:
                match = re.search(f"{pattern}{voters_issuance_date_pattern}", image_to_text, flags=re.DOTALL)

                if match:
                    extracted_guardian_info['guardians_voters_issuance_date'] = match.group(1).strip()
                    break
            
            img = None

            return extracted_guardian_info
        
        else:
            logging.error(f'Failed to read image')
            return None
    else:
        logging.error('voters_certificate is not a File object')
        return None

