# Author: Pinkal Patel
'''
Title:
Multi-Processing Call to WatsonX.AI

Description:
This code shows how to do multiple parallel calls to watsonx.ai as multiprocessing

Dependecy: pip install ibm_watson_machine_learning

.env file having the below content:
API_KEY=
IBM_CLOUD_URL=https://us-south.ml.cloud.ibm.com
PROJECT_ID=
'''
from watson_ai_api import get_watson_ai_output
import concurrent.futures
import time
import sys

start = time.perf_counter()
transcript_batch = ["\nSpeaker0: \nSpeaker1: hey there i hope you're doing well myself neha i'm from jaipur i need to get something sorted out with my credit card so i have lost it and i'm pretty worried about someone using it without my knowledge could you please block it as soon as \nSpeaker0: possible what is your credit card number \nSpeaker1: my credit card number is four one five three zero zero nine nine two one five nine \nSpeaker0: what is your aadhaar card number my aadhaar card \nSpeaker1: number is two one five nine zero zero nine nine two one five five \nSpeaker0: can i get your phone number \nSpeaker1: my phone number is eight nine nine nine five one three five one three \nSpeaker0: and your email address my email address "]

output_dict = {}
with concurrent.futures.ProcessPoolExecutor() as executor:
   output = dict((executor.submit(get_watson_ai_output,trascript),trascript) for trascript in transcript_batch)
   for output_fun in concurrent.futures.as_completed(output):
      query = output[output_fun]
      output_dict[query] = output_fun.result()
      #print("input ===> ",query)
      #print("output ===> ",output_fun.result())
finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2)} second(s)')
 
for trascript in transcript_batch:
   print("==> \n ",output_dict[trascript])