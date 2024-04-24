from llm.modeling.llm_langchain import LLM_LangChain
import torch

# Initialize the LLM LangChain model
model = LLM_LangChain.from_pretrained("gpt3.5-turbo")

def generate_summary(word, max_length=100):
    # Define the input prompt
    prompt = f"Summarize information about the word '{word}'."

    # Generate the summary
    output = model.generate(
        prompt,
        max_length=max_length,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=model.tokenizer.eos_token_id,
        return_tensors="pt"
    )

    # Decode the output tokens and extract the summary
    summary = model.tokenizer.decode(output[0], skip_special_tokens=True)

    return summary

# Example usage
word = input("Input the word")
summary = generate_summary(word)
print(f"Summary for the word '{word}':")
print(summary)
