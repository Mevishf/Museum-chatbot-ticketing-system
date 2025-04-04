"""
Install the Google AI Python SDK

$ pip install google-generativeai
"""
from ticket.ticket_details import generate_link
import google.generativeai as genai
import markdown2
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("API")

# Configure the Google Generative AI SDK with the API key
genai.configure(api_key=api_key)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  tools=[generate_link],
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  system_instruction="You are a ticket booking chatbot for the museum. Your personality traits: - Friendly and welcoming - Knowledgeable about museum exhibits - Helpful with ticket booking - Clear and concise in responses",
)

chat_session = model.start_chat(enable_automatic_function_calling=True)

def chat_with_llm(user_input):
    response = chat_session.send_message(user_input)
    response = markdown_to_html(response.text)
    return response

def markdown_to_html(markdown_text):
    markdowner = markdown2.Markdown()
    html_text = markdowner.convert(markdown_text)
    return html_text

if __name__ == "__main__":
    print("Welcome! I am your museum ticket booking assistant. How can I help you today?")
    while True:
        user_input = input("You: ")
        print(chat_with_llm(user_input))