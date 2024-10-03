import cv2
import mediapipe as mp

class FaceDetection:

    def init_variables(self):
        self.face_detected = False

    def __init__(self):
        self.init_variables()
        self.face_mesh = None
        self.cap = None

    def config_camera(self, screen_width, screen_height):
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

    def process_face_detection(self):
        ret, camera_image = self.cap.read()

        results = self.face_mesh.process(camera_image)
        
        if results.multi_face_landmarks:
            return True
        else:
            return False
            