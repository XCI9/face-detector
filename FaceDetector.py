import cv2

class FaceDetector_cv2():
    def __init__(self, scaleFactor=1.1, minNeighbors=10):
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.scaleFactor = scaleFactor
        self.minNeighbors = minNeighbors

    #input gray scale image
    #output a list of face region in the form of (x, y, w, h)
    def detect(self, img):
        faces = self.face_cascade.detectMultiScale(img, self.scaleFactor, self.minNeighbors)
        return faces