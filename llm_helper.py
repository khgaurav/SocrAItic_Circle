import os
from typing import List, Dict, Any
import sys
os.environ["GEMINI_API_KEY"] = "AIzaSyD4xPZA7-yJ4KZ2B1gk85OBFHeTsAlPGKw"
os.environ["PERPLEXITY_API_KEY"] = "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"
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
        return call_google(prompt, model_name, context)    
    # Handle Perplexity models (sonar or sonar-pro)
    elif model_name.startswith('sonar'):
        return call_perplexity(prompt, model_name, context)
    # Default case for unsupported models
    else:
        print(f"Model {model_name} not supported. Please use a Gemini or Perplexity model.")
        raise

def call_perplexity(prompt: str, model_name: str = "sonar-pro", context: List[Dict[str, str]] = None):
    try:
        from openai import OpenAI
        # Initialize with API key from environment variable
        api_key = os.getenv("PERPLEXITY_API_KEY")
        client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        
        # Prepare messages for the chat completion
        messages = []
        
        # Add context if provided
        if context:
            for msg in context:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling Perplexity API: {e}")
        raise


def call_google(prompt: str, model_name: str = "gpt-4", context: List[Dict[str, str]] = None):
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
        raise
