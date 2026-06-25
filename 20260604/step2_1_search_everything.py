import os
import glob
import sys
import ctypes
import datetime
import configparser
import pandas as pd

# Everything SDK DLL 설정 상수
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002

def init_everything_sdk(dll_path):
    """Everything DLL을 로드하고 ctypes 인터페이스를 초기화합니다."""
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
    """Everything 엔진을 사용해 특정 폴더 하위에서 파일명과 정확히 일치하는 첫 번째 결과를 찾습니다."""
    # wfn (Whole File Name) 매크로를 사용하여 파일명 전체가 정확히 매칭되도록 함
    # path:를 사용하여 검색 범위를 지정
    query = f'path:"{search_dir}" wfn:"{filename}"'
    
    dll.Everything_SetSearchW(query)
    dll.Everything_SetRequestFlags(EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH)
    
    # 동기식으로 쿼리 실행
    if not dll.Everything_QueryW(True):
        return None
        
    num_results = dll.Everything_GetNumResults()
    if num_results == 0:
        return None
        
    # 파일명이 완전히 동일한 첫 번째 결과를 찾아서 반환
    for i in range(num_results):
        res_filename = dll.Everything_GetResultFileNameW(i)
        res_path = dll.Everything_GetResultPathW(i)
        
        # 파일명 대소문자 구분 없이 비교
        if res_filename.lower() == filename.lower():
            return os.path.join(res_path, res_filename)
            
    return None

def main():
    print("=" * 60)
    print(" Step 2-1: Everything SDK 기반 복사 대상 파일 경로 자동 검색 작업을 시작합니다.")
    print("=" * 60)
    
    # 1. 설정 로드 (frozen 대응)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        
    config_file = os.path.join(exe_dir, 'config.ini')
    
    if not os.path.exists(config_file):
        print(f"[오류] 설정 파일({config_file})이 존재하지 않습니다.")
        sys.exit(1)
        
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    try:
        data_list_path = config.get('SETTINGS', 'DATA_LIST_PATH')
        data_dir = os.path.dirname(data_list_path) or exe_dir
        search_dir = config.get('SETTINGS', 'SEARCH_DIR')
    except Exception as e:
        print(f"[오류] config.ini 설정을 파싱하는 도중 에러가 발생했습니다: {e}")
        sys.exit(1)
        
    print(f"[*] 설정 로드 완료")
    print(f"   - 데이터 폴더: {data_dir}")
    print(f"   - Everything 검색 대상(SEARCH_DIR): {search_dir}")
    
    # 2. Everything SDK DLL 로드 (로컬 폴더 우선 탐색으로 백신 차단 우회)
    dll_path = os.path.join(exe_dir, 'Everything64.dll')
    
    # 만약 실행 파일 옆에 DLL이 없고 frozen 빌드 상태라면 임시 폴더에서 차선책으로 탐색
    if not os.path.exists(dll_path) and getattr(sys, 'frozen', False):
        dll_path = os.path.join(sys._MEIPASS, 'Everything64.dll')
    try:
        dll = init_everything_sdk(dll_path)
        print("[*] Everything SDK DLL 로드 완료")
    except Exception as e:
        print(f"[오류] Everything DLL 로드 실패. download_everything_sdk.py를 먼저 실행하세요: {e}")
        sys.exit(1)
        
    # 3. 최신 Missing_Files_*.xlsx 파일 검색
    # (주의: 이전에 생성된 Missing_Files_with_Paths_*.xlsx도 검색 범위에 들 수 있으나,
    # 2단계의 기본 형태인 Missing_Files_YYYYMMDD_HHMMSS.xlsx 형식을 우선 타겟팅하기 위해
    # 파일 생성 시점 및 이름을 정확히 구분하여 가져옵니다.)
    search_pattern = os.path.join(data_dir, "Missing_Files_*.xlsx")
    missing_files = glob.glob(search_pattern)
    
    # 만약 결과가 없다면 처리 종료
    if not missing_files:
        print(f"[!] '{data_dir}' 폴더 내에 누락 파일 리스트(Missing_Files_*.xlsx)가 존재하지 않습니다.")
        sys.exit(1)
        
    # 'with_Paths' 및 '_paths'가 포함된 파일은 이전 2-1단계 실행 결과이므로 제외하고 오리지널 Missing_Files 파일들 중에서 가장 최신 파일을 선택합니다.
    original_missing_files = [f for f in missing_files if "with_Paths" not in os.path.basename(f) and "_paths" not in os.path.basename(f)]
    
    if not original_missing_files:
        # 혹시 'with_Paths'만 있을 경우 예외적으로 전체 파일 중 최신 선택
        target_file = max(missing_files, key=os.path.getmtime)
    else:
        target_file = max(original_missing_files, key=os.path.getmtime)
        
    print(f"[*] 원본 누락 파일 자동 선택: {target_file}")
    
    # 4. 데이터 로드 및 전처리
    try:
        df = pd.read_excel(target_file)
    except Exception as e:
        print(f"[오류] 엑셀 파일을 읽는 과정에서 에러가 발생했습니다: {e}")
        sys.exit(1)
        
    if 'FILENAME' not in df.columns or 'COPY_FROM_PATH' not in df.columns:
        print("[오류] 엑셀 파일에 'FILENAME' 또는 'COPY_FROM_PATH' 컬럼이 존재하지 않습니다.")
        sys.exit(1)
        
    # Pandas FutureWarning 방지를 위해 미리 object 타입으로 형변환 수행
    df['COPY_FROM_PATH'] = df['COPY_FROM_PATH'].astype(object)
    
    # 5. 검색 시작
    total_rows = len(df)
    success_count = 0
    fail_count = 0
    
    print(f"\n[*] Everything 검색 수행 중... (총 {total_rows}건)")
    
    for idx, row in df.iterrows():
        filename = str(row['FILENAME']).strip()
        
        # 파일명이 정상적이지 않은 경우 스킵
        if not filename or pd.isna(row['FILENAME']):
            df.at[idx, 'COPY_FROM_PATH'] = ''
            fail_count += 1
            continue
            
        # Everything SDK 검색 수행
        found_path = search_first_match(dll, search_dir, filename)
        
        if found_path:
            df.at[idx, 'COPY_FROM_PATH'] = found_path
            success_count += 1
        else:
            df.at[idx, 'COPY_FROM_PATH'] = ''
            fail_count += 1
            
    print(f"\n[*] 검색 완료: 총 {total_rows}건 중 {success_count}건 매칭 성공 (실패/누락: {fail_count}건)")
    
    # 6. 새 파일로 저장
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Missing_Files_{timestamp}_paths.xlsx"
    output_filepath = os.path.join(data_dir, output_filename)
    
    try:
        df.to_excel(output_filepath, index=False)
        print(f"[+] 성공적으로 처리 결과를 새 파일로 저장했습니다: {output_filepath}")
        
        # 저장 직후 실제 물리 파일 확인
        if os.path.exists(output_filepath):
            print(f"[검증] 물리 파일이 디렉터리에 존재함을 확인했습니다. (크기: {os.path.getsize(output_filepath)} 바이트)")
        else:
            print("[경고] to_excel 완료 직후 파일이 존재하지 않는 특이 현상이 감지되었습니다!")
            
        print(" [다음 가이드]")
        print("   - 이제 'step3_generate_robocopy.py'를 수행하면 방금 생성된 엑셀을 기준으로 복사 스크립트가 자동 생성됩니다.")
    except Exception as e:
        print(f"[오류] 결과 파일 저장에 실패했습니다: {e}")
        sys.exit(1)
        
    print("=" * 60)

if __name__ == '__main__':
    main()
