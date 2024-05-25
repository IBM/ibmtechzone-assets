                        FineTuning a large language model locally using InstructLab
""
InstructLab provides a command-line interface (CLI) that allows users to fine-tune pre-trained 
language models (LLMs) locally. This CLI tool offers a convenient way for contributors and 
researchers to experiment with fine-tuning LLMs on their own laptops or workstations without needing access to specialized hardware or cloud-based resources.
""

## Source: 
https://github.com/instructlab/community/blob/main/InstructLab_SLACK_GUIDE.md?source=post_page-----6ffb65aa1d57--------------------------------
https://github.com/instructlab/instructlab/blob/main/README.md?source=post_page-----6ffb65aa1d57--------------------------------
https://arxiv.org/abs/2403.01081?source=post_page-----6ffb65aa1d57--------------------------------

# 1.1 Installing ilab cli:
Download required packages to run ilab cli.
1: installing g++
    >> sudo dnf install g++ gcc make pip python3 python3-devel python3-GitPython

2: Create a new folder called instructlab to store the files the ilab CLI needs when running
    >> mkdir instructlab
    >> cd instructlab

3: install the ilab CLI.
    >> python3 -m venv --upgrade-deps venv
    >> source venv/bin/activate
    >> (venv) $ pip cache remove llama_cpp_python
    >> (venv) $ pip install git+https://github.com/instructlab/instructlab.git@stable -C cmake.args="-DLLAMA_METAL=on"

# 1.2 verifyilab is installed correctly.
    >> (venv) $ ilab

# 1.3 Initialize ilab
    >> (venv) $ ilab init

# 1.4 Download the model:
    1.4.1: Downloading LLM model.
    >> (venv) ilab download

    Downloading model from instructlab/merlinite-7b-lab-GGUF@main to models...

    1.4.2: Alternatively we can download other models as well from hugging face: [Granite-7B]
    >> (venv) $ ilab download --repository instructlab/granite-7b-lab-GGUF --filename granite-7b-lab-Q4_K_M.ggufs


# 1.5 Chat with the model in ilab cli:
    >> (venv) ilab chat
    INFO 2024-05-19 19:48:02,482 server.py:206 Starting server process, press CTRL+C to shutdown server...
    INFO 2024-05-19 19:48:02,482 server.py:207 After application startup complete see http://127.0.0.1:18813/docs for API.
    ╭─────────────────────────────────────────── system ───────────────────────────────────────────╮
    │ Welcome to InstructLab Chat w/ MERLINITE-7B-LAB-Q4_K_M (type /h for help)                    │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────╯
    >>> tell me about cricket game    


2. Adding new Skills/Knowledge to the LLM and fine tuning model.    

2.1 create a new skill/knowledge for the model

To create a new skill/knowledge for the model, You need two things: a qna.yaml file and a attribution.txt 
for metadata and place it under taxonomy folder. both of these files will be used in the training phase afterwards.

Example: here we add a new qna.yaml file having arithmetic_reasoning related question and answers as available in qna.yaml:
similary we can finetune a model new skills specific to our use case, just by creating some question and examples and generate synthetic dataset..

2.2 List newly added data and validate its format by running the following command:
    >> (venv) $ ilab diff

2.3 Generate new synthetic dataset:
    >> (venv) $ ilab generate

2.4 Training the model:
    >> (venv) $ ilab train

2.5 Chat with the new model in ilab cli to test new model skill:
    >> (venv) ilab chat --model <NEW_MODEL>

2.6 Once a new model is finetuned on the specific task, we can push the same on huggingface.




########### RUN #######
Execute using the command chmod +x ilab_setup.sh. 
Then you can run the script using ./ilab_setup.sh. 
Make sure to replace <NEW_MODEL> with the name of your newly trained model.