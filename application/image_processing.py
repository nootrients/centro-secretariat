from PIL import Image

import pytesseract

import cv2
import numpy as np

import re, io, logging

from django.core.files.uploadedfile import InMemoryUploadedFile



# CONSTANTS
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
logging.basicConfig(level=logging.DEBUG)

def extract_id_info(national_id):
    if isinstance(national_id, InMemoryUploadedFile):
        logging.debug(f'national_id: {national_id.name}')
        print(national_id.name)

        binary_data = national_id.read()
        nparr = np.fromstring(binary_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
        
        #img = cv2.imdecode(np.frombuffer(binary_data, np.uint8), cv2.IMREAD_COLOR)

        if img is not None:
            #img = cv2.imread(national_id)
    
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

            # Invert image
            inverted_image = cv2.bitwise_not(img)

            #============================================================================
            # Rescaling Image
            desired_dpi = 300

            original_width, original_height = img.shape[1], img.shape[0]
            new_width = int(original_width * (desired_dpi / 72.0))                                  # 72 DPI is the default DPI for most images
            new_height = int(original_height * (desired_dpi / 72.0))

            resized_image = cv2.resize(img, (new_width, new_height))
            #============================================================================


            #============================================================================
            # Grayscaling
            def grayscale(image):
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            gray_image = grayscale(bordered_img)


            # Applying Gaussian Blur
            gau_image = cv2.GaussianBlur(src=gray_image, ksize=(3, 3), sigmaX=0, sigmaY=0)          # NOT USED!


            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))                          # CURRENT
            clahe_img = clahe.apply(gray_image)


            # Binarize Image
            thresh, im_bw = cv2.threshold(gray_image, 160, 240, type=cv2.THRESH_BINARY)              # MODIFIED FOR BINARY THRESHOLDING


            #thresh, im_bw = cv2.threshold(clahe_img, 115, 255, cv2.THRESH_TRUNC)                 # ONLY GET THE THREE NAMES


            # Removing Image noise
            no_noise = noise_removal(im_bw)
            #============================================================================


            # Dilation for font-thickening
            def thick_font(image):
                image = cv2.bitwise_not(image)
                kernel = np.ones((1, 1), np.uint8)
                image = cv2.dilate(image, kernel, iterations=1)

                image = cv2.bitwise_not(image)

                return (image)

            dilated = thick_font(im_bw)


            image_to_text = pytesseract.image_to_string(dilated, lang='eng')


            last_name_patterns = [
                r"(?:Apelyido|Last Name)\s+([A-Z\s]+)(?=\s|$)",
                r"(?:Apelyido|Lost Name)\s+([A-Z\s]+)(?=\s|$)",
                    
                r"Apelyido/Last Name\s+([A-Z\s]+)(?=\n|$)",
                r"Apelyido/Last Name\s+([A-Z\s]+)(?=\n|$)",
                r"Apelyido/Lost Name\s+([A-Z\s]+)(?=\n|$)",
                r"Apeyido/Last Name\s+([A-Z\s]+)(?=\n|$)",
                r"Apeyido/Lost Name\s+([A-Z\s]+)(?=\n|$)",
                r"Apeiyido/Last Name\s+(A-Z\s]+)(?=\n|$)",
                r"Apeiyido/Lost Name\s+([A-Z\s]+)(?=\n|$)",

                r"Apelyido/Last Name\na ~\s+([A-Z\s]+)(?=\n|$)",
                ]

            given_name_patterns = [
                r"Mga Pangalan/Given Names\s+([A-Z\s]+)(?=\n|$)",
                r"Mga Pangalan/Given Names 4\s+([A-Z\s]+)(?=\n|$)",
                r"Mga Pangalan/Given Names %\s+([A-Z\s]+)(?=\n|$)",
                r"Mga Pangalan/Given Names Ge\s+([A-Z\s]+)(?=\n|$)",

                r"Mga Pangsian/Given Names.\s+([A-Z\s]+)(?=\n|$)",
                    
                r"Mega Pangalan/Given Names\s+([A-Z\s]+)(?=\n|$)",
                r"Mega Pangalan/Given Names 4\s+([A-Z\s]+)(?=\n|$)",
                r"Mega Pangalan/Given Names %\s+([A-Z\s]+)(?=\n|$)",
                r"Mega Pangalan/Given Names Ge\s+([A-Z\s]+)(?=\n|$)",
                    
                r"Mega Pangalan/Given Names(?:[^A-Z]*[“‘=~-]*)?\s+([A-Z\s]+)(?=\s[A-Z]\s*\n|$)",

                r"Mega Pangalan/Given Names\s+[A-Z\s]+\n([A-Z\s]+)",

                r"Niga Pangalan/Given Names\s+([A-Z\s]+)(?=\n|$)",
                r"Niga Pangalan/Given Names 4\s+([A-Z\s]+)(?=\n|$)",
                r"Niga Pangalan/Given Names %\s+([A-Z\s]+)(?=\n|$)",
                r"Niga Pangalan/Given Names Ge\s+([A-Z\s]+)(?=\n|$)",

                r"Viga Pangalan/Given Names\s+([A-Z\s]+)(?=\n|$)",
                r"Viga Pangalan/Given Names 4\s+([A-Z\s]+)(?=\n|$)",
                r"Viga Pangalan/Given Names %\s+([A-Z\s]+)(?=\n|$)",
                r"Viga Pangalan/Given Names Ge\s+([A-Z\s]+)(?=\n|$)",
                ]

            middle_name_patterns = [
                r"(?:Gitnang Apelyido|Middle Name)\s+([A-Z\s]+)(?=\n|$)",
                r"(?:Gitnang Apelyido|Midale Name)\s+([A-Z\s]+)(?=\n|$)",

                r"Gitnang Apelyido/Middle Name\s+([A-Z\s]+)(?=\n|$)",
                r"Gitnang Apelyido/Middle Name 4\s+([A-Z\s]+)(?=\n|$)",
                r"Gitnang Apelyido/Middle Name %\s+([A-Z\s]+)(?=\n|$)",
                r"Gitnang Apelyido/Middle Name Ge\s+([A-Z\s]+)(?=\n|$)",
                    
                r"Gitnang Apeiyido/Middle Name\s+([A-Z\s]+)(?=\n|$)",
                r"Gitnang Apelyido/Midale Name\s+([A-Z\s]+)(?=\n|$)",
                r"Gitnang Apeiyido/Midale Name\s+([A-Z\s]+)(?=\n|$)",
                r"— Gitnang Apelyido/Middle Name\n\s+([A-Z\s]+)(?=\n|$)",
                r"Gitnang Apelyido/Middle Name\n[^A-Z]*([A-Z\s]+)(?=\n|$)",

                r"Gitnang Apely:ido/Midale Name\.\s*[-=~]*\s*([A-Z\s]+)(?=\s|$|\n)",
                ]

            extracted_data = {}

            for last_name_pattern in last_name_patterns:
                match = re.search(last_name_pattern, image_to_text, flags=re.DOTALL)
                if match:
                    extracted_data['lastname'] = match.group(1).strip()
                    break
                    

            for given_name_pattern in given_name_patterns:
                match = re.search(given_name_pattern, image_to_text, flags=re.DOTALL)

                if match:
                    extracted_data['firstname'] = match.group(1).strip()
                    break


            for middle_name_pattern in middle_name_patterns:
                match = re.search(middle_name_pattern, image_to_text, flags=re.DOTALL)

                if match:
                    extracted_data['middlename'] = match.group(1).strip()
                    break

            return extracted_data
        else:
            logging.error(f'Failed to read image')
            return None
    else:
        logging.error('national_id is not a File object')
        return None

def extract_applicant_voters(uploaded_applicant_voters):
    # Preprocess the uploaded image
    pass


def extract_guardian_voters(uploaded_guardian_voters):
    # Preprocess the uploaded image
    pass

