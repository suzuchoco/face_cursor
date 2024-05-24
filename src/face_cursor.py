import cv2
import mediapipe as mp
import pyautogui
import statistics
import time

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.nose_list_x = []
        self.nose_list_y = []
        self.screen_width, self.screen_height = pyautogui.size()
        self.frame_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.last_click_time = time.time()
        self.last_action_time = time.time()

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()

    def detect_rapid_movement(self, axis_list, threshold, min_rapid_movements):
        if len(axis_list) > 20:
            recent_movements = [axis_list[i] - axis_list[i-1] for i in range(-1, -21, -1)]
            rapid_movements = sum(1 for movement in recent_movements if abs(movement) > threshold)
            return rapid_movements / len(recent_movements) > min_rapid_movements
        return False

    def process_frame(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_face_mesh = mp.solutions.face_mesh

        drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

        with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:

            while self.video.isOpened():
                success, image = self.video.read()

                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                # 画像を左右反転させる
                image = cv2.flip(image, 1)

                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                results = face_mesh.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        mp_drawing.draw_landmarks(
                            image=image,
                            landmark_list=face_landmarks,
                            connections=mp_face_mesh.FACEMESH_IRISES,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style())

                        nose_landmark = face_landmarks.landmark[4]
                        nose_x = int(nose_landmark.x * self.frame_width)
                        nose_y = int(nose_landmark.y * self.frame_height)
                        self.nose_list_x.append(nose_x)
                        self.nose_list_y.append(nose_y)

                        # Draw a blue rectangle around the nose
                        cv2.rectangle(image, 
                                      (nose_x - 10, nose_y - 10), 
                                      (nose_x + 10, nose_y + 10), 
                                      (255, 0, 0), 
                                      2)

                        left_eye_x = int(face_landmarks.landmark[33].x * self.frame_width)
                        right_eye_x = int(face_landmarks.landmark[263].x * self.frame_width)
                        mid_eye_x = (left_eye_x + right_eye_x) // 2

                        if len(self.nose_list_x) > 20 and len(self.nose_list_y) > 20:
                            mean_nose_y = statistics.mean(self.nose_list_y[-10:])

                            # 鼻が右目寄りなら右に、左目寄りなら左にカーソルを動かす
                            if nose_x > mid_eye_x:
                                pyautogui.moveRel(20, 0, duration=0)
                            elif nose_x < mid_eye_x:
                                pyautogui.moveRel(-20, 0, duration=0)

                            # 鼻が上に向いたらカーソルを上に動かす
                            if nose_y < mean_nose_y:
                                pyautogui.moveRel(0, -20, duration=0)
                            # 鼻が下に向いたらカーソルを下に動かす
                            elif nose_y > mean_nose_y:
                                pyautogui.moveRel(0, 20, duration=0)

                            # Detect rapid vertical movement for click
                            if self.detect_rapid_movement(self.nose_list_y, threshold=10, min_rapid_movements=0.4) and time.time() - self.last_click_time > 1:
                                pyautogui.click()
                                self.last_click_time = time.time()

                            # Detect rapid horizontal movement for exit
                            if self.detect_rapid_movement(self.nose_list_x, threshold=20, min_rapid_movements=0.5) and time.time() - self.last_action_time > 1:
                                self.__del__()
                                return

                cv2.imshow('Video Feed', image)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        self.__del__()

if __name__ == "__main__":
    video_camera = VideoCamera()
    video_camera.process_frame()
