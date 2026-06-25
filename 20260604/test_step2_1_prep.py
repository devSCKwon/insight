import os
import glob
import sys
import configparser
import pandas as pd

def main():
    print("=" * 60)
    print(" 테스트용 100개 행 데이터 추출 작업을 시작합니다. (경로 인지형)")
    print("=" * 60)
    
    # 스크립트 위치 기준 설정 파일 읽기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'config.ini')
    
    data_dir = script_dir  # 기본 경로는 스크립트 폴더
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        try:
            data_list_path = config.get('SETTINGS', 'DATA_LIST_PATH')
            data_dir = os.path.dirname(data_list_path) or script_dir
            print(f"[*] 설정 파일에서 찾은 데이터 폴더: {data_dir}")
        except Exception as e:
            print(f"[!] 설정 읽기 중 에러 발생, 기본 경로 사용: {e}")
    else:
        print(f"[!] 설정 파일({config_file})이 존재하지 않아 스크립트 폴더를 기준으로 탐색합니다.")
            
    # 2. 최신 Missing_Files_*.xlsx 파일 검색
    search_pattern = os.path.join(data_dir, "Missing_Files_*.xlsx")
    missing_files = glob.glob(search_pattern)
    
    if not missing_files:
        print(f"[오류] '{data_dir}' 폴더 내에서 Missing_Files_*.xlsx 파일을 찾을 수 없습니다. step2를 먼저 실행해야 합니다.")
        sys.exit(1)
        
    # 가장 최근에 수정된 파일 선택
    target_file = max(missing_files, key=os.path.getmtime)
    print(f"[*] 최신 누락 파일 탐색 성공: {target_file}")
    
    # 3. 데이터 로드 및 100개 행 추출
    try:
        df = pd.read_excel(target_file)
    except Exception as e:
        print(f"[오류] 파일을 읽는 중 에러가 발생했습니다: {e}")
        sys.exit(1)
        
    total_rows = len(df)
    print(f"[*] 전체 누락 파일 건수: {total_rows}건")
    
    # 상위 100개 추출 (100개보다 적으면 전체 추출)
    test_df = df.head(100).copy()
    test_filename = "test_missing_100.xlsx"
    test_filepath = os.path.join(data_dir, test_filename)
    
    try:
        test_df.to_excel(test_filepath, index=False)
        print(f"[+] 성공적으로 {test_filepath} 파일을 생성했습니다. (행 개수: {len(test_df)}건)")
    except Exception as e:
        print(f"[오류] 테스트용 파일 저장 중 에러 발생: {e}")
        sys.exit(1)
        
    print("=" * 60)

if __name__ == "__main__":
    main()
