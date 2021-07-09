
from __future__ import print_function
import PIL
from PIL import ImageTk
from PIL import Image
import tkinter as tki
import screen_brightness_control as sbc
import threading
import datetime
import imutils
import cv2
from handDetector import HandDetector
import os
import math 
import numpy as np

class PhotoBoothApp:
	def __init__(self, vs, outputPath):
		
		self.vs = vs
		self.outputPath = outputPath
		self.frame = None
		self.thread = None
		self.stopEvent = None
		
		self.root = tki.Tk()
		self.panel = None
		


		l = tki.Label(self.root, bg='white', fg='black', width=20, text='empty')
		l.pack()



		def print_selection(v):
			sbc.set_brightness(v)
			l.config(text='Brightness value ' + v)

		self.s = tki.Scale(self.root, label='Brightness', from_=0, to=100, orient=tki.HORIZONTAL, length=300, showvalue=0,tickinterval=20, resolution=5,command=print_selection)

		self.s.pack(side="bottom", fill="both", expand="yes", padx=5,pady=5)

		
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()
		self.root.wm_title("Brightness Controller")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)


	def videoLoop(self):
		handDetector = HandDetector(min_detection_confidence=0.5)
		try:
			while not self.stopEvent.is_set():



				handLandmarks = handDetector.findHandLandMarks(image=self.vs.read(), draw=True)

				if(len(handLandmarks) != 0):
        
					x1, y1 = handLandmarks[4][1], handLandmarks[4][2]
					x2, y2 = handLandmarks[8][1], handLandmarks[8][2]
					length = math.hypot(x2-x1, y2-y1)
					
					volumeValue = np.interp(length, [0, 100], [-150, 0.0])
					self.s.set(int(abs(volumeValue)))
					
					cv2.circle(self.vs.read(), (x1, y1), 15, (255, 0, 255), cv2.FILLED)
					cv2.circle(self.vs.read(), (x2, y2), 15, (255, 0, 255), cv2.FILLED)
					cv2.line(self.vs.read(), (x1, y1), (x2, y2), (255, 0, 255), 3)


				self.frame = self.vs.read()
				self.frame = imutils.resize(self.frame, width=800)

				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)
				if self.panel is None:
					self.panel = tki.Label(image=image)
					self.panel.image = image
					self.panel.pack(side="left", padx=10, pady=10)
				else:
					self.panel.configure(image=image)
					self.panel.image = image
    				
		except RuntimeError:
			print("[INFO] caught a RuntimeError")

	# def takeSnapshot(self):
	# 	ts = datetime.datetime.now()
	# 	filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
	# 	p = os.path.sep.join((self.outputPath, filename))

	# 	cv2.imwrite(p, self.frame.copy())
	# 	print("[INFO] saved {}".format(filename))


	def onClose(self):
		print("[INFO] closing...")
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()