import cv2

video_capture = cv2.VideoCapture(0)  # Access the camera
if not video_capture.isOpened():
    print("Unable to open the camera.")
else:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to grab frame.")
            break
        cv2.imshow("Camera Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()
