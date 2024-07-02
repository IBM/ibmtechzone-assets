import os
from crewai import Crew, Task, Agent, Process
from crewai_tools import tool
from langchain_ibm import WatsonxLLM
from langchain.agents import Tool, load_tools
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
load_dotenv()
os.environ["WATSONX_APIKEY"] = os.getenv("WATSONX_APIKEY")
# Parameters
parameters = {"decoding_method": "greedy", "max_new_tokens": 500}
# Create the first LLM
llm = WatsonxLLM(
    model_id="meta-llama/llama-3-70b-instruct",
    url=os.getenv("WATSONX_URL"),
    params=parameters,
    project_id=os.getenv("PROJECT_ID"),
)
# Create the function calling llm
function_calling_llm = WatsonxLLM(
    model_id="ibm-mistralai/merlinite-7b",
    url=os.getenv("WATSONX_URL"),
    params=parameters,
    project_id=os.getenv("PROJECT_ID"),
)
@tool("DuckDuckGoSearch")
def search(search_query: str):
    """Search the web for information on a given topic**"""
    return DuckDuckGoSearchRun().run(search_query)


# Create the agent
researcher = Agent(
    llm=llm,
    function_calling_llm=function_calling_llm,
    role="Senior AI Researcher",
    goal="Find promising research in the field of quantum computing.",
    backstory="You are a veteran quantum computing researcher with a background in modern physics.",
    allow_delegation=False,
    tools=[search],
    verbose=1,
)

# Create a task
task1 = Task(
    description="Search the internet and find 5 examples of promising AI research.",
    expected_output="A detailed bullet point summary on each of the topics. Each bullet point should cover the topic, background and why the innovation is useful.",
    output_file="task1output.txt",
    agent=researcher,
)

# Create the second agent
writer = Agent(
    llm=llm,
    role="Senior Speech Writer",
    goal="Write engaging and witty keynote speeches from provided research.",
    backstory="You are a veteran quantum computing writer with a background in modern physics.",
    allow_delegation=False,
    verbose=1,
)

# Create a task
task2 = Task(
    description="Write an engaging keynote speech on quantum computing.",
    expected_output="A detailed keynote speech with an intro, body and conclusion.",
    output_file="task2output.txt",
    agent=writer,
)

# Put all together with the crew
crew = Crew(agents=[researcher, writer], tasks=[task1, task2], verbose=1)
print(crew.kickoff())