import re
import xml.etree.ElementTree as ET
import os

# XML 파일 경로에서 데이터를 추출하고 사건의 세부 내용을 자동으로 구조화하는 함수
def extract_case_data_from_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # 사건 내용 추출
        case_content = root.find('.//cn').text.strip()

        # 메타데이터 추출
        case_number = re.search(r"(\d{4}나\d+)", case_content)
        case_number = case_number.group(1) if case_number else "사건 번호 없음"

        judgment_date = re.search(r"(\d{4}\.\d{1,2}\.\d{1,2})", case_content)
        judgment_date = judgment_date.group(1) if judgment_date else "판결 날짜 없음"

        court = re.search(r"(서울고등법원|의정부지방법원|대법원)", case_content)
        court = court.group(1) if court else "법원 정보 없음"

        # 사건 세부 내용 추출
        background = re.search(r"(인정사실)(.*?)(주\s*문|판\s*단)", case_content, re.DOTALL)
        background = background.group(2).strip() if background else "사건 개요 없음"

        legal_issue = re.search(r"(쟁\s*점|법\s*적\s*쟁\s*점)(.*?)(주\s*문|판\s*단)", case_content, re.DOTALL)
        legal_issue = legal_issue.group(2).strip() if legal_issue else "법적 쟁점 없음"

        decision = re.search(r"(주\s*문|결\s*론)(.*?)(판\s*단|이\s*유|결\s*정)", case_content, re.DOTALL)
        decision = decision.group(2).strip() if decision else "판결 요약 없음"

        case_data = {
            "case_number": case_number,
            "judgment_date": judgment_date,
            "court": court,
            "background": background,
            "legal_issue": legal_issue,
            "decision": decision
        }

        return case_data

    except ET.ParseError as e:
        print(f"XML 파일 파싱 에러: {e}")
        return None
    except FileNotFoundError as e:
        print(f"파일을 찾을 수 없습니다: {e}")
        return None

def clean_case_data(case_data):
    cleaned_data = {}
    
    for key, value in case_data.items():
        cleaned_value = value.replace('\n', ' ')
        cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
        cleaned_value = re.sub(r'http[s]?://\S+', '', cleaned_value)
        cleaned_value = cleaned_value.strip()
        cleaned_data[key] = cleaned_value
    
    return cleaned_data

def clean_text(text):
    text = re.sub(r'\| 리걸엔진 AI 판례 검색 \d+/\d+', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

# 전처리된 데이터를 각 XML 파일마다 .txt 파일로 저장하는 함수
def process_and_save_cases_from_folders(folder_paths):
    # 현재 폴더에 있는 'preprocess_result' 폴더에 저장
    output_directory = os.path.join(os.getcwd(), 'preprocess_result')
    
    # 디렉토리가 없으면 생성
    os.makedirs(output_directory, exist_ok=True)
    
    for folder_path in folder_paths:
        # 폴더 내 모든 XML 파일의 경로를 찾기
        for root_dir, dirs, files in os.walk(folder_path):
            xml_files = [os.path.join(root_dir, file) for file in files if file.endswith('.xml')]
            
            # 각 XML 파일에 대해 처리 및 저장
            for xml_file in xml_files:
                case_data = extract_case_data_from_file(xml_file)
                
                if case_data:
                    cleaned_case_data = clean_case_data(case_data)
                    for key, value in cleaned_case_data.items():
                        cleaned_case_data[key] = clean_text(value)
                    
                    # 저장할 파일명 만들기
                    case_number = cleaned_case_data.get('case_number', os.path.basename(xml_file).split('.')[0])
                    output_file_name = f"{case_number}.txt"
                    output_file_path = os.path.join(output_directory, output_file_name)
                    
                    # .txt 파일로 저장
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        for key, value in cleaned_case_data.items():
                            f.write(f"{key}: {value}\n\n")
                        
                    print(f"{output_file_name} 저장 완료.")

# 예시 리스트 (폴더 경로들)
folder_paths = []

directory_path = 'D:/Law_Manager/1.Training-20240926T043241Z-001/1.Training/원천데이터/TS_1.판결문'
sentencing_list = ['01.민사', '02.형사', '03행정']
sentencing_year = ['1981~2016', '2017', '2018', '2019', '2020', '2021']

for idx in sentencing_list:
    for year in sentencing_year:
        folder_paths.append(f"{directory_path}/{idx}/{year}")

# 실행
process_and_save_cases_from_folders(folder_paths)
