import face_recognition
import os
import sys
import cv2
import numpy as np
import math
from PIL import ImageGrab
import pyautogui
import imutils
import time
import smtplib
from email.message import EmailMessage
import ssl
import imghdr
import pygetwindow
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import random
import string

email_sender = 'buerenn123@gmail.com'
email_password = 'cwjadzsykfodeltz'
email_reciever = 'burak.cakmaktas@istanbulticaret.edu.tr'


def select_image():
    file_path = filedialog.askopenfilename(title="Select Image", filetypes=(("JPEG Files", "*.jpg"), ("PNG Files", "*.png")))
    if file_path:
        image = Image.open(file_path)
        filename = os.path.basename(file_path)  # Get the filename from the selected path
        destination_file = "faces/" + filename  # Path and name of the target file to save
        image.save(destination_file)
        print("Image saved:", destination_file)
        











def face_confidence(face_distance, face_match_treshold=0.6):
    range = (1.0 - face_match_treshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_treshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) *
                 math.pow((linear_val - 0.5) * 2, 0.2)))
        return str(round(value, 2)) + '%'


class FaceRecognition:

    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()
    # encode faces

    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file(f'faces/{image}')
            face_encoding = face_recognition.face_encodings(face_image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)

            print(self.known_face_names)

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit('Video source not found')

        while True:
            ret, frame = video_capture.read()

            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                # cv2de blue green red diye gidiyor, biz onu rgbye çevirdik

                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = 'Unknown'
                    confidence = 'Unknown'

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(
                            face_distances[best_match_index])

                    if name == 'Unknown':
                        pyautogui.screenshot("Stranger At Door.png")
                        subject = 'Intruder Alert'
                        body = """
                        Intruder photo : 
                        """

                        em = EmailMessage()
                        em['From'] = email_sender
                        em['To'] = email_reciever
                        em['Subject'] = subject
                        em.set_content(body)

                        context = ssl.create_default_context()

                        with open('Stranger At Door.png', 'rb') as f:
                            image_data = f.read()
                            image_type = imghdr.what(f.name)
                            image_name = f.name

                        em.add_attachment(
                            image_data, maintype='image', subtype=image_type, filename=image_name)

                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                            smtp.login(email_sender, email_password)
                            smtp.sendmail(
                                email_sender, email_reciever, em.as_string())
                        time.sleep(3)

                    self.face_names.append(f'{name} ({confidence})')

            self.process_current_frame = not self.process_current_frame

            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top),
                              (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35),
                              (right, bottom), (0, 0, 255), -1)
                cv2.putText(frame, name, (left+6, bottom-6),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    
    fr = FaceRecognition()
    window = tk.Tk()
    window.title("Security Camera")
    window.geometry("800x600")
    window.configure(bg="black")
    

    button = tk.Button(window, text="Select Image", command=select_image)
    button.pack(pady=20)
    
    button3 = tk.Button(window, text="Encode Faces", command=lambda : fr.encode_faces())
    button3.pack(pady=20)
    
    button2 = tk.Button(window, text="Run Recognition", command=lambda : fr.run_recognition())
    button2.pack(pady=20)
    
    window.mainloop()
    
    
    
    
    

    
    
    
    
    
    
    
