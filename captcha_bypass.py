import os 
import random 
import time
import speech_recognition as sr 
import urllib 
import pydub
from selenium.webdriver.common.keys import Keys 
import undetected_chromedriver.v2 as uc
from unidecode import unidecode

def delay():
    time.sleep(random.randint(2,3))

def audio_to_text(audio_source):
    #Get audio source
    urllib.request.urlretrieve(audio_source, os.getcwd()+"\\sample.mp3")
    sound = pydub.AudioSegment.from_mp3(os.getcwd()+"\\sample.mp3") 
    sound.export(os.getcwd()+"\\sample.wav", format="wav") 
    AUDIO_FILE = os.getcwd()+"\\sample.wav"

    # Translate audio to text  
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  
    phrase=r.recognize_sphinx(audio)
    print("[INFO] Recaptcha Passcode: %s"%phrase)

    return phrase

def bypass_captcha(url):
    options = uc.ChromeOptions()
    # Uncomment this two lines if you want to run the script in headless mode
    #options.headless=True
    #options.add_argument('--headless')

    # Chromedriver fix for docker
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    data_ssalud = None
    is_captcha_solved = False
    # Set this text according to the language of your Chrome Navigator
    successText = 'Tu verificación se ha completado.'
    #successText = 'You are verified'

    delay()
    driver.get(url)
    
    try:
        frame_captcha=driver.find_elements_by_tag_name("iframe") 
        driver.switch_to.frame(frame_captcha[0]) 
    except Exception as e:
        print(e)
        driver.close()
        print('[WARNING] Caught. Need to change ip')
        return data_ssalud
    delay()

    #click on checkbox to activate recaptcha 
    driver.find_element_by_class_name("recaptcha-checkbox-border").click()
    delay()
    recaptchaStatus = driver.find_element_by_id("recaptcha-accessible-status").get_attribute('innerText')
    print(f'[INFO] Recaptha Status: {recaptchaStatus}')

    if  unidecode(recaptchaStatus) == unidecode(successText):
        print('[INFO] No advance captcha. Very unlikely')
        is_captcha_solved = True
    else:
        #switch to recaptcha audio control frame 
        driver.switch_to.default_content() 
        # The xpath could change, set it according to your target
        frames=driver.find_elements_by_tag_name("iframe")
        print(frames) 
        driver.switch_to.frame(frames[2]) 
        delay()
        #click on audio challenge 
        driver.find_element_by_id("recaptcha-audio-button").click()
        
        # Sometimes it has to solve the audio challenge many times
        while not is_captcha_solved:
        #switch to recaptcha audio challenge frame 
            driver.switch_to.default_content() 
            frames= driver.find_elements_by_tag_name("iframe") 
            driver.switch_to.frame(frames[-1]) 
            delay()
            
            try:
                #click on the play button
                driver.find_element_by_xpath("/html/body/div/div/div[3]/div/button").click()
            except Exception as e:
                print(e)
                driver.close()
                print('[WARNING] Bot Caught. Need to change ip')
                return data_ssalud

            #get the mp3 audio file 
            src = driver.find_element_by_id("audio-source").get_attribute("src") 
            print("[INFO] Audio src: %s"%src)

            # Transform audio to text
            passcode = audio_to_text(src)
            
            #key in results and submit 
            driver.find_element_by_id("audio-response").send_keys(passcode.lower()) 
            driver.find_element_by_id("audio-response").send_keys(Keys.ENTER) 
            driver.switch_to.default_content()
            delay()
            driver.switch_to.default_content()
            frame_captcha=driver.find_elements_by_tag_name("iframe")  
            driver.switch_to.frame(frame_captcha[0])
            recaptchaStatus = driver.find_element_by_id("recaptcha-accessible-status").get_attribute('innerText')
            print(f'[INFO] Recaptha Status: {recaptchaStatus}')

            if unidecode(recaptchaStatus) == unidecode(successText) :
                print('[INFO] Congratulations!. Captcha Solved')
                is_captcha_solved = True
            
    driver.switch_to.default_content()
    driver.find_element_by_id("recaptcha-demo-submit").click() 
    delay()
    message = driver.find_element_by_class_name("recaptcha-success").get_attribute('innerText')
    driver.close()
    return message

message = bypass_captcha('https://www.google.com/recaptcha/api2/demo')
print (message)