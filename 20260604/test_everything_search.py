import os
import sys
import ctypes
import configparser
import pandas as pd

# Everything SDK DLL 설정 상수
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002

def init_everything_sdk(dll_path):
    """Everything DLL을 로드하고 ctypes 명세를 설정합니다."""
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"DLL 파일을 찾을 수 없습니다: {dll_path}")
    
    dll = ctypes.WinDLL(dll_path)
    
    # 함수 프로토타입 정의
    dll.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
    dll.Everything_SetRequestFlags.argtypes = [ctypes.c_uint32]
    
    dll.Everything_QueryW.argtypes = [ctypes.c_bool]
    dll.Everything_QueryW.restype = ctypes.c_bool
    
    dll.Everything_GetNumResults.restype = ctypes.c_uint32
    
    dll.Everything_GetResultFileNameW.argtypes = [ctypes.c_uint32]
    dll.Everything_GetResultFileNameW.restype = ctypes.c_wchar_p
    
    dll.Everything_GetResultPathW.argtypes = [ctypes.c_uint32]
    dll.Everything_GetResultPathW.restype = ctypes.c_wchar_p
    
    return dll

def search_first_match(dll, search_dir, filename):
    """Everything 엔진을 사용해 특정 폴더 하위에서 파일명과 완전 일치하는 첫 번째 결과를 찾습니다."""
    # wfn (Whole File Name) 매크로를 사용하여 파일명 완전 일치 유도
    # path:를 사용하여 검색 범위를 지정
    query = f'path:"{search_dir}" wfn:"{filename}"'
    
    dll.Everything_SetSearchW(query)
    dll.Everything_SetRequestFlags(EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH)
    
    # 동기식 쿼리 실행
    if not dll.Everything_QueryW(True):
        return None
        
    num_results = dll.Everything_GetNumResults()
    if num_results == 0:
        return None
        
    # 검색된 결과 리스트에서 파일명이 완전히 동일한 첫 번째 결과 리턴
    for i in range(num_results):
        res_filename = dll.Everything_GetResultFileNameW(i)
        res_path = dll.Everything_GetResultPathW(i)
        
        # 파일명 대소문자 구분 없이 완전 동일 여부 체크
        if res_filename.lower() == filename.lower():
            # 경로 조립하여 반환
            return os.path.join(res_path, res_filename)
            
    return None

def main():
    print("=" * 60)
    print(" Everything SDK 연동 테스트 및 100개 데이터 검증을 시작합니다.")
    print("=" * 60)
    
    # 1. 경로 인지 및 설정 로드
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'config.ini')
    
    if not os.path.exists(config_file):
        print(f"[오류] 설정 파일({config_file})이 존재하지 않습니다.")
        sys.exit(1)
        
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    try:
        data_list_path = config.get('SETTINGS', 'DATA_LIST_PATH')
        data_dir = os.path.dirname(data_list_path) or script_dir
        search_dir = config.get('SETTINGS', 'SEARCH_DIR')
    except Exception as e:
        print(f"[오류] config.ini 설정을 읽을 수 없습니다: {e}")
        sys.exit(1)
        
    print(f"[*] 설정 정보 로드 완료")
    print(f"   - 데이터 폴더: {data_dir}")
    print(f"   - Everything 검색 범위(SEARCH_DIR): {search_dir}")
    
    # 2. Everything SDK DLL 로드
    dll_path = os.path.join(script_dir, 'Everything64.dll')
    try:
        dll = init_everything_sdk(dll_path)
        print("[*] Everything SDK DLL 로드 성공")
    except Exception as e:
        print(f"[오류] DLL 로드 실패: {e}")
        sys.exit(1)
        
    # 3. 테스트 엑셀 파일 로드 (test_missing_100.xlsx)
    test_filepath = os.path.join(data_dir, "test_missing_100.xlsx")
    if not os.path.exists(test_filepath):
        print(f"[오류] 테스트 파일({test_filepath})이 없습니다. 이전 단계를 먼저 실행하세요.")
        sys.exit(1)
        
    try:
        df = pd.read_excel(test_filepath)
    except Exception as e:
        print(f"[오류] 테스트 파일 로드 중 에러: {e}")
        sys.exit(1)
        
    if 'FILENAME' not in df.columns or 'COPY_FROM_PATH' not in df.columns:
        print("[오류] 파일 내에 'FILENAME' 또는 'COPY_FROM_PATH' 열이 존재하지 않습니다.")
        sys.exit(1)
        
    # 4. 파일명으로 Everything 검색 수행
    total_rows = len(df)
    found_count = 0
    
    print(f"\n[*] Everything SDK를 통한 검색 시작 (총 {total_rows}건)...")
    
    for idx, row in df.iterrows():
        filename = str(row['FILENAME']).strip()
        
        if not filename or pd.isna(row['FILENAME']):
            continue
            
        # 검색 실행
        found_path = search_first_match(dll, search_dir, filename)
        
        if found_path:
            df.at[idx, 'COPY_FROM_PATH'] = found_path
            found_count += 1
            if found_count <= 5:
                print(f"   - [검색 성공] {filename} -> {found_path}")
        else:
            df.at[idx, 'COPY_FROM_PATH'] = '' # 찾지 못한 경우 공백 처리
            
    print(f"\n[*] 검색 완료: 총 {total_rows}건 중 {found_count}건 검색 성공")
    
    # 5. 결과 파일 저장
    result_filepath = os.path.join(data_dir, "test_missing_100_result.xlsx")
    try:
        df.to_excel(result_filepath, index=False)
        print(f"[+] 성공적으로 검증 결과 파일({result_filepath})을 저장했습니다.")
    except Exception as e:
        print(f"[오류] 결과 파일 저장 중 에러: {e}")
        sys.exit(1)
        
    print("=" * 60)

if __name__ == "__main__":
    main()
