import cv2
import easyocr
from gpiozero import LED
from time import sleep
import glob
import os
import datetime
import sqlite3


cam=cv2.VideoCapture(0)
cam.set(3,640)
cam.set(4,480)
min_area=500
count=0

list_of_files=glob.glob('/home/raspi/plates/*')
latest_file=max(list_of_files, key=os.path.getctime)
led= LED(17)
reader=easyocr.Reader(['ch_sim','en'])
harcascade="/home/raspi/model/haarcascade_russian_plate_number.xml"

cars = []
carsEntry = []
carsExit=[]
while True:
    success, img= cam.read()
    plate_cascade=cv2.CascadeClassifier(harcascade)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    plates=plate_cascade.detectMultiScale(gray,1.1,4)
    
    for (x, y, w,h) in plates:
        area = w * h
        
        if area > min_area:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(img,"test", (x,y-5),cv2.FONT_HERSHEY_COMPLEX_SMALL,1, (255,0,255),2)
        
        img_roi=img[y: y+h,x:x+w]
        cv2.imshow("Roi",img_roi)        
        cv2.imwrite("/home/raspi/plates/plate_"+str(count)+".jpg", img_roi)        
##        cv2.imshow("Result",img)
        resut=reader.readtext(latest_file)
        text=resut[0][-2]
        
        cars.append(text)
        carsEntry.append([datetime.datetime.now(),text])
        a=datetime.datetime.now()
#same code as above for exit code with the difference below and on a seperate camera

    cars.append(text)
    carsExit.append([datetime.datetime.now(),text])
    b=datetime.datetime.now()

#comparison for fines and to calculate how long the user stayed in the car park
    
def time_to_num(time_str):
    hh,mm,ss=map(a,time.str.split(':'))
    hh1,mm1,ss1=map(b,time.str.split(':'))
    return ss1 + 60*(mm1+60*hh1)
    
    while 'hh1' 'mm1' 'ss1'>'hh' 'mm' 'ss':
        statement("Parking is valid")
    
    total='hh1-hh','mm1-mm','ss1-ss'
    if total>='6' '15' '00':
        print("you have been fined £15")


cv2.waitKey(0)
count += 1


    
#        for _ in range(6_00_15):
#            print("parking is valid")
#            total=b-a
#            if total>_:
#                print("you will be fined £15.")

        

#        print(text)
#        a=input("Input your number plate:")
#        if a==text:
#            led.on()
#            print(a,"is parked")
#        else:
#            print("invalid/unreadable")
#            led.off()
#        print(cars)
#        print(carsEntry)
#        print(carsExit)


##while True:#
##    now=datetime()


##    if cv2.waitKey(10) & 0xFF == ord('s'):
##        cv2.imwrite("/home/raspi/plates/plate_"+str(count)+".jpg", img_roi)
        #cv2.rectangle(img,(0,200), (640,300),(0,255,0),cv2.FILLED)
        #cv2.imshow("Results",img_roi)    

    
##elif len(text)<5 or len(text)>10:
  #  led.on()
   # led.off()
  #  print(text,'is an invalid number plate')
  #  sleep(2)
    
    
    
    
    
