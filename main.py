import os
import time
import serial
import speech_recognition as sr
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from gtts import gTTS
from playsound import playsound
import pvporcupine
import pyaudio
import struct
import threading
from fuzzywuzzy import fuzz

# Ses tanıma ve Arduino bağlantısı
r = sr.Recognizer()
arduino = None
try:
    arduino = serial.Serial('COM13', 9600)
except Exception as e:
    print(f"Arduino bağlantısı sağlanamadı: {e}")

class BackgroundScreen(Screen):
    def __init__(self, **kwargs):
        super(BackgroundScreen, self).__init__(**kwargs)
        with self.canvas.before:
            self.bg = Image(source='.venv/image/arkap.jpg')
            self.bg.allow_stretch = True
            self.bg.keep_ratio = False
            self.bg.pos = self.pos
            self.bg.size = self.size
            self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class MainScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        ana_layout = FloatLayout()

        buton_layout = BoxLayout(size_hint=(0.8, None), height=50, spacing=10, orientation='horizontal')
        buton_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.6}

        motor_buton = Button(text='Motorlar', size_hint=(0.4, None), height=100)
        motor_buton.bind(on_press=self.go_to_motors)

        led_buton = Button(text='LEDler', size_hint=(0.4, None), height=100)
        led_buton.bind(on_press=self.go_to_leds)

        buton_layout.add_widget(motor_buton)
        buton_layout.add_widget(led_buton)

        sesli_komut_buton = Button(text='Sesli Komut', size_hint=(0.5, None), height=50)
        sesli_komut_buton.bind(on_press=self.go_to_voice_command)
        sesli_komut_buton.pos_hint = {'center_x': 0.5, 'center_y': 0.3}

        ana_layout.add_widget(buton_layout)
        ana_layout.add_widget(sesli_komut_buton)

        self.add_widget(ana_layout)

    def go_to_motors(self, instance):
        self.manager.current = 'motor_screen'

    def go_to_leds(self, instance):
        self.manager.current = 'led_screen'

    def go_to_voice_command(self, instance):
        self.manager.current = 'voice_screen'

class MotorScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super(MotorScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        motor1_left_button = Button(text='1. Motor Sol', size_hint=(1, None), height=50)
        motor1_right_button = Button(text='1. Motor Sağ', size_hint=(1, None), height=50)
        motor2_left_button = Button(text='2. Motor Sol', size_hint=(1, None), height=50)
        motor2_right_button = Button(text='2. Motor Sağ', size_hint=(1, None), height=50)

        motor1_left_button.bind(on_press=lambda x: self.send_to_arduino('a'))
        motor1_right_button.bind(on_press=lambda x: self.send_to_arduino('d'))
        motor2_left_button.bind(on_press=lambda x: self.send_to_arduino('f'))
        motor2_right_button.bind(on_press=lambda x: self.send_to_arduino('g'))

        back_button = Button(text='Geri', size_hint=(1, None), height=50)
        back_button.bind(on_press=self.go_to_main)

        layout.add_widget(motor1_left_button)
        layout.add_widget(motor1_right_button)
        layout.add_widget(motor2_left_button)
        layout.add_widget(motor2_right_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_to_main(self, instance):
        self.manager.current = 'main_screen'

    def send_to_arduino(self, command):
        if arduino:
            try:
                arduino.write(command.encode())
            except Exception as e:
                print(f"Komut gönderilirken hata: {e}")
        else:
            print('Arduino bağlantısı yok')

class LEDScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super(LEDScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        led1_yellow_button = Button(text='1. LED Sarı', size_hint=(1, None), height=50)
        led1_red_button = Button(text='1. LED Kırmızı', size_hint=(1, None), height=50)
        led1_blue_button = Button(text='1. LED Mavi', size_hint=(1, None), height=50)
        led1_green_button = Button(text='1. LED Yeşil', size_hint=(1, None), height=50)

        led2_yellow_button = Button(text='2. LED Sarı', size_hint=(1, None), height=50)
        led2_red_button = Button(text='2. LED Kırmızı', size_hint=(1, None), height=50)
        led2_blue_button = Button(text='2. LED Mavi', size_hint=(1, None), height=50)
        led2_green_button = Button(text='2. LED Yeşil', size_hint=(1, None), height=50)

        led1_yellow_button.bind(on_press=lambda x: self.send_to_arduino('p'))
        led1_red_button.bind(on_press=lambda x: self.send_to_arduino('h'))
        led1_blue_button.bind(on_press=lambda x: self.send_to_arduino('k'))
        led1_green_button.bind(on_press=lambda x: self.send_to_arduino('j'))

        led2_yellow_button.bind(on_press=lambda x: self.send_to_arduino('w'))
        led2_red_button.bind(on_press=lambda x: self.send_to_arduino('x'))
        led2_blue_button.bind(on_press=lambda x: self.send_to_arduino('z'))
        led2_green_button.bind(on_press=lambda x: self.send_to_arduino('y'))

        back_button = Button(text='Geri', size_hint=(1, None), height=50)
        back_button.bind(on_press=self.go_to_main)

        layout.add_widget(led1_yellow_button)
        layout.add_widget(led1_red_button)
        layout.add_widget(led1_blue_button)
        layout.add_widget(led1_green_button)
        layout.add_widget(led2_yellow_button)
        layout.add_widget(led2_red_button)
        layout.add_widget(led2_blue_button)
        layout.add_widget(led2_green_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_to_main(self, instance):
        self.manager.current = 'main_screen'

    def send_to_arduino(self, command):
        if arduino:
            try:
                arduino.write(command.encode())
            except Exception as e:
                print(f"Komut gönderilirken hata: {e}")
        else:
            print('Arduino bağlantısı yok')

class VoiceCommandScreen(BackgroundScreen):
    def __init__(self, **kwargs):
        super(VoiceCommandScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.label = Label(text='Nasıl yardımcı olabilirim?')
        self.voice_button = Button(text='Sesli Komut', size_hint=(1, None), height=50)
        self.voice_button.bind(on_press=self.voice_command)

        back_button = Button(text='Geri', size_hint=(1, None), height=50)
        back_button.bind(on_press=self.go_to_main)

        layout.add_widget(self.label)
        layout.add_widget(self.voice_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def speak(self, text):
        tts = gTTS(text=text, lang='tr')
        tts.save("response.mp3")
        playsound("response.mp3")
        os.remove("response.mp3")

    def voice_command(self, instance):
        self.speak("Komutları dinliyorum")
        while True:
            with sr.Microphone() as source:
                print("Dinleniyor...")
                audio = r.listen(source)
                try:
                    command = r.recognize_google(audio, language='tr-TR')
                    print(f"Komut: {command}")
                    if fuzz.ratio('televizyonu yukarı kaldır', command) >= 80:
                        self.send_to_arduino('a')
                        self.speak("televizyon yukarı kalkıyor")
                        break
                    elif fuzz.ratio('televizyonu aşağı indir', command) >= 80:
                        self.send_to_arduino('d')
                        self.speak("televizyon aşağı iniyor")
                        break
                    elif fuzz.ratio('sehpayı yukarı kaldır', command) >= 80:
                        self.send_to_arduino('f')
                        self.speak("sehpa yukarı kalkıyor")
                        break
                    elif fuzz.ratio('sehpayı aşağı indir', command) >= 80:
                        self.send_to_arduino('g')
                        self.speak("sehpa aşağı iniyor")
                        break
                    elif fuzz.ratio('tavan ışığını kırmızı yap', command) >= 80:
                        self.send_to_arduino('h')
                        self.speak("tavan ışığı kırmızı oldu")
                    elif fuzz.ratio('tavan ışığını sarı yap', command) >= 80:
                        self.send_to_arduino('p')
                        self.speak("tavan ışığı sarı oldu")
                    elif fuzz.ratio('tavan ışığını mavi yap', command) >= 80:
                        self.send_to_arduino('k')
                        self.speak("tavan ışığı mavi oldu")
                    elif fuzz.ratio('tavan ışığını yeşil yap', command) >= 80:
                        self.send_to_arduino('j')
                        self.speak("tavan ışığı yeşil oldu")
                    elif fuzz.ratio('alt ışıkları mavi yap', command) >= 80:
                        self.send_to_arduino('z')
                        self.speak("alt ışıklar mavi oldu")
                    elif fuzz.ratio('alt ışıkları sarı yap', command) >= 80:
                        self.send_to_arduino('w')
                        self.speak("alt ışıklar sarı oldu")
                    elif fuzz.ratio('alt ışıkları kırmızı yap', command) >= 80:
                        self.send_to_arduino('x')
                        self.speak("alt ışıklar kırmızı oldu")
                    elif fuzz.ratio('alt ışıkları yeşil yap', command) >= 80:
                        self.send_to_arduino('y')
                        self.speak("alt ışıklar yeşil oldu")
                    elif fuzz.ratio('tamam', command) >= 80:
                        self.speak("Görüşürüz")
                        self.manager.current = 'main_screen'
                        break
                except sr.UnknownValueError:
                    print("Anlaşılamadı")
                except sr.RequestError as e:
                    print(f"API hatası: {e}")

    def send_to_arduino(self, command):
        if arduino:
            try:
                arduino.write(command.encode())
            except Exception as e:
                print(f"Komut gönderilirken hata: {e}")
        else:
            print('Arduino bağlantısı yok')

    def go_to_main(self, instance):
        self.manager.current = 'main_screen'

class MyKivyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(MotorScreen(name='motor_screen'))
        sm.add_widget(LEDScreen(name='led_screen'))
        sm.add_widget(VoiceCommandScreen(name='voice_screen'))

        threading.Thread(target=self.run_porcupine, daemon=True).start()

        return sm

    def run_porcupine(self):
        access_key = 'D0GdKc42Ioe7ij/evYyLj8jqyViGR3tOVBid7YnJbmAI1ksoCbEZ9g=='  # Buraya kendi Porcupine erişim anahtarınızı yazın
        keyword_path = 'hey-dirt-ix_en_windows_v3_0_0.ppn'  # Buraya kendi .ppn dosyanızın yolunu yazın

        porcupine = None
        pa = None
        audio_stream = None

        try:
            porcupine = pvporcupine.create(access_key=access_key, keyword_paths=[keyword_path])

            pa = pyaudio.PyAudio()

            audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length)

            while True:
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    print("Hotword detected!")
                    # GUI değişikliğini ana iş parçacığında yap
                    Clock.schedule_once(self.on_hotword_detected)
        except Exception as e:
            print(f"Porcupine çalıştırılırken hata: {e}")
        finally:
            if audio_stream is not None:
                audio_stream.close()

            if pa is not None:
                pa.terminate()

            if porcupine is not None:
                porcupine.delete()

    def on_hotword_detected(self, dt):
        # Sesli komut ekranına geç ve voice_button'ı tetikle
        self.root.current = 'voice_screen'
        self.root.get_screen('voice_screen').voice_command(None)

if __name__ == '__main__':
    MyKivyApp().run()
