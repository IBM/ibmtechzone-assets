import os
import yaml
from dotenv import load_dotenv
from genai.model import Credentials
from utils.classes import RagModel
from utils.templates import JD_TEMPLATE
from unstructured.partition.pdf import partition_pdf



model1 = RagModel()

load_dotenv()
api_key = os.getenv("BAM_API_KEY", None)
api_endpoint = os.getenv("BAM_URL", None)

if api_key is None or api_endpoint is None:
    print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
else:
    creds = Credentials(api_key=api_key, api_endpoint=api_endpoint)

def process_jd(jd_summary):
    prompt2 = JD_TEMPLATE.format(jd_summary=jd_summary)
    model_output = model1.send_to_watsonxai_cus(prompts=[prompt2])
    model_output_str = model_output.replace("<EOP>", "") 
    print(model_output_str)
    return (model_output_str)

def process_resumes(folder_path):
    model_outputs = []
    # Loop over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            print(filename)
            
            pdf_text = partition_pdf(filename=os.path.join(folder_path, filename))
            pdf_text = "\n\n".join([str(el) for el in pdf_text])
            print(pdf_text)

    with open('candidates.yaml', 'w') as yaml_file:
            yaml.dump(model_outputs, yaml_file, default_flow_style=False)


jd_text = """
Job Title: Data Scientist
Company: XYZ Tech Solutions
Location: San Francisco, CA
About Us:
At XYZ Tech Solutions, we are on a mission to revolutionize the way businesses leverage data for strategic decision-making. As a leading technology company, we thrive on innovation and are looking for a talented Data Scientist to join our dynamic team.
Job Description:
Responsibilities:
    Conduct exploratory data analysis to identify trends, patterns, and insights from large datasets.
    Develop and implement machine learning models for predictive analytics and classification.
    Collaborate with cross-functional teams to understand business requirements and deliver data science solutions.
    Clean, preprocess, and transform raw data into a usable format for analysis.
    Present findings and insights to technical and non-technical stakeholders.
Required Skills:
    Master's or Ph.D. in Computer Science, Statistics, or a related field.
    3+ years of hands-on experience in data science and machine learning.
    Proficiency in Python and R programming languages.
    Strong knowledge of machine learning frameworks (e.g., TensorFlow, PyTorch) and libraries (e.g., scikit-learn).
    Experience with big data technologies (e.g., Hadoop, Spark).
    Excellent problem-solving skills and ability to work independently.
Desired Skills:
    Familiarity with cloud platforms, especially AWS or Azure.
    Previous experience in the technology or e-commerce industry.
    Solid understanding of natural language processing (NLP) techniques.
    Strong communication skills and ability to convey complex concepts to non-technical stakeholders.
Benefits and Perks:
    Competitive salary with performance-based bonuses.
    Comprehensive health, dental, and vision insurance.
    401(k) retirement plan with employer matching.
    Flexible work hours and opportunities for remote work.
    Professional development programs and continuous learning opportunities."))
"""
