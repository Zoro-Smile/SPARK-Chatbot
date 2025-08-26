import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import random
import smtplib
import requests
import subprocess
import threading
from pathlib import Path
from dotenv import load_dotenv
import wolframalpha

# Optional module
try:
    import pyjokes
except ImportError:
    pyjokes = None

load_dotenv()

# Text to speech setup
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    print(f"Spark: {audio}")
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        greet = "Good Morning"
    elif hour < 18:
        greet = "Good Afternoon"
    else:
        greet = "Good Evening"
    speak(f"{greet} lord smile! I am Spark. Your personal intelligence. What do you need sir?")

def takeCommand(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening sir...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            return "None"
    try:
        print("Recognizing...")
        query = r.recognize_google(audio)
        print(f"Smile said: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        print("not reconized")
    except sr.RequestError:
        speak("Speech service unavailable sir.")
    return "None"

def sendEmail(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        server.sendmail(os.getenv('EMAIL_USER'), to, content)
        server.quit()
        speak("Email has been sent!")
    except Exception as e:
        print(e)
        speak("Unable to send the email, sir.")

def fetch_news():
    api_key = os.getenv('NEWS_API_KEY')
    url = f'https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            for i, article in enumerate(articles[:5], 1):
                speak(f"News {i}: {article['title']}")
        else:
            speak("Couldn't fetch news.")
    except Exception as e:
        print(e)
        speak("Error fetching news.")

def get_weather(city="hyderabad"):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['current']['temp_c']
            condition = data['current']['condition']['text']
            speak(f"The current temperature in {city} is {temp} degrees Celsius with {condition}.")
        else:
            speak("I couldn't get the weather right now sir.")
    except:
        speak("Error fetching weather sir.")

reminders = []

def add_reminder(content):
    reminders.append(content)
    speak(f"Reminder added: {content}")

def check_reminders():
    if reminders:
        speak("You have the following reminders:")
        for r in reminders:
            speak(r)
    else:
        speak("You have no reminders, sir.")

def calculate_with_wolfram(query):
    try:
        client = wolframalpha.Client(os.getenv("WOLFRAM_API_KEY"))
        res = client.query(query)
        answer = next(res.results).text
        speak(f"The answer is {answer}")
    except:
        speak("Sorry, I couldn't calculate that.")

def open_app(app_name, path):
    if os.path.exists(path):
        subprocess.Popen([path])
        speak(f"Opening {app_name} sir!")
    else:
        speak(f"Sorry sir. {app_name} is not available.")

def close_app(app_name):
    close_commands = {
        "notion": "Notion.exe",
        "vs code": "Code.exe",
        "word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "notepad": "notepad.exe",
        "calculator": "Calculator.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "whatsapp": "chrome.exe",
        "youtube": "chrome.exe",
        "telegram": "chrome.exe",
        "github": "chrome.exe",
        "google": "chrome.exe"
    }

    exe = close_commands.get(app_name)
    if exe:
        os.system(f"taskkill /f /im {exe}")
        speak(f"Closed {app_name} sir.")
    else:
        speak(f"I don't know how to close {app_name} sir.")

def main():
    wishMe()
    app_paths = {
        "notion": r"C:\Users\nagap\AppData\Local\Programs\Notion\Notion.exe",
        "vs code": r"C:\Users\nagap\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"
    }

    while True:
        query = takeCommand()
        if query == "none":
            continue

        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                speak(results)
            except:
                speak("Sorry, I couldn't find that.")

        elif 'open youtube' in query:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube sir!")

        elif 'open google' in query or 'open chrome' in query:
            webbrowser.open("https://google.com")
            speak("Opening Google sir!")

        elif 'open whatsapp' in query:
            webbrowser.open("https://web.whatsapp.com/")
            speak("Opening WhatsApp sir!")

        elif 'open chatgpt' in query:
            webbrowser.open("https://chatgpt.com/")
            speak("Opening ChatGPT sir!")

        elif 'open github' in query:
            webbrowser.open("https://github.com")
            speak("Opening GitHub sir!")

        elif 'open telegram' in query:
            webbrowser.open("https://web.telegram.org/a/")
            speak("Opening Telegram sir!")

        elif 'play music' in query:
            music_dir = Path.home() / "Music"
            songs = list(music_dir.glob("*.mp3"))
            if songs:
                os.startfile(songs[0])
                speak("Playing music sir!")
            else:
                speak("No music files found sir!")

        elif 'time is' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, now the time is {strTime}")

        elif 'email' in query:
            speak("What should I say?")
            content = takeCommand()
            speak("Whom should I send it to?")
            to = input("Enter recipient email: ")
            sendEmail(to, content)

        elif 'news' in query:
            threading.Thread(target=fetch_news).start()

        elif 'weather' in query:
            speak("Which city sir?")
            city = takeCommand()
            if city != "none":
                get_weather(city)

        elif 'reminder' in query:
            if 'add' in query:
                speak("What should I remind you of sir?")
                reminder = takeCommand()
                if reminder != "none":
                    add_reminder(reminder)
            elif 'show' in query or 'check' in query:
                check_reminders()

        elif 'turn off system' in query:
            speak("Shutting down the system.")
            os.system('shutdown /s /t 5')

        elif 'restart system' in query:
            speak("Restarting the system.")
            os.system('shutdown /r /t 5')

        elif 'say some joke' in query:
            if pyjokes:
                joke = pyjokes.get_joke()
                speak(joke)
            else:
                speak("Joke module not installed.")

        elif 'calculate' in query:
            speak("What should I calculate?")
            calc_query = takeCommand()
            calculate_with_wolfram(calc_query)

        elif 'open notepad' in query:
            subprocess.Popen(['notepad.exe'])
            speak("Opening Notepad sir!")

        elif 'open calculator' in query or 'open clock' in query:
            subprocess.Popen(['calc.exe'])
            speak("Opening Calculator sir!")

        elif any(f"open {app}" in query for app in app_paths):
            for app in app_paths:
                if f"open {app}" in query:
                    open_app(app, app_paths[app])
                    break

        elif 'close' in query:
            for app in [
                "notion", "vs code", "word", "excel", "notepad",
                "calculator", "chrome", "firefox", "whatsapp",
                "youtube", "telegram", "github", "google"
            ]:
                if f"close {app}" in query:
                    close_app(app)
                    break
            else:
                speak("Which app should I close sir?")

        elif 'shutdown spark' in query or 'spark shutdown' in query:
            speak("Goodbye sir. Call me anytime you need.")
            break

        elif 'spark' in query:
            speak("I'm here sir, always ready.")

if __name__ == "__main__":
    main()
