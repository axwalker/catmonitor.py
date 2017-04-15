from datetime import datetime
import threading
import time

import imutils
import cv2


class CatMonitor:
    def __init__(self, camera_index, width=1280, height=720):
        self.camera_index = camera_index
        self.base_gray = None
        self.recording = False

        self.width, self.height = width, height

    def __enter__(self):
        self.capture = cv2.VideoCapture(self.camera_index)
        self.capture.set(3, self.width)
        self.capture.set(4, self.height)
        return self

    def __exit__(self, *args):
        self.capture.release()

    def monitor(self):
        grabbed, frame = self.capture.read()
        self.base_gray = to_gray_blur(frame)

        while True:
            self._look_for_changes()
            time.sleep(0.1)

    def _look_for_changes(self):
        grabbed, frame = self.capture.read()
        current_gray = to_gray_blur(frame)
        contours = contour_differences(self.base_gray, current_gray)
        object_found = any((cv2.contourArea(c) > 1000 for c in contours))

        if object_found and not self.recording:
            self.record_video()
        elif not object_found and self.recording:
            self.stop_video()

    def record_video(self):
        def record():
            print('starting recording')
            self.recording = True
            filename = '/data/{}.avi'.format(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(filename, fourcc, 20, (self.width, self.height))
            while self.recording:
                ret, frame = self.capture.read()
                if ret:
                    video_writer.write(frame)
            video_writer.release()

        video_thread = threading.Thread(target=record, args=())
        video_thread.start()

    def stop_video(self):
        print('stopping recording')
        self.recording = False


def to_gray_blur(frame):
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (21, 21), 0)


def contour_differences(f1, f2):
    frame_delta = cv2.absdiff(f1, f2)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)
    return cnts


if __name__ == '__main__':
    with CatMonitor(camera_index=1) as cm:
        cm.monitor()
