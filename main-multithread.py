from tkinter import Canvas, Tk
from FaceDetector import *
from screenshot import screenshot
import threading
import time

class DragType:
    Edge = True
    Vertex = False

class Gender:
    Male = True
    Female = False

#https://stackoverflow.com/questions/65174044/tkinter-resize-a-rectange-on-canvas-using-mouse
class Window(Tk):
    def __init__(self, **args):
        super().__init__(**args)
        self.lift()
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", 'gray')
        self.wait_visibility()

        self.screen = self.canvasInit()

        self.detect = FaceDetector_cv2().detect

        #use two faces buffer so that we can add new faces before delete old
        #which solved the screen flickers
        self.facesRect = [[],[]]
        self.facesInfo = [[],[]]
        self.displayTag = 0

        self.endLoop = False

        self.bind('<Escape>', self.on_closeWindow)
        
        #just make self.frameBuffer contain something
        self.frameBuffer = screenshot(0,0,10,10)

        self.multithread()

    def canvasInit(self):
        #Get the current screen width and height
        width =  self.winfo_screenwidth()
        height = self.winfo_screenheight()

        canvas = Canvas(width = width, height = height)

        canvas.create_rectangle(0, 0, width, height, width=3, fill='gray')
        self.current = canvas.create_rectangle(10, 10, 110, 1010, width=5, outline = 'red')
        canvas.tag_bind(self.current, '<Button-1>', self.on_click)
        canvas.tag_bind(self.current, '<Button1-Motion>', self.on_motion)
        canvas.tag_bind(self.current, '<Enter>', self.on_enter)

        canvas.pack()

        return canvas

    def getCoordsRelatedToCurrent(self, currentX, currentY):
        x1, y1, x2, y2 = self.screen.coords(self.current)
        if abs(currentX - x1) < abs(currentX - x2):
            nearX, farX = x1, x2
        else:
            nearX, farX = x2, x1

        if abs(currentY - y1) < abs(currentY - y2):
            nearY, farY = y1, y2
        else:
            nearY, farY = y2, y1

        return nearX, nearY, farX, farY


    def on_click(self, event):
        self.originalCoord = self.screen.coords(self.current)
        self.originalCursorX, self.originalCursorY = event.x, event.y

        nearX, nearY, farX, farY = self.getCoordsRelatedToCurrent(event.x, event.y)

        self.start = (farX, farY)
        self.end = (nearX, nearY)

        SELECT_REGION_SIZE = 50
        if (abs(nearX - event.x) < SELECT_REGION_SIZE and abs(nearY - event.y) > SELECT_REGION_SIZE) or \
           (abs(nearY - event.y) < SELECT_REGION_SIZE and abs(nearX - event.x) > SELECT_REGION_SIZE):
            self.dragType = DragType.Edge
            self.config(cursor="fleur")
        else:
            self.dragType = DragType.Vertex
            self.config(cursor="tcross")  

    def on_enter(self, event):
        nearX, nearY, farX, farY = self.getCoordsRelatedToCurrent(event.x, event.y)

        #change cursor
        SELECT_REGION_SIZE = 50
        if (abs(nearX - event.x) < SELECT_REGION_SIZE and abs(nearY - event.y) > SELECT_REGION_SIZE) or \
           (abs(nearY - event.y) < SELECT_REGION_SIZE and abs(nearX - event.x) > SELECT_REGION_SIZE):
            self.config(cursor="fleur")
        else:
            self.config(cursor="tcross")    

    def on_motion(self, event):
        deltaX= event.x - self.originalCursorX
        deltaY= event.y - self.originalCursorY

        if self.dragType == DragType.Edge:
            self.config(cursor="fleur")
            self.start = (self.originalCoord[0] + deltaX, self.originalCoord[1] + deltaY)
            self.end   = (self.originalCoord[2] + deltaX, self.originalCoord[3] + deltaY)
        elif self.dragType == DragType.Vertex:
            self.end = (event.x, event.y)
            self.config(cursor="tcross")
        else:
            raise Exception("Should not reach here!")
        self.screen.coords(self.current, *self.start, *self.end)

    def on_closeWindow(self, event):
        self.endLoop = True
        self.destroy()
        

    def getCoords(self):
        left, top, right, bottom = list(map(int, self.screen.coords(self.current)))
        width = right - left
        height = bottom - top

        return (left, top, width, height)

    def multithread(self):
        t1 = threading.Thread(target = self.screenshot)
        t2 = threading.Thread(target = self.faceDetect)

        #kill threads when main thread died
        t1.daemon = True 
        t2.daemon = True 

        t1.start()
        t2.start()
        
    
    def screenshot(self):
        while not self.endLoop:
            region = self.getCoords()

            if region[2] <= 1 or region[3] <= 1:    #height or width <= 1
                continue
            img = screenshot(*region)

            self.frameBuffer = img
            

    def faceDetect(self):
        self.totalTime = 0
        self.totalRound = 0
        self.time = time.time()
        while not self.endLoop:
            #get area which is selected
            region = self.getCoords()
            regionLeft = int(region[0])
            regionTop = int(region[1])   

            img = self.frameBuffer

            faces = self.detect(img)

            #draw new faces
            for (left, top, width, height) in faces:
                age, gender = self.faceClassify(img[left:left + width, top:top+height])

                if gender == Gender.Male:
                    outlineColor = 'blue'
                elif gender == Gender.Female:
                    outlineColor = 'red'

                left += regionLeft
                top += regionTop
                right = left + width
                bottom = top + height
                
                rect = self.screen.create_rectangle(left, top, right, bottom, width=2, outline = outlineColor)
                self.facesRect[self.displayTag].append(rect)
                text = self.screen.create_text(left, top, text = f'Age:{age}', anchor='nw', fill='red')
                self.facesInfo[self.displayTag].append(text)

            #clear last frame faces
            while len(self.facesRect[1 - self.displayTag]) > 0:
                self.screen.delete(self.facesRect[1 - self.displayTag].pop())
            while len(self.facesInfo[1 - self.displayTag]) > 0:
                self.screen.delete(self.facesInfo[1 - self.displayTag].pop()) 

            #flip tag
            self.displayTag = 1 - self.displayTag

            #for debug
            self.totalTime += time.time() - self.time
            self.totalRound += 1
            print(f"frame took {time.time() - self.time} seconds, current pixels count: {region[2] * region[3]}")
            self.time = time.time()


    def faceClassify(self, face):
        age = 18
        gender = Gender.Male
        return age, gender

if __name__ == "__main__":
    window = Window()
    window.mainloop()
