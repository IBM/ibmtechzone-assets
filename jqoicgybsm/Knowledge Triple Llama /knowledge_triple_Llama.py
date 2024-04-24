import os
import networkx as nx
from pyvis.network import Network
import gradio as gr
from typing import Any, List, Mapping, Optional, Union, Dict
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.graphs.networkx_graph import KG_TRIPLE_DELIMITER
from langchain.llms.base import LLM
from langchain.llms.base import LLM 
from pyvis.network import Network

from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

#config Watsonx.ai environment
from typing import Dict, Optional, List, Any

class EnvSetup:
    def __init__(self):
        self.api_key = os.environ("API_KEY", None)
        self.ibm_cloud_url = os.environ("IBM_CLOUD_URL", None)
        self.project_id = os.environ("PROJECT_ID", None)
        self.creds = None

        if not all([self.api_key, self.ibm_cloud_url, self.project_id]):
            print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
        else:
            self.creds = {
                "url": self.ibm_cloud_url,
                "apikey": self.api_key
            }

class WatsonXModel:
    def __init__(self, creds: Dict[str, str], project_id: str):
        self.creds = creds
        self.project_id = project_id
        self.params = {
            "decoding_method": "sample",
            "min_new_tokens": 1,
            "max_new_tokens": 100,
            "random_seed": 42,
            "temperature": 0.5,
            "top_k": 50,
            "top_p": 1
        }
        self.model_id = 'meta-llama/llama-2-70b-chat'
        self.model = Model(model_id=self.model_id, params=self.params, credentials=self.creds, project_id=self.project_id)

    def generate_text(self, prompt: str) -> str:
        return self.model.generate_text(prompt)

class KnowledgeGraphGenerator:
    def __init__(self, model: WatsonXModel):
        self.model = model
        self.knowledge_triple_extraction_template = """
    "You are a networked intelligence helping a human track knowledge triples"
    " about all relevant people, things, concepts, etc. and integrating"
    " them with your knowledge stored within your weights"
    " as well as that stored in a knowledge graph."
    " Extract all of the knowledge triples from the text."
    " A knowledge triple is a clause that contains a subject, a predicate,"
    " and an object. The subject is the entity being described,"
    " the predicate is the property of the subject that is being"
    " described, and the object is the value of the property.\n\n"
    "EXAMPLE\n"
    "It's a state in the US. It's also the number 1 producer of gold in the US.\n\n"
    f"Output: (Nevada, is a, state){KG_TRIPLE_DELIMITER}(Nevada, is in, US)"
    f"{KG_TRIPLE_DELIMITER}(Nevada, is the number 1 producer of, gold)\n"
    "END OF EXAMPLE\n\n"
    "EXAMPLE\n"
    "I'm going to the store.\n\n"
    "Output: NONE\n"
    "END OF EXAMPLE\n\n"
    "EXAMPLE\n"
    "Oh huh. I know Descartes likes to drive antique scooters and play the mandolin.\n"
    f"Output: (Descartes, likes to drive, antique scooters){KG_TRIPLE_DELIMITER}(Descartes, plays, mandolin)\n"
    "END OF EXAMPLE\n\n"
    "EXAMPLE\n"
    "{text}"
    "Output:"
        """

    def extract_knowledge_triples(self, text: str) -> str:
        prompt = self.knowledge_triple_extraction_template.format(text=text)
        return self.model.generate_text(prompt)

    def parse_triples(self, response: str, delimiter=';') -> List[str]:
        if not response:
            return []
        return response.split(delimiter)

    def create_graph_from_triplets(self, triplets: List[str]):
        G = nx.DiGraph()
        for triplet in triplets:
            subject, predicate, obj = triplet.strip().split(',')
            G.add_edge(subject.strip(), obj.strip(), label=predicate.strip())
        return G

    def visualize_graph(self, graph: nx.DiGraph) -> str:
        pyvis_network = Network(notebook=True, height="600px", width="100%", bgcolor="#222222", font_color="white")
        for node in graph.nodes():
            pyvis_network.add_node(node)
        for edge in graph.edges(data=True):
            pyvis_network.add_edge(edge[0], edge[1], label=edge[2]["label"])
        pyvis_network.show_buttons(filter_=['physics'])
        pyvis_network.save_graph("graph.html")
        return "graph.html"

# Example usage
env = EnvSetup()
if env.creds:
    model = WatsonXModel(creds=env.creds, project_id=env.project_id)
    kg_generator = KnowledgeGraphGenerator(model=model)
    text = "The city of Paris is the capital and most populous city of France. The Eiffel Tower is a famous landmark in Paris."
    triples_response = kg_generator.extract_knowledge_triples(text)
    triplets = kg_generator.parse_triples(triples_response)
    graph = kg_generator.create_graph_from_triplets(triplets)
    graph_html = kg_generator.visualize_graph(graph)

    def serve_graph():
        return graph_html

    demo = gr.Interface(fn=serve_graph, outputs="html", title="Knowledge Graph Visualization")
    demo.launch()
