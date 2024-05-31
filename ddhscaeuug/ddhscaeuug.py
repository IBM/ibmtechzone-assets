import xml.etree.ElementTree as ET
import pandas as pd
import getpass
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
import os
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
import pandas as pd
import xml_to_sql_input_prep
import gc
from tqdm import tqdm
from ibm_watsonx_ai.foundation_models import ModelInference
# Load and parse the XML file
tree = ET.parse('m_CrDbStatsment.xml')

instructions_to_model1_df=pd.DataFrame([['Source Qualifier','''Three inputs are provided source, destination and connection list. 
    Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
    Mention the appropriate transformation on columns using information available in destination. 
    If datatype is changing from source to destination then perform sql cast operation for data type conversion.
    Replace IIF functions with case sql clause.
    The output should be a set of instruction to generate sql query used for text to sql conversion application. 
    Provide concise instructions. The generated text should give source name, destination name, and transformation applied on each columns. 
    No other details should be mentioned. Output structure should be like Fetch data from source to create temp view destination with following transformations:
    "source_name.column name" "transformation"...''',
    "generate sql query to create view based on instructions. Remove \ character from output."],
   [ 'Expression','''Three inputs are provided source, destination and connection list. 
    Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
    Mention the appropriate transformation on columns using information available in destination. 
    If datatype is changing from source to destination then perform sql cast operation for data type conversion.
    Replace IIF functions with case sql clause.
    The output should be a set of instruction to generate sql query used for text to sql conversion application. 
    Provide concise instructions. The generated text should give source name, destination name, and transformation applied on each columns. 
    No other details should be mentioned. Output structure should be like Fetch data from source to create temp view destination with following transformations:
    "source_name.column name" "transformation"...''',
    "generate sql query to create view based on instructions. Remove \ character from output."],
    ['Aggregator',"""Three inputs are provided source, destination and connection list. 
    Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
    Mention the appropriate transformation on columns using information available in destination. 
    If datatype is changing from source to destination then perform sql cast operation for data type conversion.
    The output should be a set of instruction to generate sql query used for text to sql conversion application. 
    Provide concise instructions. The generated text should give source name, destination name, and transformation applied on each columns. 
    No other details should be mentioned. 
    If TYPE ="Aggregator" THEN PERFORM GROUP BY ON ALL COLUMNS WITH PORTYPE="INPUT/OUTPUT" and transformation name is GROUP BY.
    Output structure should be like Fetch data from source to create temp view destination with following transformations:
    "source_name.column name" "transformation name""","generate sql query to create view based on instructions. Use PARTITION BY clause in select IF GROUPBY not in n-1 columns"],
    ['Sorter',"""Three inputs are provided source, destination and connection list. 
    Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
    Mention the appropriate transformation on columns using information available in destination. 
    Select column where OUTPUT is mentioned in PORTTYPE
    The output should be a set of instruction to generate sql query used for text to sql conversion application. 
    Provide concise instructions. Generate less token if all relevant information is extracted
    Do not add \ within names
    refer EXPRESSION in TRANSFORMFIELD tag for value
    if TYPE ="Sorter" and ISSORTKEY ="YES" then use order by clause on these columns based SORTDIRECTION in sequence of their occurence
    Output structure should like Fetch data from source to create temp view destination with following transformations:
    { column name : data type : value }
    Example:
    Input: 
    <TRANSFORMFIELD DATATYPE ="string" DEFAULTVALUE ="" DESCRIPTION ="" ISSORTKEY ="YES" NAME ="a" PICTURETEXT ="" PORTTYPE ="INPUT/OUTPUT" PRECISION ="20" SCALE ="0" SORTDIRECTION ="ASCENDING"/>
    <TRANSFORMFIELD DATATYPE ="string" DEFAULTVALUE ="" DESCRIPTION ="" ISSORTKEY ="YES" NAME ="b" PICTURETEXT ="" PORTTYPE ="INPUT/OUTPUT" PRECISION ="20" SCALE ="0" SORTDIRECTION ="DESCENDING"/>     
    <TRANSFORMFIELD DATATYPE ="string" DEFAULTVALUE ="" DESCRIPTION ="" ISSORTKEY ="NO" NAME ="c" PICTURETEXT ="" PORTTYPE ="INPUT/OUTPUT" PRECISION ="20" SCALE ="0" SORTDIRECTION ="ASCENDING"/>   
    <TRANSFORMFIELD DATATYPE ="string" DEFAULTVALUE ="" DESCRIPTION ="" ISSORTKEY ="YES" NAME ="d" PICTURETEXT ="" PORTTYPE ="INPUT/OUTPUT" PRECISION ="20" SCALE ="0" SORTDIRECTION ="ASCENDING"/>     
    Output: Fetch data from table source to create temp view destination with following transformations:
    column a : string : order by ASCENDING
    column b: string : order by DESCENDING
    column c: string : no sort
    column d: string : order by ASCENDING
    Input:
    <TRANSFORMFIELD DATATYPE ="string" DEFAULTVALUE ="" DESCRIPTION ="" ISSORTKEY ="NO" NAME ="a" PICTURETEXT ="" PORTTYPE ="INPUT/OUTPUT" PRECISION ="20" SCALE ="0" SORTDIRECTION ="ASCENDING"/>        
    Output: 
    Fetch data from table source to create temp view destination with following transformations:
    column a: string: no sort""",
    'Generate a sql query for sorting data to create view based on instructions. Use order by information to sort'],
   [ 'Union Transformation',"""Three inputs are provided source, destination and connection list. 
    Source will have multiple components used to perform union operation based on GROUP value.
    Only select those columns where PORTTYPE containg OUTPUT value.
    Write the text that describes the union happening between source tables to generate destination table. 
    IF TEMPLATENAME = "Union Transformation" then tables will be added by union clause. 
    Output structure should like:
    Fetch data from source: source1, source2, ..., sourcen to create temp view destination with following transformation:
    "source.column name" "column level transformation name""",
    "Generate a sql query to create view based on instructions. Use union by clause to add table data"],
    ['Joiner',""" Three inputs are provided source, destination and connection list. 
    Source will have two components source1 and source2. source1 and source2 can be inferred from distinct connector FROMINSTANCE
    Write the text that describes the join happening between source tables to generate destination table. 
    IF TYPE ="Joiner" then two table will be joined. 
    <TABLEATTRIBUTE NAME ="Join Condition" will provide information about joining condition.
    <TABLEATTRIBUTE NAME ="Join Type" will provide information about joining type.
    Refer PORTTYPE ="INPUT/OUTPUT/MASTER" to know which table is master table
    Output structure should like:
    Fetch data from source: source1 and source2 to create temp view destination with following join conditions:
    source1 {join Type} source2
    {join condition}
    column transformations: {source.column name} {transformation}""",
    'generate sql query to create view based on instructions.'
    ],
    ['Filter',""" Three inputs are provided source, destination and connection list. 
    Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
    Mention the appropriate transformation on columns using information available in destination. 
    Fetching filter condition is important.
    Refer VALUE attribute of tag <TABLEATTRIBUTE NAME ="Filter Condition" for filter condition
    The output should be a set of instruction to generate sql query used for text to sql conversion application. 
    Output structure should be like Fetch data from source to create temp view destination with following where condition and transformations:
    {filter condition}
    column transformations: {source.column name} {transformation}""",
    " generate sql query to create view based on instructions. generate sql query with correct where condition"],
    ["to_lookup","""Three inputs are provided source, destination and connection list. 
Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
Mention the appropriate transformation on columns using information available in destination. 
If  <TABLEATTRIBUTE NAME ="Lookup Sql Override" is provided the text followed by VALUE = should be in the output
The output should be a set of instruction to generate sql query used for text to sql conversion application. 
Provide concise instructions. Generate less token if all relevant information is extracted
Output structure should like Fetch data from source to create temp view destination with following transformations:
{column name : data type : transformation}
""","""generate sql query to create view based on instructions.
create destination table view from cobimation of source and loopup sql override.
The lookup sql override is used to populate column mentioned under text Perform lookup on destinatio
Join source with sql override query and rename column of sql override query from lookup table name information
"""],
['from_lookup',"""  Three inputs are provided source, destination and connection list. 
    Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
    Mention the appropriate transformation on columns using information available in destination. 
    Select column where OUTPUT is mentioned in PORTTYPE
    The output should be a set of instruction to generate sql query used for text to sql conversion application. 
    Provide concise instructions. Generate less token if all relevant information is extracted
    Do not add \ within names
    refer EXPRESSION in TRANSFORMFIELD tag for value
    Output structure should like Fetch data from source to create temp view destination with following transformations:
    { column name : data type : value }
    Example:
    Input: <TRANSFORMFIELD DATATYPE ="bigint" DEFAULTVALUE ="ERROR(&apos;transformation error&apos;)" DESCRIPTION ="" EXPRESSION ="DECODE(UPPER(TIME_BCKT_PERD_TYP),&#xD;&#xA;&apos;CURR&apos;,TRX,0)" EXPRESSIONTYPE ="GENERAL" NAME ="CURR_TRX" PICTURETEXT ="" PORTTYPE ="OUTPUT" PRECISION ="19" SCALE ="0"/>
    Output: Fetch data from source to create temp view destination with following transformations:
    Output: CURR_TRX : bigint : case when UPPER(TIME_BCKT_PERD_TYP)='CURR' THEN TRX ELSE 0 END CASE
    Input: <TRANSFORMFIELD DATATYPE ="string" DEFAULTVALUE ="" DESCRIPTION ="" EXPRESSION ="CURR_TRX" EXPRESSIONTYPE ="GENERAL" NAME ="CURR_TRX" PICTURETEXT ="" PORTTYPE ="INPUT/OUTPUT" PRECISION ="20" SCALE ="0"/>
    Output: Fetch data from source to create temp view destination with following transformations:
    CURR_TRX : bigint : CURR_TRX
    Input: <TRANSFORMFIELD DATATYPE ="string" DEFAULTVALUE ="" DESCRIPTION ="" EXPRESSION ="BRAND_ID" EXPRESSIONTYPE ="GENERAL" NAME ="BRAND_ID" PICTURETEXT ="" PORTTYPE ="INPUT/OUTPUT" PRECISION ="20" SCALE ="0"/>
    Output:""",
    "generate sql query to create view based on instructions."]
])
if __name__=='__main__':
    map_seq=0
    root = tree.getroot()
    # Find the SOURCE element
    source = root.findall('.//SOURCE')[map_seq]

    # Get a string representation of the SOURCE element
    source_str = ET.tostring(source, encoding='unicode')
    source_name = source.attrib['NAME']
    target = root.findall('.//TARGET')[map_seq]
    # Get a string representation of the SOURCE element
    target_str = ET.tostring(target, encoding='unicode')
    target_name = target.attrib['NAME']

    # Find the MAPPING element
    transformations = root.findall('.//MAPPING/TRANSFORMATION')#[map_seq]
    transformations_list=[]
    transformation_type_list=[]
    for transformation in transformations:
        name=transformation.attrib['NAME']
        tr_type=transformation.attrib['TYPE']
        if "custom" in tr_type.lower():
            tr_type=transformation.attrib['TEMPLATENAME']
        transformation_str = ET.tostring(transformation, encoding='unicode')
        transformations_list.append({name:transformation_str})
        transformation_type_list.append([tr_type,name])

    # Find the MAPPING element
    mappings=root.findall('.//MAPPING')
    connectors = mappings[map_seq].findall('./CONNECTOR')

    connectors_list=[]
    connectors_list_1=[]
    for connector in connectors:
        from_instance=connector.attrib['FROMINSTANCE']
        to_instance=connector.attrib['TOINSTANCE']
        connector_str = ET.tostring(connector, encoding='unicode')
        connectors_list.append({from_instance:[connector_str,to_instance]})
        connectors_list_1.append({to_instance:[connector_str,from_instance]})

    curr_instance=source_name
    instance_order={}
    for item in connectors_list_1:
        for key in item.keys():
            if key in instance_order.keys():
                if list(item.values())[0][1] not in instance_order[key]:
                    instance_order[key].append(list(item.values())[0][1])
            else:
                instance_order[key]=([list(item.values())[0][1]])


    instance_order_name=source_name
    order=1
    transformation_type=[]
    instance_order_new={}
    instance_order_flag={}
    for key in instance_order.keys():
        instance_order_flag[key]=False
    instance_order_source_name_list=[]
    for key in instance_order.keys():
        if instance_order[key][0]==instance_order_name:
            instance_order_new[order]={key:instance_order[key]}
            order+=1
            instance_order_flag[key]=True
            instance_order_source_name_list.append(key)
    #print('instance_order_source_name_list',instance_order_source_name_list)
    for instance_order_name in instance_order_source_name_list:
            for key in instance_order.keys():
                if instance_order_name in instance_order[key] and sum([0 if instance_order_flag[i] ==True else 1 for i in instance_order[key] ])==0:
                    #print(instance_order_name)
            
                    instance_order_new[order]={key:instance_order[key]}
                    order+=1
                    for key_ in instance_order:
                        if instance_order_name in instance_order[key_] and  sum([0 if instance_order_flag[i] ==True else 1 for i in instance_order[key_] ])==0 and key!=key_:
                            #instance_order[key_].append(order)
                            instance_order_new[order]={key_:instance_order[key_]}
                            order+=1
                            instance_order_flag[key_]=True


                    
                    instance_order_name=key
                    instance_order_flag[key]=True
                    #print(instance_order_flag)
    while False in instance_order_flag.values():
        for key in instance_order.keys():
                if instance_order_name in instance_order[key] and sum([0 if instance_order_flag[i] ==True else 1 for i in instance_order[key] ])==0:
                    #print(instance_order_name)
            
                    instance_order_new[order]={key:instance_order[key]}
                    order+=1
                    for key_ in instance_order:
                        if instance_order[key][-1] in instance_order[key_] and key!=key_:
                            #instance_order[key_].append(order)
                            instance_order_new[order]={key_:instance_order[key_]}
                            order+=1
                            instance_order_flag[key_]=True


                    
                    instance_order_name=key
                    instance_order_flag[key]=True
                    #print(instance_order_flag)
                    #print('next',instance_order_name)
        
            
        
    instance_order_new
    #instance_order_flag
                

    llm_inputs=[]
    # curr_source=source_name

    curr_destination=[]
    for item in sorted(instance_order_new.keys()):
        curr_source=[]
        for source_item in list(instance_order_new[item].values())[0]:
            if source_item==source_name:
                curr_source.append(source_str)
            else:
                curr_source.append([i[source_item] for i in transformations_list if list(i.keys())[0]==source_item][0])
        if target_name == list(instance_order_new[item].keys())[0] :
            #print(1)
            
            curr_destination_str=target_str
        else:
            curr_destination_str=[list(i.values())[0] for i in transformations_list if list(i.keys())[0]==list(instance_order_new[item].keys())[0]][0]
        #print('here',item,list(instance_order_new[item].keys()))
        if target_name == list(instance_order_new[item].keys())[0] :
            
            curr_connection_list=[target_str]
        else:
            #print(2)
            
            #print('ri')
            curr_connection_list=[list(i.values())[0][0] for i in connectors_list_1 if list(i.keys())[0]==list(instance_order_new[item].keys())[0]]
            # if (list(instance_order_new[item].keys())[0])=='union':
            #     print(list(instance_order_new[item].keys())[0])
            #     print(curr_connection_list)
            #     print([i for i in connectors_list_1 if 'union' in i.keys()][0])
        
        
        llm_inputs.append([curr_source,curr_destination_str,curr_connection_list])


    instruction = """Three inputs are provided source, destination and connection list. 
    Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
    Mention the appropriate transformation on columns using information available in destination. 
    If Template name is union then input tables will be combined by UNION SQL clause.
    IF PORTTYPE ="OUTPUT" then sql query might drop some of the input columns or it might rename some of the columns or it might group by on input columns.
    For renaming refer to FIELDDEPENDENCY tag
    for grouping refer GROUP tag
    The output should be a set of instruction to generate sql query used for text to sql conversion application. 
    Treat all columns of source as string. Provide concise instructions. The generated text should give source name, destination name, and transformation applied on each columns. 
    No other details should be mentioned. Output structure should like Fetch data from source name to create temp view destination name with following transformations:{column name} {transformation}...
    If TABLEATTRIBUTE NAME ="Sql Query" is provided then output should only be sql query in VALUE 
    """

    question_list=[]
    for i in llm_inputs:
        question = f"""
        source:
        {str(i[0])}
        destination:
        {str(i[1])}
        connection_list:
        [{str(i[2])}
        Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation. 
        The generated text should give source name, destination name, and transformation applied on each columns. 
        Mention the appropriate transformation on columns using information available in destination. 
        If TABLEATTRIBUTE NAME ="Sql Query" is provided then output should only be sql query in VALUE """
        question_list.append(question)

    instructions_df=instructions_to_model1_df.rename(columns={0:'transformation_type',1:"instructions_to_model1",2:'instructions_to_model2'})

    transformation_type_list.append(['Target',target_name])

    transformation_name=[list(i.keys())[0] for i in instance_order_new.values()]
    transformation_type_df=pd.DataFrame(transformation_type_list).rename(columns={0:'transformation_type',1:'transformation_name'})

    llm_inputs=pd.DataFrame(question_list)
    llm_inputs.rename(columns={0:'xml_content'},inplace=True)
    llm_inputs['transformation_name']=[i.split('destination:')[1].split('NAME=')[1].split(' ')[0][1:-1] for i in llm_inputs['xml_content']]
    # df1.rename(columns={'question':'xml_content'},inplace=True)
    #df1['transformation_name']=transformation_name
    llm_inputs=llm_inputs.merge(transformation_type_df,on='transformation_name')
    llm_inputs=llm_inputs.merge(instructions_df,on='transformation_type')
    #df1.to_excel('inputs_for_code_conversion.xlsx')
    
    credentials = {
        "url": os.environ['url'],
        "apikey": os.environ['apikey']
    }
    
    project_id = os.environ["project_id"]
    model_id = os.environ["model_id"]
    
    parameters = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 800,
        GenParams.STOP_SEQUENCES: ["<end·of·code>"]
    }
    
    
    model = ModelInference(
        model_id=model_id, 
        params=parameters, 
        credentials=credentials,
        project_id=project_id)
    
    if __name__=='__main__':
        xml_to_sql_input_prep.prep_input()
        llm_outputs=llm_inputs[:1].copy()
        sql_text_list=[]
        for item in tqdm(llm_inputs[:1].iterrows()):
            try:
                # print()#3,item['question'])
                result = model.generate_text(" ".join([item[1]['instructions_to_model1'],item[1]['xml_content'], ]))
                result = model.generate_text(" ".join([item[1]['instructions_to_model2'],result]))
                #print(result)
                sql_text_list.append(result)
                gc.collect()
            except Exception as e:
                print(e)
        llm_outputs['sql_code']=sql_text_list
        llm_outputs.to_excel('code_conversion_output.xlsx')


