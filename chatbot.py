import nltk
from nltk.chat.util import Chat
from llm import chat_with_llm
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from gemini_handler import generate_museum_response
import re
import random

# Create a dictionary to store user states (for each user session)
user_states = {}

# Pairs: List of patterns and corresponding responses
pairs = [
    [
        r"my name is (.*)",
        ["Hello %1, How can I assist you today?",]
    ],
    [
        r"hello|hi|hey",
        ["Hello! Welcome to the Indian Music Museum! 🙏",
         "Hi there! Welcome to your musical journey!",
         "Greetings! Ready to explore Indian music?"]
    ],
    [
        r"how are you?",
        ["I'm doing great, how about you?", "I'm good! Ready to assist you.",]
    ],
    [
        r"thank you|thanks",
        ["धन्यवाद! (Thank you!) Have a musical day!", 
         "You're welcome! Don't forget to check out our special exhibitions!",
         "Glad to help! Hope you enjoy the rhythms of Indian music!"]
    ],
    [
        r"goodbye|bye|quit",
        ["Farewell! May the music be with you! 🎵",
         "Goodbye! Looking forward to your melodious journey with us!",
         "See you soon! Don't forget to check our live performances schedule!"]
    ],
    [
        r"तिकिटांची किंमत काय आहे",
        ["राष्ट्रीय संग्रहालयातील प्रवेश शुल्क खालीलप्रमाणे आहे:\n\nप्रौढ: 20 रुपये\nविदेशी नागरिक: 500 रुपये\n12 व्या वर्गापर्यंतचे विद्यार्थी: विनामूल्य (शालेय ओळखपत्रासह)\n\nतुम्हाला कोणत्याही प्रवेश शुल्कांबद्दल अधिक माहिती हवी असेल तर तुम्ही संग्रहालयाच्या वेबसाइटला भेट देऊ शकता किंवा त्यांना फोन करू शकता.\n\nतुमच्याकडे काही प्रश्न असतील तर मला कळवा."]
    ],
    [
        r"opening hours|timings",
        ["🕒 Our musical doors are open:\nTuesday-Sunday: 10:00 AM to 6:00 PM\nClosed on Mondays for maintenance"]
    ],
    [
        r"exhibition|special exhibition|current exhibition",
        ["🎵 Current Special Exhibitions:\n\n1. 'The Evolution of Tabla'\n2. 'Rare Musical Instruments Gallery'\n3. 'Classical Legends of India'\n\nWould you like to know more about any specific exhibition?"]
    ],
    [
        r"facilities|amenities",
        ["🏛️ Our Facilities:\n• Guided Audio Tours in multiple languages\n• Wheelchair accessibility\n• Musical Instrument Display Gallery\n• Interactive Music Room\n• Cafeteria with traditional refreshments\n• Souvenir Shop\n• Free Locker Service"]
    ],
    [
        r"ticket|booking|price",
        ["Ticket Prices:\n🎫 Indian Visitors: ₹20\n🎫 International Visitors: ₹500\n🎓 Students: Free (with valid ID)\n\nWould you like to book tickets now?"]
    ],
    [
        r"performance|show|concert",
        ["📅 Upcoming Performances:\n• Classical Sitar Recital - This Weekend\n• Carnatic Vocal Concert - Next Tuesday\n• Tabla Workshop - Every Saturday\n\nWould you like to book tickets for any performance?"]
    ],
    [
        r"guide|tour|audio",
        ["🎧 Audio Guide Options:\n• Hindi\n• English\n• Sanskrit\n• Regional Languages\n\nAudio guides are available at the reception for ₹50."]
    ],
    [
        r"parking|transport",
        ["🚗 Parking Information:\n• Free parking available\n• Nearest Metro: XYZ Station\n• Bus Routes: 101, 102, 103\n• Taxi stand available"]
    ],
    [
        r"food|cafe|restaurant",
        ["🍽️ Our Cafeteria:\n• Traditional Indian Refreshments\n• Modern Cafe\n• Open 10:30 AM - 5:30 PM\n• Located on Ground Floor"]
    ],
    [
        r"souvenir|shop|merchandise",
        ["🛍️ Museum Shop:\n• Traditional Instruments\n• Music Books & CDs\n• Handcrafted Items\n• Cultural Merchandise"]
    ],
    [
        r"नमस्ते|हैलो",
        ["नमस्ते! भारतीय संगीत संग्रहालय में आपका स्वागत है! 🙏",
         "भारतीय संगीत की यात्रा में आपका स्वागत है!",
         "कैसे मदद कर सकते हैं आपकी?"]
    ],
    [
        r"टिकट|बुकिंग",
        ["टिकट की कीमतें:\n🎫 भारतीय नागरिक: ₹20\n🎫 विदेशी नागरिक: ₹500\n🎓 विद्यार्थी: मुफ्त (ID के साथ)\n\nक्या आप टिकट बुक करना चाहेंगे?"]
    ],
    [
        r"समय|टाइमिंग",
        ["🕒 हम खुले हैं:\nमंगलवार-रविवार: सुबह 10:00 से शाम 6:00 बजे तक\nसोमवार को बंद"]
    ],
    [
        r"வணக்கம்|ஹலோ",
        ["வணக்கம்! இந்திய இசை அருங்காட்சியகத்திற்கு வரவேற்கிறோம்! 🙏",
         "இந்திய இசை பயணத்திற்கு வரவேற்கிறோம்!",
         "நான் உங்களுக்கு எப்படி உதவ முடியும்?"]
    ],
    [
        r"டிக்கெட்|புக்கிங்",
        ["டிக்கெட் விலைகள்:\n🎫 இந்தியர்கள்: ₹20\n🎫 வெளிநாட்டினர்: ₹500\n🎓 மாணவர்கள்: இலவசம் (ID உடன்)"]
    ],
    [
        r"नमस्कार|हॅलो",
        ["नमस्कार! भारतीय संगीत संग्रहालयात आपले स्वागत आहे! 🙏",
         "भारतीय संगीताच्या प्रवासात आपले स्वागत आहे!",
         "मी आपली कशी मदत करू शकतो?"]
    ],
    [
        r"सुविधा|सोयी",
        ["🏛️ आमच्या सुविधा:\n• बहुभाषिक ऑडिओ टूर\n• व्हीलचेअर प्रवेश\n• संगीत वाद्य प्रदर्शन\n• कॅफेटेरिया\n• सोवेनिर शॉप"]
    ],
    [
        r"નમસ્તે|હેલો",
        ["નમસ્તે! ભારતીય સંગીત સંગ્રહાલયમાં આપનું સ્વાગત છે! 🙏",
         "ભારતીય સંગીતની સફરમાં આપનું સ્વાગત છે!",
         "હું આપની કેવી મદદ કરી શકું?"]
    ],
    [
        r"ટિકિટ|બુકિંગ",
        ["ટિકિટ ભાવ:\n🎫 ભારતીય નાગરિક: ₹20\n🎫 વિદેશી નાગરિક: ₹500\n🎓 વિદ્યાર્થી: મફત (ID સાથે)"]
    ],
]


