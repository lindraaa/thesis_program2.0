import subprocess
import sys
import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import Label, Entry
import os
import util
from twilio.rest import Client
from drowsiness import DrowsinessDetectorApp
import sys
from sms_sender import send_sms
import pygame

import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.IN,pull_up_down=GPIO.PUD_OFF)
GPIO.setup(15,GPIO.IN,pull_up_down=GPIO.PUD_OFF)


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.center_window(self.main_window, 900, 300)
        self.main_window.title("Navigation System")
        
    def center_window(self, window, width, height):
        #center the window
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x_coordinate = (screen_width - width) // 2
        y_coordinate = (screen_height - height) // 2
#------------------------------------------------------
        window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

        self.login_button_main_window = util.get_button(self.main_window, 'Login ', 'navy blue', self.login)
        self.login_button_main_window.place(x=550, y=45)

        self.admin_access_main_window = util.get_button(self.main_window, 'Admin ', 'grey', self.admin, fg='black')
        self.admin_access_main_window.place(x=550, y=150)

        self.webcam_label = tk.Label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=400, height=280)
        self.add_webcam(self.webcam_label)
#--------------------------------------------------
        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.login_attempts = 0
        self.max_login_attempts = 2
    def start(self):
        self.main_window.mainloop()

    # def sms(self):
    #     # Your Twilio Account SID and Auth Token
    #     account_sid = 'ACe9f4b8ddf5fcdcdd909044427713a18a'
    #     auth_token = '1aa210647e5736e3c41845dcefd1bd27'
    #
    #     # Create a Twilio client
    #     client = Client(account_sid, auth_token)
    #
    #     # Your Twilio phone number and the recipient's phone number
    #     from_phone_number = '+18047939534'
    #     to_phone_number = '+639771136735'
    #
    #     # The message you want to send
    #     message = client.messages.create(
    #         body='Warning, Someone is attemting to start your car',
    #         from_=from_phone_number,
    #         to=to_phone_number
    #     )
    #
    #     # Print the message SID to confirm that it was sent successfully
    #     print(f"Message SID: {message.sid}")

    def login(self):
        if self.login_attempts >= self.max_login_attempts:
            util.msg_box('Access Blocked', 'Too many login attempts!')
            #send_sms()
            self.play_alarm()
            return

        unknown_img_path = './.tmp.jpg'
        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)
        
        try:
            output = str(subprocess.check_output(['face_recognition', self.db_dir, unknown_img_path]))
            
            if 'face_recognition.api' in output:
                util.msg_box('Error', 'Face recognition API error. Please try again.')
            elif 'no_persons_found' in output:
                self.login_attempts += 1
                util.msg_box('Login Failed',
                             'No face detected. Please try again. Attempt {} of {}.'.format(self.login_attempts, self.max_login_attempts))
            elif 'unknown_person' in output:
                self.login_attempts += 1
                util.msg_box('Login Failed',
                             'Unknown person. Please try again. Attempt {} of {}.'.format(self.login_attempts, self.max_login_attempts))
                
               
            else:
                self.login_attempts = 0  # Reset the login attempts on a successful login
                name = output.split(',')[1][:-5]
                util.msg_box('Starting Engine', 'Welcome, {}'.format(name))
                
                self.redirect_to_specific_file()
                
                
        except subprocess.CalledProcessError as e:
            util.msg_box('Error', 'Error during face recognition. Please try again.')

        os.remove(unknown_img_path)

    def play_alarm(self):
        pygame.mixer.init()
        pygame.mixer.music.load('car_alarm.mp3')
        pygame.mixer.music.play()
        pygame.time.wait(20000) 
        pygame.mixer.music.stop()
    
    def admin(self):
        self.admin_access_main_window = tk.Toplevel(self.main_window)
        self.admin_access_main_window.geometry("900x300")
        self.admin_access_main_window.title("Owner access only")

        custom_font = ("Helvetica bold", 20)
        input_font_size = 50
        title = Label(self.admin_access_main_window, text="ADMIN", font=custom_font)
        title.pack()

        self.username_label = Label(self.admin_access_main_window, text="Username", font=custom_font)
        self.username_label.pack()

        self.username_entry = Entry(self.admin_access_main_window, font=input_font_size)
        self.username_entry.pack()

        self.password_label = Label(self.admin_access_main_window, text="Password", font=custom_font)
        self.password_label.pack()

        self.password_entry = Entry(self.admin_access_main_window, font=input_font_size, show="*")
        self.password_entry.pack()

        self.access_button_main_window = util.get_button(self.admin_access_main_window, 'Login ', 'navy blue',self.login_access)
        self.access_button_main_window.place(x=550, y=50)
        self.access_button_main_window.pack()

    def login_access(self):
        entered_username = self.username_entry.get()
        entered_password = self.password_entry.get()

        if entered_username == "adminonly" and entered_password == "root_admin":
            print("Login Successfully")
            self.admin_access_main_window.destroy()
            self.new_tab()
        else:
            print("Login failed")

    def new_tab(self):
        custom_font = ("Helvetica bold", 20)
        font_username = ("Helvetica bold", 10)
        self.new_tab_main_window = tk.Toplevel(self.main_window)
        self.new_tab_main_window.geometry("900x300")
        self.new_tab_main_window.title("Admin Page")

        label = tk.Label(master=self.new_tab_main_window, text="Face Registration", font=custom_font)
        label.place(x=550, y=10)

        label2 = tk.Label(self.new_tab_main_window, text="Please input username", font=font_username)
        label2.place(x=580, y=70)

        self.accept_new_user_button = util.get_button2(self.new_tab_main_window, 'Capture', 'navy blue',
                                                       self.capture)
        self.accept_new_user_button.place(x=580, y=150)


        
        self.entry_name = Entry(self.new_tab_main_window)
        self.entry_name.place(x=580, y=100)

        self.new_capture_label = tk.Label(self.new_tab_main_window)
        self.new_capture_label.place(x=10, y=0, width=400, height=280)
        self.add_new_webcam_for_registration(self.new_capture_label)

        # Store the reference to the tab window
        self.tab_window = self.new_tab_main_window

        # Set a callback to be triggered when the tab window is closed
        self.tab_window.protocol("WM_DELETE_WINDOW", self.refresh_main_window)

    def refresh_main_window(self):
        if self.main_window.winfo_exists():
            self.main_window.destroy()
            self.__init__()  # Reinitialize the App object
            self.start()
    
    def open_drowsiness_window(self):
        drowsiness_window = tk.Toplevel(self.main_window)
        drowsiness_app = DrowsinessDetectorApp(drowsiness_window)


    def redirect_to_specific_file(self):
        file_path = 'starter.py'  # Provide the path to the file you want to redirect to
        try:
            # Run the specified file
            subprocess.Popen(['python', file_path])
        except Exception as e:
            print("Error:", e)
        finally:
            # Close the current Python process
            sys.exit()

#
    def add_new_webcam_for_registration(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self, _=None):
        ret, frame = self.cap.read()
        self.most_recent_capture_arr = frame

        img = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img)

        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def capture(self):
        name = self.entry_name.get()
        if not name:
            print("Please input your name")
            return

        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self.new_capture_label.imgtk = imgtk
        self.new_capture_label.configure(image=imgtk)

        cv2.imwrite(os.path.join(self.db_dir,'{}.jpg'.format(name)),self.most_recent_capture_arr)
        print("Image Captured and saved: ",name)
        self.accept_new_user_button.config(state=tk.NORMAL)
        # self.try_again_new_user_button.config(state=tk.NORMAL)

        util.msg_box('Success!' ,'User was registered successfully')
        #print("Success user was registered successfully! ")
        self.refresh_main_window()

if __name__ == '__main__':
    app = App()
    app.start()
    file_path = 'starter.py'
    app.redirect_to_specific_file(file_path)
