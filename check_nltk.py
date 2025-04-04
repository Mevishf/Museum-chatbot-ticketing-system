import nltk

def check_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
        print("NLTK Data is already downloaded")
    except LookupError:
        print("Downloading required NLTK data...")
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        print("Download complete!")

if __name__ == "__main__":
    check_nltk_data() 