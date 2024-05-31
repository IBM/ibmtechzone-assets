# Author: Pinkal Patel

'''
Title: Multi-Agent: Code Generation, Review, Execution, Test Case And Documentation
Description:
This Assest is describing usecase for code genration for complex problem using multi-agent with custome selection techinque and also collect final answer for user.
In this usecase, I have used 8 Agents.
Admin, Planner, Senior_Python_Engineer, Code_Executor, Code_Reviewer, Test_Cases_Writer, Code_Documentor, Society of Mind

Main Adavantage: Custome Agent Selection Technique and final answer collection

Step to Run:
Step 1: Run proxy_server.py  (command to run: python3 proxy_server.py --bearer_token {bam_apikey} --api_type bam --api_url https://bam-api.res.ibm.com/v2/text/generation)
Step 2: Run multi-agent.py

Note:
proxy_server.py file: Flask API to call Watsonx.AI Model. To use WatsonX.AI for llm model, one wrapper is written on top of this.

Library:
pip install pyautogen;
pip install flask
'''

import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, Agent
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
import subprocess
import sys
import time

seed_number = "4112"
config_list_code_reviewer = [
    {
    "api_type": "watsonx.ai",
    "base_url": "http://localhost:5432/v1",
    "api_key": "NULL",
    "model": "mistralai/mixtral-8x7b-instruct-v01"
    }
]

llm_config_code_reviewer = {"config_list": config_list_code_reviewer, "timeout": 60, "temperature": 0.8, "seed": seed_number,"cache_seed": seed_number}

config_list_code_writer = [
    {
    "api_type": "watsonx.ai",
    "base_url": "http://localhost:5432/v1",
    "api_key": "NULL",
    "model": "mistralai/mixtral-8x7b-instruct-v01" #"codellama/codellama-34b-instruct"
    }
]

llm_config_code_writer = {"config_list": config_list_code_writer, "timeout": 60, "temperature": 0.8, "seed": seed_number,"cache_seed": seed_number}


def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" in str(x.get("content", ""))[-11:].upper()

planner = autogen.AssistantAgent(
    name="Planner",
    system_message="""Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an Senior_Python_Engineer who can write code, a Code_Reviewer who doesn't write code but review the code, Code_Executor who can execute the code, Test_Cases_Writer who can write multiple testcase for the code and Code_Documentor who can document the final code.
Explain the plan first. Be clear which step is performed by a Senior_Python_Engineer, Code_Reviewer, Code_Executor,Test_Cases_Writer and Code_Documentor. Based on problem statement, planner can skip the agent. For example, user only ask sample code then do not need of Test_Cases_Writer, Code_Executor or Code_Reviewer.
""",
    llm_config=llm_config_code_reviewer,
)

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the Planner to discuss the plan for given problem statment. Plan execution needs to be approved by this admin. Once all task are completelly executed successfully, then club and pass all results as code, documentation and testcases to manager. If All task is done, stop the process.",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=termination_msg,
)

code_executor = UserProxyAgent(
    name="Code_Executor",
    system_message="You are a Code Executor. Execute the python code. You follow an approved plan.",
    human_input_mode="NEVER",
    #is_termination_msg=termination_msg,
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "/Users/pinkal/Documents/projects/multi-agent/temp",#"tasks",
        "use_docker": False,
        #"executor":LocalCommandLineCodeExecutor(work_dir="/Users/pinkal/Documents/projects/multi-agent/temp")
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    #default_auto_reply="Reply `TERMINATE` if the task is done.",
    description="Code Executor who can execute the code after review process is completed from Code Reviwer and call to boss",
)

coder = AssistantAgent(
    name="Senior_Python_Engineer",
    #is_termination_msg=termination_msg,
    system_message="You are a Senior Python Engineer, a specialist in writing succinct Python functions. You follow an approved plan.",
    llm_config=llm_config_code_writer,
    description="Senior Python Engineer who can write Python code as required and reiterates with feedback from the Code Reviewer.",
)

reviewer = AssistantAgent(
    name="Code_Reviewer",
    #is_termination_msg=termination_msg,
    system_message="You are a Code Reviewer, experienced in checking and review the code. You follow an approved plan. You don't write code but Review and provide feedback to the Senior Python Engineer until Code Reviewer is satisfied.",
    llm_config=llm_config_code_reviewer,
    description="Code Reviewer, reviews written code for correctness, efficiency, and security. Asks the Senior Python Engineer to address issues.",
)

code_documentor = AssistantAgent(
    name="Code_Documentor",
    #is_termination_msg=termination_msg,
    system_message="You're a seasoned Code Documentor, skilled in crafting clear, concise documentation using advanced natural language processing techniques. You follow an approved plan.",
    llm_config=llm_config_code_reviewer,
    description="Streamline Python code documentation effortlessly with our intelligent agent assistant. Empower developers to create clear, concise documentation with advanced natural language processing.",
)

test_cases_writer = AssistantAgent(
    name="Test_Cases_Writer",
    #is_termination_msg=termination_msg,
    system_message="You are a Test Cases Writer who can write unit tests in YAML format based on the code given by Senior Python Engineer. You follow an approved plan. Crafting Python test cases with precision and expertise to ensure comprehensive coverage of code functionality.",
    llm_config=llm_config_code_reviewer,
    description="Test Cases Writer, write the unit tests in YAML format based on code given by Senior Python Engineer.",
)

def _reset_agents():
    planner.reset()
    code_executor.reset()
    coder.reset()
    reviewer.reset()
    code_documentor.reset()
    test_cases_writer.reset()

def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat):
    """Define a customized speaker selection function.
    A recommended way is to define a transition for each speaker in the groupchat.

    Returns:
        Return an `Agent` class or a string from ['auto', 'manual', 'random', 'round_robin'] to select a default method to use.
    """
    messages = groupchat.messages

    if len(messages) <= 1:
        return planner
    else:
        return "auto"

def norag_chat(problem_statment):
    _reset_agents()
    groupchat = GroupChat(
        agents=[user_proxy ,planner, coder, reviewer, code_executor, test_cases_writer, code_documentor],
        messages=[],
        max_round=12,
        speaker_selection_method=custom_speaker_selection_func,
        #speaker_selection_method="round_robin",
        allow_repeat_speaker=False,
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config_code_reviewer)

    soc_mind_agent = SocietyOfMindAgent(
        "soc_mind_agent",
        chat_manager=manager,
        # human_input_mode="NEVER",
        llm_config= llm_config_code_reviewer
    )

    # Start chatting with the code_executor as this is the user proxy agent.
    user_proxy.initiate_chat(
        soc_mind_agent,
        message=problem_statment,
    )
    return soc_mind_agent
    

if __name__ == '__main__':
    bam_api_key = sys.argv[1]
    process = subprocess.Popen(["python3", "proxy_server.py","--bearer_token",bam_api_key,"--api_type","bam","--api_url","https://bam-api.res.ibm.com/v2/text/generation"])
    time.sleep(5)
    # Call Multi-agent for below problem statment
    PROBLEM = "Write a Python function for the Fibonacci sequence, the function will have one parameter for the number in the sequence, which the function will return the Fibonacci number for."
    soc_mind_agent = norag_chat(PROBLEM)
    for mess in soc_mind_agent.chat_messages.keys():
        content_dict = soc_mind_agent.chat_messages[mess]
        if content_dict[0]['role'] == 'user':
            print("============= Final Answer ===================== \n ",content_dict[1]['content'])
    process.terminate()