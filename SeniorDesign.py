import cv2
import move as m
import io
from picamera       import PiCamera
from picamera.array import PiRGBArray
import picamera
import time
import numpy
import ultra as ut
import RPIservo as rp

stack1 = []
stack2 = []
stack3 = []
moving = 0
stream = io.BytesIO()
pickup = 0
obj = []
return1 = 0
found = 0
trans =0
pos = 0
count = 0
count1 =0
pos2 = 0
numx = 250
numz = 0
dist = 100
approached = 0
flag = 0
str1 = 'bottle'
complete = 0
check = 0
stuck = 0

camera = PiCamera()
camera.resolution= (640,480)
camera.framerate = 16
rawCapture = PiRGBArray(camera, size = (640,480))
time.sleep(1.0)

thres = 0.45 # Threshold to detect object
#img = cv2.imdecode(buff,1)#img = cv2.imdecode(buff,1) #cv2.imread("/home/pi/Desktop/Object_Detection_Files/lena.PNG")
#classNames = ['person', 'bottle', 'cup', 'banana', 'apple', 'orange', 'broccoli','carrot']
classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")


configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)



    
    

def getObjects(img, thres, nms, draw=True, objects=[]): # Draw box print name and conf level
    
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    return img,objectInfo


if __name__ == "__main__":
    
    m.setup()
    m.destroy()
    speed_set = 60
    sc = rp.ServoCtrl()
    sc.start()
    sc.moveAngle(1,(pos))
    sc.moveAngle(0,(pos2))
    sc.moveAngle(2,(pos))
    sc.moveAngle(3,(pos2))
    sc.moveAngle(4,(pos2))
    
        
        
        
    
    for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        img = frame.array



        if return1 == 1: # if bottle is secured return to orgin
            found = -1
            m.setup()
            m.motorStop()
            m.destroy()
  
            while stack1:
                moving = 1
                sc.moveAngle(0,(stack3.pop()))
                time.sleep(.5)
                m.setup()
                m.move(speed_set, stack1.pop(), 'no', 0.8)
                time.sleep(stack2.pop())
                m.motorStop()
                time.sleep(.5)
                m.destroy()
            else:       # drop bottle and return to original state
                check = 0
                return1 =0
                check1 = 0
                complete = 0
                
                sc.moveAngle(2,(40))
                time.sleep(.5)
                sc.moveAngle(3,(80))
                time.sleep(1)
                sc.moveAngle(4,(60))
                time.sleep(2)
                sc.moveAngle(1,(0))
                sc.moveAngle(0,(0))
                sc.moveAngle(2,(0))
                sc.moveAngle(3,(0))
                sc.moveAngle(4,(0))
                time.sleep(3)
                
                           
        result, objectInfo = getObjects(img,thres,0.1,objects=[str1])
        print(objectInfo)
        

        if objectInfo:

            found = 5
            obj = objectInfo[0][0]
            numx = obj[0]
            numy = obj[1]
            numz = obj[2]
        else:
            
            trans = 0
            found = found - 1
            numx = 250
            numz = 100
            print(found)
            
  

        if found < 0: # search and scan
            m.setup()
            m.motorStop()
            m.destroy()
            approached = 0
            if flag == 0:  
                pos = pos - 7
            if flag == 1:
                pos = pos + 7
            
       
            if complete == 2:
                
                if check < 2:
                    
                    
                    if ut.checkdist() > 0.3:
                        sc.moveAngle(0,(0))
                        time.sleep(.5)
                        m.setup()
                        m.move(speed_set, 'backward', 'no', 0.8)
                        time.sleep(0.8)
                        m.motorStop()
                        time.sleep(1)
                        m.destroy()
                        stack1.append('forward')
                        stack2.append(0.8)
                        stack3.append(0)
                        complete = 0
                        count1 = 0
                        check = check +1
                    else:
                        complete = 0
                        count1 = 0
                        check = 0
                        m.setup()
                        sc.moveAngle(0,(40))
                        m.move(speed_set, 'forward', 'no', 0.8)                    
                        time.sleep(0.8)
                        sc.moveAngle(0,(0))
                        m.motorStop()
                        m.destroy()
                
                
                elif check == 2:
                        
                    
                    
                    if ut.checkdist() > 0.3:
                        
                        sc.moveAngle(0,(-40)) 
                        time.sleep(.5)
                        m.setup()
                        m.move(speed_set, 'backward', 'no', 0.8)
                        time.sleep(1.5)
                        m.motorStop()
                        time.sleep(1)
                        m.destroy()
                        stack1.append('forward')
                        stack2.append(1.5)
                        stack3.append(-40)
                        complete = 0
                        count1 = 0

                    elif ut.checkdist() < 0.3: 
                        complete = 0
                        count1 = 0
                        check = 0        
                        m.setup()
                        sc.moveAngle(0,(40))
                        m.move(speed_set, 'forward', 'no', 0.8)                    
                        time.sleep(1.0)
                        m.motorStop()
                        m.destroy()
                        sc.moveAngle(0,(0))
                        stack1.append('backward')
                        stack2.append(1.0)
                        stack3.append(40)

                        
           
    
        else:
            if moving == 0:
                pos2 = pos *1.5
                print('1',pos2)
            complete = 0
            if numx < 260 and not pickup and numy > 100:   # ceter camera on object
                
                pos= pos + 2
                pos2= pos2 + 4            
            elif numx > 290 and not pickup and numy > 100:
                pos = pos - 2
                pos2= pos2 - 4
        
            if numz < dist and numx > 50 and numx < 500 and numy > 100:  # begin moving closer to object
                stuck = 0
                moving = 1
                m.setup()
                if ut.checkdist() > 0.3:
                    if numx > 290:
                        pos2 = pos - (20-(numx/35))
                        pos2 = pos2 +((100 - numz)/3)
                        sc.moveAngle(0,(pos2))
                        time.sleep(1.0)
                        print('2',pos2)
                    elif numx < 260:
                        pos2 = pos + (20 -(numx/35))
                        pos2 = pos2 -((100 - numz)/3)
                        sc.moveAngle(0,(pos2))
                        time.sleep(1.5)
                    else:
                        sc.moveAngle(0,(pos))
                        time.sleep(1.0)
                    
                    tim = (dist - numz)/50
                    print('x',tim)
                    print('y',pos2)
                    m.setup()
                    m.move(speed_set, 'backward', 'no', 0.8)
                    time.sleep(tim)
                    m.motorStop()
                    m.destroy()
                    stack1.append('forward')
                    stack2.append(tim)
                    stack3.append(pos2)
                    
                    moving = 0
                elif ut.checkdist() < 0.3:
                    m.setup()
                    sc.moveAngle(0,(40))
                    m.move(speed_set, 'forward', 'no', 0.8)
                    time.sleep(1.0)
                    m.motorStop()
                    m.destroy()
                    stack1.append('backward')
                    stack2.append(1.0)
                    stack3.append(40)

                    sc.moveAngle(0,(0))
                    moving = 0
            else:

                m.setup()
                m.motorStop()
                m.destroy()
                moving = 0
                
            if numz > 100:  # if close to object 
                approached = approached + 1
            
            if approached > 7 and return1 == 0:
                stuck = 0
                if numz < 215 and objectInfo:
                    tim = .4 - (numz/ 1000)
                    m.setup()
                    m.move(50, 'backward', 'no', 0.8)
                    time.sleep(tim)                    
                    m.motorStop()
                    m.destroy()
                elif numz > 235:
                    m.setup()
                    m.move(50, 'forward', 'no', 0.8)
                    time.sleep(.05)                    
                    m.motorStop()
                    m.destroy()
                if numz < 235 and numz > 215:
                    pickup = 1
            
            if pickup == 1: #once in perfect position pickup object
                if numx < 280 and objectInfo: 
                    pos = pos + ((295 - numx)/35)                   
                if numx > 295 and objectInfo:
                    pos = pos - ((numx - 280)/35) 
                if numx > 280 and numx < 295:
                    count = count + 1
                        
                    if count > 5:
                        sc.moveAngle(4,(0))
                        sc.moveAngle(2,(-70))
                        sc.moveAngle(3,(80))
                        time.sleep(1)
        
                        sc.moveAngle(4,(-70))
                        time.sleep(2)
                        sc.moveAngle(2,(0))
                        pickup = 0
                        count = 0
                        return1 = 1
                        m.setup()

                        m.destroy()
                else:
                    count = 0

    
        
        print(numx)
        print(numz)
        print(pos)
       
        cv2.imshow("Frame", img)
        key = cv2.waitKey(1) & 0xFF
    
        rawCapture.truncate(0)
        if key ==ord("q"):
            break
        if pos < -45:
            flag = 1
            complete = complete +1
        if pos > 45:
            flag = 0
            complete = complete +1
        sc.moveAngle(1,(pos)) # update servo positions
        time.sleep(.05)
        sc.moveAngle(0,(pos2))
        time.sleep(.05)




   


