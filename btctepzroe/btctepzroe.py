import re
import ast
import os

JSON_LIST = os.environ["json_list"]

def clean_summary_numbers(responses):
    '''this function cleans extracted numbers in json '''
    lens = [1 if len(response.split('{'))>1 else 0 for response in responses]
    responses=['{'+response.replace('\n','').replace('%','').split('{')[l].replace('null','"Null"').replace('Null','"Null"').replace('NULL','"Null"').replace('chang"','change"') for l,response in zip(lens,responses)]
    responses=[re.sub(r"([^'a-zA-Z+-.0-9% ])([a-zA-Z+-.0-9% ]+':)",r"\1'\2",response).replace("''","'") for response in responses]
    responses=[re.sub(r"(:'[a-zA-Z+-.0-9% ]+)([^'a-zA-Z+-.0-9% ])",r"\1'\2",response).replace("''","'") for response in responses]
    responses= [re.sub(r'([a-zA-Z+-.0-9% ]+":)([^"a-zA-Z+-.0-9% ])',r'\1"\2',response).replace('""','"') for response in responses]
    responses= [re.sub(r'([^"a-zA-Z+-.0-9% ])([a-zA-Z+-.0-9% ]+":)',r'\1"\2',response).replace('""','"') for response in responses]
    responses= [response.replace('" Null','"Null').replace("' Null","'Null").replace(' "Null','"Null').replace(" 'Null","'Null") for response in responses]
    responses= [response.replace('Null "','Null"').replace("Null '","Null'").replace('Null" ','Null"').replace("Null' ","Null'") for response in responses]
    responses=[response.replace('""','"').replace(''''"''','"').replace(""""'""",'"').replace("''","'") for response in responses]
    responses=[response.replace('$','').split('}')[0]+'}' for response in responses]
    
    responses=[re.sub(r'''([a-zA-Z]+)([ ]+)?"([\d%.+-]+)"''', r'\1":"\3"',response) for response in responses] # Change "-0.32"    
    responses=[re.sub(r'''([a-zA-Z]+):"([ ]+)?([\d%.+-]+)''', r'\1":\3',response) for response in responses] # Transcation:" +6.7  
    responses=[re.sub(r'''([\d%.+-]+),([ ]+)?"''', r'''\1",''',response) for response in responses]# moving comma to outside "8.96%,"
    
    responses=[re.sub(r'''([\d%.+-]+)([,]+)?([ ]+)?//or([ ]+)?([\d%+-]+|"Null")''', r'\5\2',(re.sub(r''':([ ]+)?,''', r':"Null",',response))) for response in responses]# remove //or "Null" | //or 2

    responses=[re.sub(r'''([\d%.+-]+)([ ]+)?"([a-zA-Z]+)''', r'''\1,"\3''',response) for response in responses]# mising comma
    responses=[re.sub(r'''([\d%.+-]+)"([ ]+)?"([a-zA-Z]+)''', r'''\1","\3''',response) for response in responses]# mising comma

    responses=[re.sub(r'([\d%.+-]+),([ ]+)?// or round\(([\d%.+-]+)\)',r'\3',(re.sub(r',([ ]+)?//([\^()/*\d%.+-]+)([,]+)?',r'\3',response))) for response in responses]# mising comma


    responses=[re.sub(r'''([a-zA-Z]+)([ ]+)?:([ ]+)?(['"\d%.+-]+)''', r'\1":\4',response) for response in responses] #Change : '-1.12 missing "
    responses=[re.sub(r''',([ ]+)?([a-zA-z])''', r',"\2',response) for response in responses]#, Transcation missing "

    responses=[re.sub(r''':([ ]+)?([-])"([\d%.+-]+)"''', r''':"-\3"''',response) for response in responses]#: -"8"
    responses=[re.sub(r''':([ ]+)?([+])"([\d%.+-]+)"''', r''':"\3"''',response) for response in responses]#: +"8.9"    
    responses=[re.sub(r""""([\d%.+-]+)'""",r'"\1"',response) for response in responses] # "-6.7%'
    responses=[re.sub(r''''([\d%.+-]+)"''', r"'\1'",response) for response in responses]    #  '7.7"
    responses=[re.sub(r''''([\d%.+-]+)([ ]+)?}''', r"'\1'}",response) for response in responses]    #  '7.7 }

    responses=[re.sub(r""":([ ]+)?([\d%.+-]+)([ ]+)?'""", r":'\2'",response) for response in responses]#: -16.89'
    
    
    responses=[re.sub(r''':([ ]+)?([\d%.+-]+)([ ]+)?"''', r": '\2'",response) for response in responses] # : 7.8"
    responses=[re.sub(r''',",([ ]+)?"''', r',"',response) for response in responses] # ,", "

    responses=[re.sub(r''':" ([\d%.+-]+)([,}])''', r':"\1"\2',response) for response in responses]#: "7.7 ,
    responses=[re.sub(r'''([\d%.+-]+)"([ ]+)?"([a-zA-Z]+)''', r'''\1","\3''',response) for response in responses]# mising comma

    responses=[response.replace('""','"').replace("''","'").replace(''''"''','"').replace(""""'""",'"') for response in responses]

    responses=[response.replace('//not provided in input','').replace('and',',').replace(';',',').replace('percent ','').replace('percent,',',').replace('.,',',').replace(',,',',').replace('Zero','0') for response in responses]
    responses=[ ast.literal_eval(response) for response in responses]
    return responses
    
responses=ast.literal_eval(JSON_LIST)
print(clean_summary_numbers(responses))    