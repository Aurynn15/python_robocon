import cv2


class CameraService:
    """Service khusus untuk kamera OpenCV agar logic kamera tidak numpuk di class GUI."""

    def __init__(self, device_path: str):
        self.device_path = device_path
        self.cap = None
        self.open()

    def open(self) -> None:
        self.release()
        self.cap = cv2.VideoCapture(self.device_path, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def read_rgb_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret:
            return False, None

        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return True, frame

    def reconnect(self) -> None:
        self.open()

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None
