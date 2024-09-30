import os
import re
import json
import torch
from datasets import Dataset  # 추가된 부분
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

# 텍스트 데이터를 불러오는 함수
def load_preprocessed_data(preprocessed_data_dir):
    data = []
    labels = []
    
    for file_name in os.listdir(preprocessed_data_dir):
        file_path = os.path.join(preprocessed_data_dir, file_name)
        
        # 텍스트 파일을 열어서 데이터를 읽음
        if os.path.getsize(file_path) > 0:
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    case_data = file.read()

                    # 사건 번호, 판결 날짜, 법원 등 중요한 정보 추출
                    case_number = re.search(r'case_number: (.+)', case_data)
                    judgment_date = re.search(r'judgment_date: (.+)', case_data)
                    court = re.search(r'court: (.+)', case_data)
                    background = re.search(r'background: (.+)', case_data)
                    legal_issue = re.search(r'legal_issue: (.+)', case_data)
                    decision = re.search(r'decision: (.+)', case_data)
                    
                    if case_number and judgment_date and court and background and legal_issue and decision:
                        input_text = f"사건 번호: {case_number.group(1)}\n" \
                                     f"판결 날짜: {judgment_date.group(1)}\n" \
                                     f"법원: {court.group(1)}\n" \
                                     f"배경: {background.group(1)}\n" \
                                     f"법적 쟁점: {legal_issue.group(1)}\n" \
                                     f"결정: {decision.group(1)}"
                        data.append(input_text)
                        labels.append(0)  # 레이블은 상황에 맞게 설정

                except Exception as e:
                    print(f"파일을 읽는 중 오류 발생: {file_path}, 오류: {e}")
        else:
            print(f"빈 파일 건너뜀: {file_path}")

    return data, labels

# 텍스트 클리닝 함수
def clean_text(text):
    # '리걸엔진 AI 판례 검색' 관련 패턴 제거
    text = re.sub(r'\| 리걸엔진 AI 판례 검색 \d+/\d+', '', text)
    
    # 추가로 불필요한 개행문자나 공백 정리
    text = re.sub(r'\n+', '\n', text)  # 연속된 개행문자는 하나로 줄임
    text = re.sub(r'\s+', ' ', text)  # 연속된 공백을 하나로 줄임
    text = text.strip()  # 앞뒤 공백 제거
    
    return text

# 학습용 데이터 준비
def prepare_training_data(preprocessed_data_dir):
    data, labels = load_preprocessed_data(preprocessed_data_dir)
    
    cleaned_data = []
    
    # 클리닝 및 전처리된 텍스트 변환
    for text in data:
        cleaned_text = clean_text(text)
        cleaned_data.append(cleaned_text)
    
    return cleaned_data, labels

# 학습 실행 코드
def train_model():
    # 학습에 사용할 경로 설정
    preprocessed_data_dir = "./preprocess_result"
    
    # 학습용 데이터 불러오기
    data, labels = prepare_training_data(preprocessed_data_dir)
    
    # Tokenizer와 모델 불러오기
    tokenizer = BertTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
    model = BertForSequenceClassification.from_pretrained("nlpaueb/legal-bert-base-uncased", num_labels=2)
    
    # 데이터셋 준비
    encodings = tokenizer(data, truncation=True, padding=True, max_length=512)
    
    # encodings를 Dataset 형태로 변환
    dataset = Dataset.from_dict({
        'input_ids': encodings['input_ids'],
        'attention_mask': encodings['attention_mask'],
        'labels': labels
    })
    
    # 모델 학습에 필요한 설정
    training_args = TrainingArguments(
        output_dir='./results',
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
    )
    
    # Trainer를 통해 학습
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        eval_dataset=dataset,
    )
    
    # 모델 학습
    trainer.train()

# 학습 함수 호출
if __name__ == "__main__":
    train_model()
