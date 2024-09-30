import os
import glob
import re

# 한국어 불용어 리스트 (직접 확장 가능)
korean_stopwords = ['을', '를', '이', '가', '은', '는', '에', '하다', '있다', '되다']

def remove_urls(text):
    url_pattern = r'http[s]?://\S+'
    return re.sub(url_pattern, '', text)

def preprocess_korean_text():
    preprocess_result = []
    # 경로 설정 (예: '/path/to/your/directory')
    directory_path = 'D:/Law_Manager/1.Training-20240926T043241Z-001/1.Training/원천데이터/TS_1.판결문'
    sentencing_list = ['01.민사', '02.형사', '03행정']
    sentencing_year = ['1981~2016', '2017', '2018', '2019', '2020', '2021']

    for idx in sentencing_list:
        for year in sentencing_year:
            new_directory_path = f"{directory_path}/{idx}/{year}"

            # 디렉터리 내 모든 파일 가져오기 (텍스트 파일만 선택하려면 '*.txt' 사용)
            file_list = glob.glob(os.path.join(new_directory_path, '*.xml'))

            # 파일들을 순서대로 처리
            for file_path in sorted(file_list):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # 1. URL 제거
                    content = remove_urls(content)
                    
                    # 2. 특수문자 제거 (한글, 영어, 숫자, 띄어쓰기를 제외한 모든 문자 제거)
                    content = re.sub(r"[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s]", "", content)
                    
                    # 3. 소문자 변환 (한국어는 필요 없지만 영어 혼합 시 적용)
                    content = content.lower()
                    
                    # 4. 불용어 제거
                    words = content.split()
                    meaningful_words = [word for word in words if word not in korean_stopwords]
                    
                    # 5. 다시 하나의 문자열로 결합
                    preprocessed_text = ' '.join(meaningful_words)
                    
                    #print(f"File: {file_path}")
                    #print(preprocessed_text)
                    
                    
                    # 6. preprocess_result에 결합
                    preprocess_result.append(preprocessed_text.strip())
    
    return preprocess_result




'''

def save_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:  # 쓰기 모드로 파일 열기
        file.write(text)  # 전처리된 텍스트 쓰기
    print(f"텍스트가 {file_path}에 저장되었습니다.")

'''
