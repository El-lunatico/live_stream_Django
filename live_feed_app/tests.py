from django.test import TestCase

# Create your tests here.
import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Try with and without cv2.CAP_DSHOW
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Error: Failed to capture frame.")
        break

    # Print pixel values for debugging
    print(f"Pixel at center: {frame[frame.shape[0] // 2, frame.shape[1] // 2]}")

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
