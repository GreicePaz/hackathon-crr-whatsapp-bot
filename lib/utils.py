from gtts import gTTS
from pydub import AudioSegment
from os import path

import speech_recognition as psr
import requests, time, os

def convert_text_in_audio(text):
    obj_audio = gTTS(text=text, lang='pt-br', slow=False)

    name_audio = f'text_in_audio{time.time()}.mp3'

    obj_audio.save(f'static/{name_audio}')

    return name_audio

def convert_audio_in_text(audio):
    rg = psr.Recognizer()

    try:
        with psr.AudioFile(audio) as source:
            sound = rg.record(source)
    except FileNotFoundError:
        time.sleep(10)
        with psr.AudioFile(audio) as source:
            sound = rg.record(source)
    
    delete_file(audio)

    response = {'sucess': True, 'text': ''}
    try:
        list_text = rg.recognize_google(
            sound,
            language='pt-BR',
            show_all = True
        )
    except Exception as e:
        response['sucess'] = False
    
    text = clean_text(list_text)

    response['text'] = text

    return response

def download_audio(url):
    name = f'static/dow_audio_{time.time()}'.replace('.', '_')
    file_name = f'{name}.ogg'

    audio_file = path.join(path.dirname(path.realpath(__file__)), file_name)

    with open(file_name, "wb") as file:
        response = requests.get(url)
        
        file.write(response.content)
    
    response = convert_audio(name)
    
    delete_file(f'{name}.ogg')
    
    if not response:
        return False    
    
    return response

def convert_audio(name):
    try:
        p = AudioSegment.from_ogg(f'{name}.ogg')
        p.export(f'{name}_convert.wav', format='wav')
    except:
        return False

    audio = f'{name}_convert.wav'

    return audio

def delete_file(name):
    if os.path.exists(name):
        os.remove(name)
    
    return True

def clean_text(text):
    pharase = ''

    alternatives = text.get('alternative')
    for section in alternatives:
        if section.get('confidence'):
            phrase = section.get('transcript')
            break
    
    return phrase