reflections = {
    "i am"       : "you are",
    "i was"      : "you were",
    "i"          : "you",
    "i'm"        : "you are",
    "i'd"        : "you would",
    "i've"       : "you have",
    "i'll"       : "you will",
    "my"         : "your",
    "you are"    : "I am",
    "you were"   : "I was",
    "you've"     : "I have",
    "you'll"     : "I will",
    "your"       : "my",
    "yours"      : "mine",
    "you"        : "me",
    "me"         : "you"
}


chatbot = Chat(pairs, reflections)

def display_menu():
    menu = """
    🏛️ Welcome to Museum Assistant! 🏛️
    Please select an option (enter the number):
    
    1. Ticket Booking
    2. Museum Timings
    3. Entry Fees
    4. Special Exhibitions
    5. Facilities
    6. Contact Us
    7. Free Form Chat
    
    Enter 'quit' to exit
    """
    return menu

def handle_menu_choice(choice):
    menu_responses = {
        "1": """
        Ticket Booking Options:
        a) Indian Citizen (₹20)
        b) Foreign National (₹500)
        c) Student (Free with ID)
        
        Please type 'book a/b/c' to proceed
        """,
        "2": "We're open Tuesday-Sunday, 10:00 AM to 6:00 PM. Closed on Mondays and National Holidays.",
        "3": """
        Entry Fees:
        - Indian Adults: ₹20
        - Foreign Nationals: ₹500
        - Students (up to class 12): Free with ID
        """,
        "4": "Current exhibitions: [Exhibition details will be displayed here]",
        "5": """
        Available Facilities:
        - Wheelchair access
        - Audio tours
        - Cafeteria
        - Cloak room
        - Museum shop
        
        Type the facility name for more details
        """,
        "6": "Contact us at: [contact details]"
    }
    return menu_responses.get(choice, "Please select a valid option (1-7)")

def get_chatbot_response(user_input, user_id=None):
    # Pattern matching using regex
    for pattern, responses in pairs:
        match = re.match(pattern, user_input.lower())
        if match:
            response = random.choice(responses)
            return response
    
    # If no pattern matches, use Gemini
    try:
        return generate_museum_response(user_input)
    except Exception as e:
        print(f"Error getting Gemini response: {str(e)}")
        return "I apologize, but I'm having trouble understanding. Could you please rephrase your question?"

def get_language_preference():
    return """
    Select your preferred language / भाषा चुनें / भाषा निवडा / மொழியைத் தேர்ந்தெடுக்கவும் / ભાષા પસંદ કરો:
    
    1. English
    2. हिंदी (Hindi)
    3. मराठी (Marathi)
    4. தமிழ் (Tamil)
    5. ગુજરાતી (Gujarati)
    
    Type the number or language name
    """

if __name__ == "__main__":
    print("Welcome! I am your museum ticket booking assistant. How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        response = get_chatbot_response(user_input, "user1")
        print(f"Bot: {response}")