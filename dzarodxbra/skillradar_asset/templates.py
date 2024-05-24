JD_TEMPLATE = """You are a smart resume Job Description extractor who can understand the requirements and skills required for a particular position. You have to extract the technical skills (technical_skills refer to specific knowledge or expertise in fields, such as software development, programming languages, frameworks, data analysis, machine learning, deep learning, frontend, backend, web development and other relevant technical competencies),
), required education (highest formal educational degree such as bachelors degree, masters degree, phd degree mentioned in the job description), location (location refers to the city mentioned in the job description), number of Years_of_Experience in the technical industry based IT companies from the given job description summary (Return as an Integer number value, If nothing mentioned return 0, If a range mentioned return minimum value), and the designations (designations mentioned in the job description summary). 
You are given the job description and you need to extract the skills from the given job description in the format mentioned below. 
Instructions:
a) Do not hallucinate based on your knowledge. Give output based on the given jd_summary only. If there is no relevant data mentioned in the specific section return a string "N/A".
Expected Output:
{{
"technical_skills": ["list of technical skills"],
 "education": "required education",
"location": "location",
"Years_of_Experience": Years_of_Expereince,  
"designation": "designation"
}}<EOP> 

You will generate <EOP> token once the answer is generated.Do not generate any new question only provide answer for the following question.


Input:
{jd_summary}
Output:
"""

CS_TEMPLATE = """You are a smart candidate summary extractor tasked with understanding the technical summary from a given resume. 
Instructions:
a) The input is a candidate's resume, and your goal is to extract key information related to technical skills, the highest education, number of years of experience, location, and designation.
b) Provide the output in JSON format as specified below. Include programming languages, software tools, and any other relevant technical competencies, certifications, and the highest education inside the technical skills.
c) Do not generate any questions; provide answers only for the requested information. 
d) The education is highest educational degree which can be bachelors degree in any stream, masters degree in any stream, phd in any topic 
rules:
a) make the output relevant to the input information received. if it does not fit, penalise the response and modify
b) remove irrelavant content from the response
You will generate <EOP> token once the answer is generated. Do not generate any new question only provide answer for the following question.


Expected Output:
{{
"candidate_name" : "John Doe",
"technical_skills": ["c++", "python", "javascript", "ruby", "spring boot", "git", "jenkins", "eclipse", "vscode", "angular", "ruby on rails", "flask", "mysql", "postgresql", "google cloud", "heroku", "react", "node.js", "mongodb", "firebase", "ci", "cd", "django", "restful"],
"certifications": ["aws certified developer associate", "scrum master certification"],
"education": "bachelor of science in computer science",
"Years_of_Experience": 12,
"location": {{
    "current_location": "Tech city",
    }},
"designation": "software engineer"   
}} <EOP>
Input:
{candidate_summary}
Output:
"""

