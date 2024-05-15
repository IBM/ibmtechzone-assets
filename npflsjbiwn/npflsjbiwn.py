import os
class caseDict(object):

    #Here you can add your old pseudocode
    older_version_Pseudocode=os.environ["SAMPLE_PSEUDOCODE"]

    #Here you can add your old java code
    older_version_Java_Code=os.environ["SAMPLE_JAVA_CODE"]

    #Here you can add your new pseudocode
    New_version_Pseudocode=os.environ["NEW_PSEUDOCODE"]

    #Prompt for java code generation based on the provided pseudocode.
    prompt_input = f"""Input: You are an excellent agent focused on creating accurate and efficient Java code. Consider the provided older version of pseudocode, older version of javacode as a example. Generate the New version Java code according to New version Pseudocode. New version java code must be compatible with stable JDK(java development version) version. Generated New version Java code must contain the updated logic made in the New version Pseudocode. 
    ***IMPORTANT CONDITIONS AND STEPS TO FOLLOW IN NEW VERSION JAVA CODE GENERATION PROCESS :
    1. Required to generate the code without object oriented programming concepts. Only code snippet is required.
    2. First Understand the older version pseudocode and its corresponding older version of javacode then compare the New version Pseudocode with older version Pseudocode. Strictly consider the updation made in New version Pseudocode.
    3. You must use the same parameter names for the java function call which was mention in the older version Java Code. 
    4. You may use the same variable names of older version Java Code in New version Java code.
    5. The changes made in the new version Java code must be included in the New version Java code.
    6. Use the IF condition validation like written in older version Java Code.
    7. Use the English translated variable names from the Japanese written New version Pseudocode.
    8. Use StringUtil.isBlank java in-built method to validate that the variable whether it contains whitespace character or not.

    older version Pseudocode:
    {older_version_Pseudocode}

    older version Java Code:
    {older_version_Java_Code}

    New version Pseudocode: 
    {New_version_Pseudocode:}

    New version Java code:

    Output:"""

    