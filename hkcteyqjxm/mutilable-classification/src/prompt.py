tagger_prompt = """You are a automatic tagger, who tag multiple topics or single topic based on given context.

You must read the given context and consider each example for each topic and tag the given context to list of topics. You also provided with list of topics available as listed below and you should only be add to the tagging list from the given list of topics.

examples for each topic as below:
{example_for_topics}

Below is a simple example of how tagging should be done based on reading Input text:

Input:
YOUR INPUT GOES HERE

Output:
['SAMPLE CLASS 1','SAMPLE CLASS 2']

Below is example based on exceptions:

Input:
YOUR INPUT GOES HERE

Output:
['SAMPLE CLASS 1','SAMPLE CLASS 2']

Input:
YOUR INPUT GOES HERE

Output:
['SAMPLE CLASS 1','SAMPLE CLASS 2']

Input:
YOUR INPUT GOES HERE

Output:
['SAMPLE CLASS 1','SAMPLE CLASS 2']

Input:
YOUR INPUT GOES HERE

Output:
['SAMPLE CLASS 1','SAMPLE CLASS 2']

Input:
YOUR INPUT GOES HERE

Output:
['SAMPLE CLASS 1','SAMPLE CLASS 2']

{reiterate}

Input:
{input}

Output:"""

topic_specific_prompt="""You are a summary writer for a given topic by using given context.

You will be provided with two context such as main context and child context. You have to read the main context throughly then read each child context with higher precedence given to main context text. The top most precedence provided to the main context. Generate the next possible step with respect to given topic and summarise entire content in one or two sentences.

Good example of generating description as follows:

MAIN CONTEXT:
PROVIDE YOUR MAIN CONTEXT HERE


CHILD CONTEXT 1 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 2 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 3 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 4 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 5 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 6 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 7 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 8 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 9 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 10 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 11 : 
CHILD CONTEXT GOES HERE


CHILD CONTEXT 12 : 
CHILD CONTEXT GOES HERE

OUTPUT DESCRIPTION FOR TOPIC :
SAMPLE OUTPUT HERE


OUTPUT DESCRIPTION FOR CLASS_NAME_GOES_HERE :
SAMPLE_OUTPUT

Your task is to read below MAIN CONTEXT and all subsequent CHILD CONTEXT and then extract the text which are relevant to {topic} in a summarized manner

MAIN CONTEXT:
{main_context}

{child_contexts}

Generate rephrased meaningful text for the {topic} as output. The output should be three sentences in a summarized and rephrased manner. Generate the meaningful and semantically similar text for the {topic} based on given MAIN CONTEXT as showed in above examples

OUTPUT DESCRIPTION FOR {topic} :

"""
