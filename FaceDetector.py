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


import mediapipe as mp

class FaceDetector_mediapipe():
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

    #input gray scale image
    #output a list of face region in the form of (x, y, w, h)
    def detect(self, img):
        results = self.face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not results.detections:
            return []
        else:
            imgHeight, imgWidth, _ = img.shape
            
            faces = []
            for detection in results.detections:
                left = int(detection.location_data.relative_bounding_box.xmin * imgWidth)
                top = int(detection.location_data.relative_bounding_box.ymin * imgHeight)
                width = int(detection.location_data.relative_bounding_box.width * imgWidth)
                height = int(detection.location_data.relative_bounding_box.height * imgHeight)
                faces.append((left, top, width, height))
            return faces