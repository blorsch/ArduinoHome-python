import speech_recognition as sr
import serial
import threading
from gtts import gTTS
import os
import time

temperature = 0.0
humidity = 0.0

def recognize_speech_from_mic(recognizer, microphone): #https://towardsdatascience.com/how-to-build-a-speech-recognition-bot-with-python-81d0fe3cea9a
    """Transcribe speech from recorded from `microphone`.
    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)  # #  analyze the audio source for 1 second
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #   update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
        interpret_transcription(response["transcription"])
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable/unresponsive"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

def interpret_transcription(transcription):

    text = ""

    #asking about temperature
    if "temperature" in transcription:
        output("The temperature is %.1f degrees" % temperature)

    elif "humidity" in transcription:
        output("The relative humidity is %.1f percent" % humidity)

def output(str):
    audio = gTTS(text=str, lang='en', slow=False)  # https://www.geeksforgeeks.org/convert-text-speech-python/
    audio.save("audio.mp3")
    os.system("mpg321 audio.mp3")

def get_serial_data():
    threading.Timer(10.0, get_serial_data).start()
    with serial.Serial('/dev/cu.usbmodem14201', 9600, timeout=3) as ser:
        data = ser.read(50)  # read up to 100 bytes (timeout)

        datapoints = data.decode('utf-8').split('\r\n')

        for point in datapoints:
            if "*" in point:
                global temperature
                temperature = float(point[1:])
            elif "&" in point:
                global humidity
                humidity = float(point[1:])

# %%

if __name__ == "__main__": #https://towardsdatascience.com/how-to-build-a-speech-recognition-bot-with-python-81d0fe3cea9a

    get_serial_data()
    time.sleep(5) #wait for serial data to come in
    print("Waiting for speech")
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=0)
    response = recognize_speech_from_mic(recognizer, mic)
    print('\nSuccess : {}\nError   : {}\n\nText from Speech\n{}\n\n{}' \
          .format(response['success'],
                  response['error'],
                  '-' * 17,
                  response['transcription']))