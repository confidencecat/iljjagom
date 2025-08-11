import torch
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# YOLOv5 모델 로드
model_path = 'runs/train/document_yolov5s_results/weights/best.pt'
print(f'모델 경로: {model_path}')
print(f'파일 존재: {os.path.exists(model_path)}')

try:
    model = torch.load(model_path, map_location='cpu', weights_only=False)
    print(f'모델 키: {list(model.keys())}')
    
    if 'model' in model:
        model_obj = model['model']
        print(f'모델 클래스 이름: {model_obj.names}')
        print(f'클래스 개수: {model_obj.nc}')
    else:
        print('모델 구조를 확인할 수 없습니다.')
        
except Exception as e:
    print(f'모델 로드 오류: {e}')
