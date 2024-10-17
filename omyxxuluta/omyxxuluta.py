import time
import os
import zipfile

import requests

# get the start time
wall_st = time.time()
cpu_st = time.process_time()

import cv2
import numpy as np

import easyocr
import re

def set_marker_colour(pen_colour='orange'):
    
    if pen_colour.strip().lower() == 'red':
        # Define the lower and upper bounds for the red color in HSV
        lower_bound = np.array([0, 50, 50])
        upper_bound = np.array([10, 255, 255])

    elif pen_colour.strip().lower() == 'black':
        lower_bound = np.array([0, 0, 0])
        upper_bound = np.array([180, 250, 30])

    elif pen_colour.strip().lower() == 'grey':
        lower_bound = np.array([0, 0, 50])
        upper_bound = np.array([180, 50, 200])

    elif pen_colour.strip().lower() == 'orange':
        # Define lower and upper bounds for orange color
        lower_bound = np.array([10, 100, 100])
        upper_bound = np.array([25, 255, 255])

    elif pen_colour.strip().lower() == 'blue':

        # Define lower and upper bounds for blue color
        lower_bound = np.array([100, 150, 0])
        upper_bound = np.array([140, 255, 255])


    elif pen_colour.strip().lower() == 'green':
        # Define lower and upper bounds for green color
        lower_bound = np.array([35, 100, 100])
        upper_bound = np.array([85, 255, 255])
        
        
    return lower_bound, upper_bound


def get_extracted_region(file_name, lower_bound, upper_bound):

                    
    # Load the image
    image = cv2.imread(file_name)

    # Convert the image to HSV color space since it's easier to detect the contours in this
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cv2.imshow("display", hsv)


    # Threshold the HSV image to get only specified colors
    # this sets all the values in this range to 255 and rest to 0   

    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Find contours in the masked image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a copy of the image to draw contours
    output_image = image.copy()


    # # Loop over the contours and filter out those with a single color
    # filtered_contours = []
    # for contour in contours:
    #     # Create a mask for the current contour
    #     contour_mask = np.zeros_like(mask)
    #     cv2.drawContours(contour_mask, [contour], -1, 255, thickness=cv2.FILLED)
        
    #     # Extract the HSV values within the contour
    #     hsv_values = hsv[contour_mask == 255]
        
    #     # Check if all HSV values are the same within the contour
    #     if np.all(hsv_values == hsv_values[0]):
    #         continue  # Skip contours with a single color
        
    #     # If not, add to filtered contours
    #     filtered_contours.append(contour)
    filtered_contours = contours

    # # Draw filtered contours on the image
    cv2.drawContours(output_image, filtered_contours, -1, (0, 255, 0), 2)

    # Loop over the contours to find the largest one
    largest_contour = None
    max_area = 0
    for contour in filtered_contours:
        area = cv2.contourArea(contour)

        if area > max_area:
            largest_contour = contour
            max_area = area

    # If the selected colour contour is found, draw its bounding box
    if largest_contour is not None:
        # Get the bounding rectangle of the contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        x = x+5
        y = y+10
        if w>=20:
            w = w-10
        if h>=20:
            h = h-10
        # Draw a green rectangle around the detected circle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Extract the region of interest (ROI) from the original image
        roi = image[y:y+h, x:x+w]
        extracted_output_directory = file_name.rsplit('/',2)[0] + '/output/'
        extracted_output_filename = file_name.rsplit('/',1)[1].rsplit('.')[0] + '-extracted.png'
        extracted_filename = extracted_output_directory + extracted_output_filename

        cv2.imwrite(extracted_filename, roi)

        # Display the ROI
        cv2.imshow('ROI', roi)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No red circle found.")
        raise Exception(" There is no region found")
    
    return extracted_filename



def process_strings(strings):
        result = []
        for string in strings:
            if "'Juros" in string:
                break
            result.append(string)
        return result

def process_strings_with_second_juros(strings):
    if 'Juros' in strings:
        combined_string = ' '.join(strings)
        # Generalized regex to find a date followed by any text pattern (e.g., "USINA AUTO CENTER")
        match = re.search(r'\b\d{2}/\d{2}\b.*', combined_string)
        if match:
            start_index = match.start()
            cleaned_string = combined_string[start_index:]
            result = cleaned_string.split()
            return result
    else:
        None
    return strings

