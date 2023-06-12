import re
import random
import speech_recognition as sr
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play
from scipy.io.wavfile import write
import wavio as wv
from gtts import gTTS
from time import sleep


RECIPES = ["La cuisine africaine est très diversifiée en raison de la grande variété de cultures et de traditions culinaires sur le continent.",
                  "1. Poulet yassa : Un plat sénégalais à base de poulet mariné dans une sauce à base d'oignons, de citron et d'épices, puis grillé ou braisé.",
                  "2. Couscous : Un plat d'origine berbère qui est couramment consommé dans plusieurs pays d'Afrique du Nord, avec différentes variations selon les régions.",
                  "3. Bobotie : Un plat traditionnel d'Afrique du Sud à base de viande hachée, d'œufs et de pain, assaisonné avec des épices et cuit au four.",
                  "4. Jollof rice : Un plat populaire en Afrique de l'Ouest, principalement au Nigeria, à base de riz, de tomates, d'oignons et d'épices, souvent servi avec du poulet ou du poisson.",
                  "5. Injera : Un pain traditionnel éthiopien et érythréen, qui est également utilisé comme base pour de nombreux plats en Éthiopie, comme le doro wat (un ragoût de poulet épicé) ou le tibs (un plat de viande sautée)."]

UNKNOWN_RESPONSES = ['Je n\'ai pas compris', 'Veuillez répéter s\'il vous plaît', 'Il semblerait que je n\'ai pas suivi ce cours', 'Error 404', 'Sorry I don\'t speak french', '...']

def unknown():
    return random.choice(UNKNOWN_RESPONSES)


def message_probability(user_message, recognised_words, single_response=False, required_words=[]):
    message_certainly = 0
    has_required_words = True

    for word in user_message:
        if word in recognised_words:
            message_certainly += 1
        
    percentage = float(message_certainly) / float(len(recognised_words))

    for word in required_words:
        if word not in user_message:
            has_required_words = FloatingPointError
            break

    if has_required_words or single_response:
        return int(percentage*100)
    else:
        return 0
    

def check_all_messages(message):
    highest_prob_list = {}

    def response(bot_response, list_of_words, single_response=False, required_words=[]):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = message_probability(message, list_of_words, single_response, required_words)

    
    response(random.choice(["Hello", "Hey", "Hi", "Comment puis-je vous aider ?", "Salut", "Bonjour", "Salutations", "Salut!", "Salut à toi", "Hi!", "Comment ça va ?"]), ["hello", 'hi', 'cc', 'bonjour', 'hé', 'yo', "salut"], single_response=True)
    response(random.choice(["A la prochaine", "Ok", "A +"]), ["ciao", 'revoir', 'bye', 'goodbye'])
    response(random.choice(['Je m\'appelle Boty', "Boty !", "C'est Boty"]), ['nom', 'nomme', 'appelle'], single_response=True)
    response(random.choice(RECIPES), ['plat', 'africain', 'cuisine', 'recette', 'traditionnelle'], single_response=True)

    best_match = max(highest_prob_list, key=highest_prob_list.get)
    print(highest_prob_list)

    return unknown() if highest_prob_list[best_match] < 1 else best_match


def user_question():
    duration = 3 # en secondes
    freq = 44100
    filename = "output.wav"

    recording = sd.rec(int(duration * freq),
                   samplerate=freq, channels=2)
 
    # Record audio for the given number of seconds
    song = AudioSegment.from_mp3("1023.mp3")
    play(song)
    sd.wait()
    song = AudioSegment.from_mp3("1024.mp3")
    play(song)
    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write("recording0.wav", freq, recording)
     
    # Convert the NumPy array to audio file
    wv.write(filename, recording, freq, sampwidth=2)  # Save as WAV file 
    
    # initialize the recognizer
    r = sr.Recognizer()
    
    # open the file
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        try:
            text = r.recognize_google(audio_data, language="fr-FR")
        except:
            text = "salut"    
    return text


def answer_player(tts):
    song = AudioSegment.from_mp3("answer.mp3")
    play(song)


def get_response(user_input):
    split_message = re.split(r'\s+|[,;?!.-]\s*', user_input.lower())
    response = check_all_messages(split_message)
    return response

while True:
    # question = input('You: ')
    question = user_question()
    print(question)

    if str(question) == 'stop':
        print('Ce fut un plaisir !')
        break
    answer = get_response(question)
    print('Boty: ' + answer)

    tts = gTTS(text=answer, lang='fr')
    tts.save("answer.mp3")
    answer_player(tts)
    sleep(1)
