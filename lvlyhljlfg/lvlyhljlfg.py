from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.extensions.langchain import (
    WatsonxLLM,
)
import os
from dotenv import load_dotenv

load_dotenv()

generate_params = {GenParams.MAX_NEW_TOKENS: 25}

model = Model(
    model_id="meta-llama/llama-3-70b-instruct",
    credentials={"apikey": os.getenv("GA_API"), "url": os.getenv("GA_URL")},
    params=generate_params,
    project_id=os.getenv("PROJECT_ID"),
)

llm = WatsonxLLM(model=model)
from langchain.agents import Tool, initialize_agent
from langchain.chains import LLMMathChain

# CREATE TOOLS

math_chain = LLMMathChain.from_llm(llm=llm)

math_tool = Tool(
    name="Calci",
    func=math_chain.run,
    description="Useful for when you need to answer questions related to Math.",
)

tools = [math_tool]
agent = initialize_agent(
    agent="zero-shot-react-description",
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=3,
)

print(agent)
response = agent("What is (4*512)+152 ")
response