def combine_text_elements(strings):
    

    
    result = []
    text_buffer = []

    date_pattern = re.compile(r'\b\d{2}/\d{2}\b')
    number_pattern = re.compile(r'\b\d+(?:,\d{2})?\b')

    for string in strings:
        if date_pattern.match(string) or number_pattern.match(string):
            if text_buffer:
                # Combine buffered text elements into a single string if there are multiple text elements
                if len(text_buffer) > 1:
                    result.append(' '.join(text_buffer))
                else:
                    result.extend(text_buffer)
                text_buffer = []
            result.append(string)
        else:
            text_buffer.append(string)

    # Check the last buffer
    if text_buffer:
        if len(text_buffer) > 1:
            result.append(' '.join(text_buffer))
        else:
            result.extend(text_buffer)

    return result


def extract_text_from_roi(file_name):
    
    """
    Extract text from the Region of Interest
    
    :param file_name: Name of the file to extract the text from 
    :return: Json object containing the required elements
    """
    

    reader = easyocr.Reader(['pt'], gpu=False)
    result = reader.readtext(file_name)
    
    strings_only = [item for sublist in result for item in sublist if isinstance(item, str)]
    result1 = process_strings(strings_only)
    result2 = process_strings_with_second_juros(result1)
    final_result = combine_text_elements(result2)
    
    input_text = ' '.join(final_result)


    # Split the text into parts
    parts = input_text.split()
    
    elements_list = merge_elements_by_regex(parts, r'[A-Z]+')
    
    json_object = create_final_json(elements_list)
    
    return json_object
    
    
def merge_elements_by_regex(original_list, pattern):
    
    """
    Merges elements in the original_list that match the given regex pattern.

    :param original_list: List of elements to be merged.
    :param pattern: Regex pattern to match elements for merging.
    :return: New list with merged elements.
    
    """
    
    merged_list = []
    merge_buffer = []

    for element in original_list:
        if re.search(pattern, element):
            merge_buffer.append(element)
        else:
            if merge_buffer:
                merged_list.append(' '.join(merge_buffer))
                merge_buffer = []
            merged_list.append(element)

    if merge_buffer:
        merged_list.append(' '.join(merge_buffer))

    return merged_list




#     pattern = r'[A-Z]+'  # Regex pattern to match elements with uppercase letters

#     new_list = merge_elements_by_regex(parts, r'[A-Z]+')
#     print(new_list)
    
    
def create_final_json(new_list):
    
    """
    Create json object from list of elements

    :param new_list: List of elements to be merged.
    :return: Json object containing the required elements
    
    """
    
    import json
    if len(new_list) == 4:
        # Construct the JSON object
        json_object = {
            'Date': new_list[0],
            'Biller name': new_list[1],
            'Transaction number': new_list[2],
            'Amount': new_list[3]
        }
    elif len(new_list) == 3:
        # Construct the JSON object
        json_object = {
            'Date': new_list[0],
            'Biller name': new_list[1],
            'Transaction number': '',
            'Amount': new_list[2]  # Adjust the index to match the length of new_list
        }
    else:
        json_object = {}

    # Print the JSON object
    json_object = json.dumps(json_object, indent=4)
    
    return json_object


def main():
    
    
    # The following part is to download a file from a given url
    # Define the URL to download
    wget_url = os.environ["file_path"]
    # Create the 'data' directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Change the current working directory to 'data'
    os.chdir('data')

    # Get the current working directory
    CWD = os.getcwd()

    # Download the file from the URL
    response = requests.get(wget_url)
    file_name = wget_url.split('/')[-1]
    file_path = os.path.join(CWD, file_name)

    # Write the downloaded content to a file
    with open(file_path, 'wb') as file:
        file.write(response.content)

    # Iterate through all files in the current working directory
    for file in os.listdir(CWD):
        if file.endswith('.zip'):
            # Unzip the file
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(CWD)
                
    colour = os.environ["colour"]
    lower_bound, upper_bound = set_marker_colour(colour)
                
    extracted_file = get_extracted_region(file_path, lower_bound, upper_bound)
    
    final_json_object = extract_text_from_roi(extracted_file)
    
    print(final_json_object, "json objectttt")
    
if __name__ == "__main__":
    main()
    
    
# get the execution time
wall_et = time.time()
cpu_et = time.process_time()
execution_time = wall_et - wall_st

# get the cpu time
cpu_time = cpu_et - cpu_st
print('Execution time:', execution_time, 'seconds')
# print('Execution time :', execution_time/60, "minutes")
print('CPU time :',cpu_time, 'seconds')
