import cv2
import os
import face_recognition
import pickle
import numpy as np
import cvzone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("C:\\javascript tutorials\\service account key.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://face-attendance-89932-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-89932.appspot.com"
    })

bucket = storage.bucket()

cap= cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)


imgBackground = cv2.imread('C:\\javascript tutorials\\Resources\\background.png')
 
#importing the mode images into a list 
folderModePath = 'C:\\javascript tutorials\\Resources\\Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [ ]

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
#print(len(imgModeList))

#load the encoding file
print ("load encoding file...")
file = open("C:\\javascript tutorials\\EncodeFILE.p", 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentsIds)
print("Encode File Loaded")

modeType = 0
counter = 0 
id = -1
imgStudent =[]



while True:
    success, img = cap.read()
 
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)   


    imgBackground[162:162 + 480, 55:55 +640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceloc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        #print('matches', matches)
        #print('facedis', faceDis)

        matchIndex = np.argmin(faceDis)
        #print("Match Index",matchIndex)

        if matches[matchIndex]:
            #print("known face detected")
            #print(studentIds[matchIndex])
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            bbox = 55+x1,162+y1, x2-x1, y2-y1
            imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)
            id = studentIds[matchIndex]

            if counter == 0:
                counter = 1
                modeType = 1

    if  counter!= 0:
                
        if counter == 1: 
            #get the data     
            studentInfo = db.reference(f'Students/{id}').get()
            print(studentInfo)
            # Get the Images from the storage
            blob = bucket.get_blob(f'C:/javascript tutorials/Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(),np.uint8)
            imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)   

        cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),
                   cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1 )
        cv2.putText(imgBackground,str(studentInfo['major']),(1006,550),
                   cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1 )
        cv2.putText(imgBackground,str(id),(1006,493),
                    cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1) 
        cv2.putText(imgBackground,str(studentInfo['standing']),(910,625),
                    cv2.FONT_HERSHEY_COMPLEX,1,(100,100,100),1)
        cv2.putText(imgBackground,str(studentInfo['year']),(1025,625),
                    cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1 )
        cv2.putText(imgBackground,str(studentInfo['starting_year']),(1125,625),
        cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1 )
        
        
        (w,h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
        offset = (414-w)//2

        cv2.putText(imgBackground,str(studentInfo['name']),(808+offset,445),
                   cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1 )

         
        #imgBackground[175:175+216,909:909+216] = imgStudent



        counter+= 1    





    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
    
    
