from typing import Any
from PIL import Image
import easyocr
import pytesseract
import numpy as np
from typing import Optional

class ImageToText:
    def __init__(self,method:Optional[str],lang:Optional[str|list]='eng'):
        '''
        Args: 
            image_path = path to the image \n
            image = numpy array containing image \n
            method = algorithm to use (supported : easyocr,pytesseract) \n
            lang = language of text in image. Please visit respective algorithm for more info on lang \n
        '''
        self.method = method
        self.lang = lang

        if self.method == 'easyocr':
            try:
                assert type(self.lang) == list
            except:
                raise Exception('Lang should be of type list for method = easyocr')
            self.easyocr_reader = easyocr.Reader(self.lang) 

        if self.method is None:
            raise ValueError('Please specify method as pytesseract or easyocr')
        
    def pytesseract_text(self):
        '''
        return : extracted text
        '''
        extracted_text = pytesseract.image_to_string(self.image_path,lang=self.lang)
        return extracted_text
    
    def easyocr_text(self):
        '''
        return : list of tuple containing list of (text co-ordinates,text,..) 
        '''
        extracted_text = self.easyocr_reader.readtext(self.image_path)
        return extracted_text

    def read(self,image_path:Optional[str],image:Optional=None):
        '''
        Args: 
            image_path = path to the image \n
            image = numpy array containing image \n

        returns : String 
        '''
        self.image_path = image_path
        self.image = image

        if self.image is not None :
            raise Exception('Reading with image Not Implemented please use image_iath instead')
        if self.image_path is not None :
            try :
                self.image = Image.open(self.image_path)
            except :
                raise Exception('Image non readable please check path or extension')

        if self.method == 'pytesseract':
            text = self.pytesseract_text()
            return text
        elif self.method == 'easyocr':
            text = self.easyocr_text()
            temp_meta = ""
            for extract in text:
                temp_meta = temp_meta + extract[1] + " "
            return temp_meta
        else :
            raise ValueError('Please specify method as pytesseract or easyocr')

