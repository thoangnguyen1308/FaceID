import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import matplotlib.pyplot as  plt
import requests
import json
import os
import numpy as np
from aaa import CFEVideoConf, image_resize

class App:
     def __init__(self, window, window_title, video_source=0):
         self.window = window
         self.window.title(window_title)
         self.video_source = video_source
 
         # open video source (by default this will try to open the computer webcam)
         self.vid = MyVideoCapture(self.video_source)
 
         # Create a canvas that can fit the above video source size
         self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
         self.canvas.pack()
        
         # Button that lets the user take a snapshot
         self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
         self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
 
         # After it is called once, the update method will be automatically called every delay milliseconds
         self.delay = 15
         self.update()
 
         self.window.mainloop()
 
     def snapshot(self):
         # Get a frame from the video source
         ret, frame = self.vid.get_frame()
         
         if ret:
             cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
 
     def update(self):
         # Get a frame from the video source
         ret, frame = self.vid.handle()
 
class MyVideoCapture:
    def __init__(self, video_source=0):
         # Open the video source
         self.vid = cv2.VideoCapture(video_source)
         self.vid.set(3, 640) # set video width
         self.vid.set(4, 480) # set video height
         
         if not self.vid.isOpened():
             raise ValueError("Unable to open video source", video_source)
 
         # Get video source width and height
         self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
         self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
 
    def get_frame(self):
         if self.vid.isOpened():
             ret, frame = self.vid.read()
             if ret:
                 # Return a boolean success flag and the current frame converted to BGR
                 return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
             else:
                 return (ret, None)
         else:
             return (ret, None)
 
     # Release the video source when the object is destroyed
    def __del__(self):
         if self.vid.isOpened():
             self.vid.release()
    def handle(self):
        #face_detector = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('UI/trainingData.yml')
        face_detector = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_frontalface_default.xml')
        eyeCascade = cv2.CascadeClassifier('Cascades/haarcascade_eye.xml')
        smileCascade = cv2.CascadeClassifier('Cascades/haarcascade_smile.xml')
        #faceCascade = cv2.CascadeClassifier(cascadePath);
        save_path ='dataset/aaa.mp4'
        frames_per_seconds = 24
        config = CFEVideoConf(self.vid, filepath=save_path, res='720p')
        out = cv2.VideoWriter(save_path, config.video_type, frames_per_seconds, config.dims)
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        face_id = input('\n enter user id end press <return> ==>  ')
        names = ['None', 'Marcelo', 'Paula', 'Ilza', 'Z', 'W']
        minW = 0.1*self.vid.get(3)
        minH = 0.1*self.vid.get(4)
        glasses = cv2.imread('glasses.png',1)
        while(True):
            ret, image_frame = self.vid.read()
            image_frame = cv2.flip(image_frame, 1)
            gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize = (int(minW), int(minH)),
                flags=cv2.CASCADE_SCALE_IMAGE
                )
            # Loops for each faces
            for (x,y,w,h) in faces:

                #cv2.rectangle(image_frame, (x,y), (x+w,y+h), (0,255,0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = image_frame[y:y+h, x:x+w]
                face_id, confidence = recognizer.predict(gray[y:y+h,x:x+w])       
                # Save the captured image into the datasets folder
                
                eyes = eyeCascade.detectMultiScale(
                    roi_gray,
                    scaleFactor= 1.5,
                    minNeighbors=5,
                    #minSize = (int(minW), int(minH)),
                    )
                for (ex, ey, ew, eh) in eyes:
                    #cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                     roi_eyes = roi_gray[ey: ey + eh, ex: ex + ew]
                     glasses = image_resize(glasses, width=ew)
                     gw, gh, gc = glasses.shape
                     for i in range(0, gw):
                         for j in range(0, gw):
                             print(glasses[i,j])
                             if glasses[i,j][2] != 0:
                                 roi_color[ey +i, ex + j] = glasses[i,j]
        
                smile = smileCascade.detectMultiScale(
                    roi_gray,
                    scaleFactor= 1.5,
                    minNeighbors=15,
                    minSize=(25, 25),
                    )
                
                for (xx, yy, ww, hh) in smile:
                    cv2.rectangle(roi_color, (xx, yy), (xx + ww, yy + hh), (0, 255, 0), 2)
                
                if (confidence < 100):
                    #face_id = names[face_id]
                    confidence = "  {0}%".format(round(100 - confidence))
                else:
                    face_id = "unknown"
                    confidence = "  {0}%".format(round(100 - confidence))

                cv2.putText(image_frame, str(face_id), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(image_frame, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
                out.write(image_frame)
                cv2.imshow('camera',image_frame)
            # To stop taking video, press 'q' for at least 100ms
                if cv2.waitKey(30) & 0xff == ord('q') : # press 'ESC' to quit
                    break
# Create a window and pass it to the Application object
root = tkinter.Tk()
root.geometry("600x512")
App(root, "Tkinter and OpenCV")
