import tkinter as tk
import cv2
import sys
import requests
import numpy as np
import matplotlib.pyplot as  plt
import matplotlib.image as mpimg
from tkinter import filedialog as fd
from pylab import figure, axes, pie, title, show
import json



root = tk.Tk() 
root.geometry("500x250")
frame = tk.Frame(root)
frame.pack()
bottomframe =tk.Frame(root)
bottomframe.pack( side = tk.BOTTOM )

L1 = tk.Label(frame, text="Enter the Location file: ")
L1.pack( side = tk.LEFT)
e1 = tk.Entry(frame,bd =5, width=150)
e1.pack(side = tk.RIGHT)

uri_base = 'https://westcentralus.api.cognitive.microsoft.com'
    # Request headers.
headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '9bc708b0763b43bf837d4c9296fc9f67',
    }
    # Request parameters.
params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    }

def loadFile(e1):
    filename = fd.askopenfilename()
    if(e1.get)=="":
        e1.insert(0,str(filename))
    else:
       clear_text(e1)
       e1.insert(0,str(filename))
def clear_text(self):
    self.delete(0, 'end')    
def detectFile():
    file = e1.get()
    print("abc",file)
    image = cv2.imread(file)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    print("[INFO] Found {0} Faces!".format(len(faces)))
    resized_img = ""
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_color = image[y:y + h, x:x + w] 
        print("[INFO] Object found. Saving locally.") 
        cv2.imwrite(str(w) + str(h) + '_faces.jpg', roi_color) 
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),thickness=7)
        resized_img = cv2.resize(image, (1000, 700))
        img=mpimg.imread(str(w) + str(h) + '_faces.jpg')

        plt.imshow(img)
        plt.show()
        print("Result Detection") 
        plt.imshow(resized_img)
        
    f = open(e1.get(), "rb")
    body = f.read()
    f.close()
    body = body
 
    try:
        # Execute the REST API call and get the response.
        response = requests.request('POST', uri_base + '/face/v1.0/detect', data=body, headers=headers,
                                    params=params)
        print ('Response:')
        parsed = json.loads(response.text)
        print (json.dumps(parsed, sort_keys=True, indent=2))
    
    except Exception as e:
        print('Error:')
        print(e)

            
btnLoadFile = tk.Button(root, text='Load File', width=15, command = lambda: loadFile(e1)) 
btnDetect = tk.Button(root, text='Detect File', width=15, command = detectFile) 
btnLoadFile.pack(side=tk.LEFT)
btnDetect.pack(side=tk.RIGHT)
tk.mainloop()
