import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def get_gemini_response(prompt):
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate response with museum context
        prompt_with_context = f"""
        As a museum guide chatbot named MuseoBot, respond to: {prompt}
        
        Keep in mind:
        - Focus on museum-related information
        - Be informative but concise
        - Include relevant cultural and historical context
        - Maintain a friendly, helpful tone
        """
        
        response = model.generate_content(prompt_with_context)
        return response.text
    except Exception as e:
        print(f"Error with Gemini API: {str(e)}")
        return "I apologize, but I'm having trouble processing your request at the moment."

def generate_museum_response(user_input):
    return get_gemini_response(user_input) 