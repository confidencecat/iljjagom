import cv2

# USB 카메라 장치 번호를 변경해보세요 (0, 1, 2 등)

cam_num = int(input("카메라 번호 : "))
cap = cv2.VideoCapture(cam_num)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
else:
    print("카메라가 정상적으로 열렸습니다.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("카메라에서 프레임을 가져올 수 없습니다.")
        break

    cv2.imshow('USB Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
