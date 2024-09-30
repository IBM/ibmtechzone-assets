"""
1. This is prompt template to create a call summary from the Call logs/Interaction between the Operator and Customer.
2. You can modify the prompt based on your requirements, for example removing/adding example conversation for more accurate summary creation by llm, number of words to generate summary, etc.
3. Currently, used prompt styling is ReAct(Reasoning and Acting prompting style). This is compatible with Lllam and Mistral.
4. It would be best to first preprocess the call interaction such as removing filler words, jargons, identifying speakers, etc.
"""

prompt_context = """
reAct {{
  task: "Summarization of a conversation between OP (Operator) and CU (Customer)"
  instructions: [
    "Provide a text summary of the conversation under 130 words without any fillers or redundant information.",
    "Stick strictly to the factual details presented in the conversation; do not introduce new information.",
    "Ensure your summary is cohesive and includes as many factual details as possible.",
    "If any of these rules are not followed, regenerate the summary."
  ]
  examples: [
    {{
      conversation:f"Enter your example call interaction between Operator and Customer"
      summary: "Enter the summary of the example call interaction between Operator and Customer"
    }},
    {{
      conversation:f"Enter your example call interaction between Operator and Customer"
      summary: "Enter the summary of the example call interaction between Operator and Customer"
    }},  
    {{
      conversation:f"Enter your example call interaction between Operator and Customer"
      summary: "Enter the summary of the example call interaction between Operator and Customer"
    }}
  ]
  }}
  
Summary:
"""
