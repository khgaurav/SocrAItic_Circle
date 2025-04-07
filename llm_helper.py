import os
from typing import List, Dict, Any
import sys
os.environ["GEMINI_API_KEY"] = ""
os.environ["PERPLEXITY_API_KEY"] = ""
def call_llm_api(prompt: str, model_name: str = "gpt-4", context: List[Dict[str, str]] = None) -> str:
    """
    Function to call Gemini or Perplexity API based on the model name.

    Args:
        prompt (str): The input prompt for the LLM.
        model_name (str): The specific LLM model to use (e.g., 'gemini-1.5-flash', 'sonar-pro').
        context (List[Dict[str, str]]): Optional conversation history or context.

    Returns:
        str: The response from the LLM.
    """

    print(f"\n--- Calling LLM ({model_name}) ---")
    print(f"Prompt: {prompt[:100]}...") # Print truncated prompt
    
    # Handle Gemini models
    if model_name.startswith('gemini'):
        try:
            from google import genai
            
            # Initialize with API key from environment variable
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            
            # Convert context to format expected by Gemini
            if context:
                # For Gemini, we need to flatten the context messages
                contents = []
                for msg in context:
                    contents.append(msg["content"])
                contents.append(prompt)
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
            else:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
            
            return response.text
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error: Could not get response from {model_name}."
    
    # Handle Perplexity models (sonar or sonar-pro)
    elif model_name.startswith('sonar'):
        try:
            from openai import OpenAI
            
            # Initialize the client with custom base URL for Perplexity
            api_key = os.getenv("PERPLEXITY_API_KEY")
            client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
            
            # Format messages for chat completion ensuring alternating roles
            if context:
                messages = context.copy()
                if messages and messages[-1].get("role") == "user":
                    messages.append({"role": "assistant", "content": ""})
            else:
                messages = []
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling Perplexity API: {e}")
            sys.exit(f"Error: Could not get response from {model_name}.")
    
    # Default case for unsupported models
    else:
        print(f"Model {model_name} not supported. Please use a Gemini or Perplexity model.")
        return f"Error: Unsupported model {model_name}."
