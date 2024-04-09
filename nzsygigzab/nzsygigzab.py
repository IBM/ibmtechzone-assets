import pandas as pd
import numpy as np
import io

from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os
import json
import pdfkit
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
# Create custom fonts for bold and italic
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from collections import defaultdict
import re


string = os.environ["transcript"]



vttlist = string.split('\n')
newvtt = [i for i in vttlist if i]

# Need to remove "<v" and replace ">" with ":"

cleaned_list = []


alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
'n','o','p','q','r','s','t','u','v','w','x','y','z','A','B',
'C','D','E','F','G','H', 'I', 'J','K','L','M','N','O','P','Q','R',
'S','T','U','V','W','X','Y','Z']


for x in newvtt:
    
    if x.startswith("<v") == True:
        remove_v = x.strip("<v ")
        cleaned_v = remove_v.replace(">", ": ")
        cleaned_list.append(cleaned_v)
    else:
        if x[0] in alphabet:
            cleaned_list.append(x)

#drop first item of test list because it just says "WEBVTT"
cleaned_list.pop(0)
        


#Cleaning for one off lines with no speaker in front
#removing \r to prevent issues when merging lines into chunks
for i in range(0,len(cleaned_list)):
    test = cleaned_list[i].split(': ', 1)
    cleaned_list[i] = cleaned_list[i].replace("\r", "")
    if len(test)==1:
        try:
            cleaned_list[i-1] = cleaned_list[i-1] + " " + cleaned_list[i]
        except:
            continue

cleaned_list_final = [x for x in cleaned_list if len(x.split(': ', 1))>1]


###Speak in one chunk if speaker appears multiple times in a row
#If some lines already don't contain speaker, strs so deal wit hthose before

final_output = []
current_name = ''
speaker_str = ''

for line in cleaned_list_final:
    spl = line.split(': ', 1)
    #print(spl)
    #print('#######')
    if spl[0] != current_name:
        #print("spl [0]; ", spl[0])
        final_output.append(speaker_str)
        #print(final_output)
        speaker_str = line
        current_name = spl[0]
    elif spl[0] == current_name:
        speaker_str = speaker_str + " " + spl[1]


# #removed first item in list which is '' since first speaker_str is ''
final_output.pop(0)


# Clean same words appearing 2x in row

final_no_dupes = []

regex = r'\b(\w+)(?:\W+\1\b)+'

for f in final_output:
    no_dupes = re.sub(regex, r'\1', f, flags=re.IGNORECASE)

    final_no_dupes.append(no_dupes)
    

# Create one whole doc from all the strings
#whole_doc = ' '.join(str(c) + ' ' for c in clean_clean)
whole_doc = '\n'.join(line for line in final_no_dupes) # clean_clean  # adding "\n" helps with chunking
print(whole_doc)