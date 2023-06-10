#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 16:26:46 2023

@author: steeltitanunbrk
"""

import random
import json 
import torch
from models import NeuralNet
from nltk_utils import bag_of_words, tokenize
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import speech_recognition as sr
from gtts import gTTS
from time import sleep
from pydub import AudioSegment
from pydub.playback import play

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
duration = 3 # en secondes
freq = 44100
filename = "output.wav"

def user_question():
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
    

with open('intents.json', 'r') as f:
    intents = json.load(f)
    
FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()



bot_name = "Boty"
print("Let's chat! type 'quit' to exit")
while True:
    print("Posez votre question !")
    sentence = f"You : {user_question()}"
    if sentence == 'You : stop':
        break
    print(sentence)
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X)
    
    output = model(X)
    
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    
    
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    
    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                # print(f"{bot_name}: {random.choice(intent['responses'])}")
                answer = random.choice(intent['responses'])
                print(f"{bot_name}: {answer}")
                tts = gTTS(text=answer, lang='fr')
                tts.save("answer.mp3")
                answer_player(tts)
                sleep(1)
    else:
        print(f"{bot_name}: Je ne comprends pas ...")
        tts = gTTS(text="Je ne comprends pas", lang='fr')
        tts.save("answer.mp3")
        answer_player(tts)
        sleep(1)
        
"""while True:
    sentence = f"You : {user_question()}"""
