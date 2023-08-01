import cv2
import numpy as np
from time import sleep

def vd(video):
    min_width = 80  # Minimum width of the rectangle
    min_height = 80  # Minimum height of the rectangle

    offset = 6  # Allowed pixel error

    count_line_pos = 550  # Position of the counting line

    fps = 60  # Frames per second of the video

    detected_centers = []
    car_count = 0

    def get_center(x, y, w, h):
        # Calculate the center of the rectangle
        x_center = int(w / 2)
        y_center = int(h / 2)
        cx = x + x_center
        cy = y + y_center
        return cx, cy

    cap = cv2.VideoCapture(video)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    while True:
        ret, frame1 = cap.read()
        if not ret:
            print("Video has ended")
            break

        time = float(1 / fps)
        sleep(time)

        grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grey, (3, 3), 5)
        bg_mask = bg_subtractor.apply(blur)
        dilated_mask = cv2.dilate(bg_mask, np.ones((5, 5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated_mask = cv2.morphologyEx(dilated_mask, cv2.MORPH_CLOSE, kernel)
        dilated_mask = cv2.morphologyEx(dilated_mask, cv2.MORPH_CLOSE, kernel)
        contours, hierarchy = cv2.findContours(dilated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.line(frame1, (25, count_line_pos), (1200, count_line_pos), (255, 127, 0), 3)

        for (i, contour) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            is_valid_contour = (w >= min_width) and (h >= min_height)
            if not is_valid_contour:
                continue

            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

            center = get_center(x, y, w, h)
            detected_centers.append(center)

            cv2.circle(frame1, center, 4, (0, 0, 255), -1)

            for (x, y) in detected_centers:
                if y < (count_line_pos + offset) and y > (count_line_pos - offset):
                    car_count += 1
                    cv2.line(frame1, (25, count_line_pos), (1200, count_line_pos), (0, 127, 255), 3)
                    detected_centers.remove((x, y))
                    print("Car detected: " + str(car_count))

        cv2.putText(frame1, "VEHICLE COUNT: " + str(car_count), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
        cv2.imshow("Original Video", frame1)
        #cv2.imshow("Detection", dilated_mask)

        if cv2.waitKey(1) == 27: 
            break

    cv2.destroyAllWindows()
    cap.release()
    return car_count
