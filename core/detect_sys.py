import cv2
import time
import torch
from pathlib import Path
import sys
import os

# YOLOv5 모델 및 유틸리티 경로 설정
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # 프로젝트 루트 (iljjagom)
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# 현재 작업 디렉토리를 프로젝트 루트로 변경
os.chdir(ROOT)

from models.common import DetectMultiBackend
from utils.general import (check_img_size, non_max_suppression, scale_boxes, xyxy2xywh)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device
from utils.augmentations import letterbox

class BookDetector:
    def __init__(self, inform_system, weights=None, data='data/coco128.yaml', device='', half=False, camera_source=0):
        
        if weights is None:
            custom_weights = 'runs/train/document_yolov5s_results/weights/best.pt'
            if os.path.exists(custom_weights):
                weights = custom_weights
                print(f"문서 감지 모델을 사용합니다: {weights}")
            else:
                weights = 'yolov5s.pt'
                print(f"문서 감지 모델을 찾을 수 없습니다: {custom_weights}")
                sys.exit()
        
        self.device = select_device(device)
        self.model = DetectMultiBackend(weights, device=self.device, dnn=False, data=data, fp16=half)
        self.stride, self.names, self.pt = self.model.stride, self.model.names, self.model.pt
        self.imgsz = check_img_size((640, 640), s=self.stride)
        self.inform_system = inform_system
        self.camera_source = camera_source

    def run(self, source=None, conf_thres=0.6, iou_thres=0.45, max_det=1000, classes=None, agnostic_nms=False):
        # classes 인자 처리
        if classes is not None and isinstance(classes, list):
            classes = [int(c) for c in classes]
        
        try:
            if source is None:
                source = str(self.camera_source)
            else:
                source = str(source)
            
            is_webcam = source.isnumeric()
            
            if is_webcam:
                cap = cv2.VideoCapture(int(source))
                if not cap.isOpened():
                    raise IOError(f"웹캠 {source}를 열 수 없습니다.")
                print(f"카메라 {source} 연결 성공")
            else:
                print("오류: 웹캠 소스만 지원됩니다.")
                return None
        except Exception as e:
            print(f"카메라 초기화 오류: {e}")
            return None

        detection_start_time = None
        stable_bbox = None
        STABILITY_SECONDS = 5.0

        print(f"감지 가능한 클래스: {self.names}")
        print("문서/책을 카메라 앞에 놓아주세요...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 이미지 전처리
            im = letterbox(frame, self.imgsz, stride=self.stride, auto=self.pt)[0]
            im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
            im = torch.from_numpy(im.copy()).to(self.device)
            im = im.half() if self.model.fp16 else im.float()
            im /= 255.0
            if len(im.shape) == 3:
                im = im[None]

            # 추론
            pred = self.model(im, augment=False, visualize=False)
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

            detected = False
            annotator = Annotator(frame, line_width=3, example=str(self.names))
            
            for i, det in enumerate(pred):
                if len(det):
                    # 결과 좌표 스케일링
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], frame.shape).round()

                    for *xyxy, conf, cls in reversed(det):
                        class_name = self.names[int(cls)]
                        print(f"감지된 객체: {class_name} (신뢰도: {conf:.2f})")
                        
                        # 'document' 클래스이고 신뢰도가 0.6 이상인 경우만 처리
                        if class_name.lower() == 'document' and conf >= 0.6:
                            detected = True
                            current_bbox = [int(c) for c in xyxy]
                            
                            # 바운딩 박스 그리기
                            c = int(cls)
                            label = f'{class_name} {conf:.2f}'
                            annotator.box_label(xyxy, label, color=colors(c, True))
                            
                            # 안정성 체크
                            if stable_bbox and self.is_stable(stable_bbox, current_bbox):
                                if time.time() - detection_start_time >= STABILITY_SECONDS:
                                    print("안정적인 문서 감지 완료. 캡처 및 처리 시작.")
                                    cap.release()
                                    cv2.destroyAllWindows()
                                    return {'frame': frame, 'bbox': current_bbox}
                            else:
                                stable_bbox = current_bbox
                                detection_start_time = time.time()
                                print(f"문서 감지 시작... ({STABILITY_SECONDS}초 대기)")
                            
                            break  # 가장 확률 높은 문서 하나만 처리
            
            if not detected:
                detection_start_time = None
                stable_bbox = None

            im_display = annotator.result()
            
            # 상태 정보 표시 (영어로 표시하여 호환성 보장)
            font = cv2.FONT_HERSHEY_SIMPLEX
            if detection_start_time:
                elapsed = time.time() - detection_start_time
                remaining = max(0, STABILITY_SECONDS - elapsed)
                status_text = f"Document detection... {remaining:.1f}s remaining"
                cv2.putText(im_display, status_text, (10, 30), font, 1, (0, 255, 0), 2)
            else:
                cv2.putText(im_display, "Searching for documents...", (10, 30), font, 1, (0, 0, 255), 2)
            
            cv2.imshow('Book Detection', im_display)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("사용자가 ESC를 눌러 감지를 중단")
                break
            elif cv2.getWindowProperty('Book Detection', cv2.WND_PROP_VISIBLE) < 1:
                print("카메라 창이 닫혀 감지를 중단.")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("감지 종료.")
        return None

    def is_stable(self, prev_box, curr_box, iou_threshold=0.7, center_threshold=30):
        # IoU 계산
        xA = max(prev_box[0], curr_box[0])
        yA = max(prev_box[1], curr_box[1])
        xB = min(prev_box[2], curr_box[2])
        yB = min(prev_box[3], curr_box[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (prev_box[2] - prev_box[0]) * (prev_box[3] - prev_box[1])
        boxBArea = (curr_box[2] - curr_box[0]) * (curr_box[3] - curr_box[1])
        iou = interArea / float(boxAArea + boxBArea - interArea)

        # 중심점 거리 계산
        prev_center = ((prev_box[0] + prev_box[2]) / 2, (prev_box[1] + prev_box[3]) / 2)
        curr_center = ((curr_box[0] + curr_box[2]) / 2, (curr_box[1] + curr_box[3]) / 2)
        dist = ((prev_center[0] - curr_center[0]) ** 2 + (prev_center[1] - curr_center[1]) ** 2) ** 0.5

        return iou > iou_threshold and dist < center_threshold
