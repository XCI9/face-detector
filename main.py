from tkinter import Canvas, Tk
from FaceDetector import FaceDetector_cv2
from screenshot import screenshot
import cv2

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

        self.facesRect = []
        self.facesInfo = []

        self.bind('<Escape>', self.on_closeWindow)

        #start face detect loop
        self.faceDetect()

    def canvasInit(self):
        #Get the current screen width and height
        width =  self.winfo_screenwidth()
        height = self.winfo_screenheight()

        canvas = Canvas(width = width, height = height)

        canvas.create_rectangle(0, 0, width, height, width=3, fill='grey')
        self.current = canvas.create_rectangle(50, 50, 100, 100, width=5, outline = 'red')
        canvas.tag_bind(self.current, '<Button-1>', self.on_click)
        canvas.tag_bind(self.current, '<Button1-Motion>', self.on_motion)
        canvas.tag_bind(self.current, '<Enter>', self.on_enter)

        canvas.pack()

        return canvas

    def on_click(self, event):
        self.originalCoord = self.screen.coords(self.current)
        self.originalCursorX, self.originalCursorY = event.x, event.y

    def on_enter(self, event):
        x1, y1, x2, y2 = self.screen.coords(self.current)
        if abs(event.x - x1) < abs(event.x - x2):
            # opposing side was grabbed; swap the anchor and mobile side
            nearX, farX = x1, x2
        else:
            nearX, farX = x2, x1

        if abs(event.y - y1) < abs(event.y - y2):
            nearY, farY = y1, y2
        else:
            nearY, farY = y2, y1

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
        self.destroy()

    def getCoords(self):
        left, top, right, bottom = list(map(int, self.screen.coords(self.current)))
        width = right - left
        height = bottom - top

        return (left, top, width, height)

    def faceDetect(self):
        #clear last frame faces
        while len(self.facesRect) > 0:
            self.screen.delete(self.facesRect.pop())
        while len(self.facesInfo) > 0:
            self.screen.delete(self.facesInfo.pop())

        #get area which is selected
        region = self.getCoords()
        regionLeft = int(region[0])
        regionTop = int(region[1])

        if region[2] <= 1 or region[3] <= 1:    #height or width <= 1
            self.after(1, self.faceDetect)
            return
        img = screenshot(*region)

        #shrink picture to run faster
        faces = self.detect(cv2.resize(img, (0, 0), fx=0.5, fy=0.5))
        #faces = self.detect(img)
        #draw new faces
        for (left, top, width, height) in faces:
            left <<= 1
            top <<= 1
            width <<= 1
            height <<= 1
            age, gender =self.faceClassify(img[left:left + width][top:top+height])

            if gender == Gender.Male:
                outlineColor = 'blue'
            elif gender == Gender.Female:
                outlineColor = 'red'

            left += regionLeft
            top += regionTop
            right = left + width
            bottom = top + height
            rect = self.screen.create_rectangle(left, top, right, bottom, width=2, outline = outlineColor)
            self.facesRect.append(rect)
            text = self.screen.create_text(left, top, text = f'Age:{age}', anchor='nw', fill='red')
            self.facesRect.append(text)

        self.after(1, self.faceDetect)

    def faceClassify(self, face):
        age = 18
        gender = Gender.Male
        return age, gender

if __name__ == "__main__":
    window = Window()
    window.mainloop()
