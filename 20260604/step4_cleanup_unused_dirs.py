import os
import glob
import sys
import configparser
import pandas as pd

def safe_removedirs(path, root_limit):
    """
    지정한 디렉터리(path)부터 시작하여 상위 디렉터리가 비어있는 동안 
    root_limit(ROOT_DIR) 직전까지 순차적으로(재귀적으로) 빈 디렉터리를 삭제하는 함수.
    """
    # 절대 경로로 표준화하여 비교 방어력 강화
    path = os.path.abspath(path)
    root_limit = os.path.abspath(root_limit)
    
    current = path
    deleted_folders = []
    
    while current and current != root_limit:
        # 안전장치: 현재 지우려는 경로가 설정된 ROOT_DIR의 하위가 맞는지 더블 체크
        if not current.startswith(root_limit) or current == root_limit:
            break
            
        if os.path.exists(current) and os.path.isdir(current):
            try:
                # 폴더 안이 완전히 비어있는지 확인
                if len(os.listdir(current)) == 0:
                    os.rmdir(current)
                    deleted_folders.append(current)
                    # 부모 경로로 거슬러 올라감
                    current = os.path.dirname(current)
                else:
                    # 파일이나 하위 폴더가 하나라도 존재하면 상위 디렉터리 삭제 중단
                    break
            except Exception as e:
                print(f"[경고] 폴더 삭제 중 에러 발생 ({current}): {e}")
                break
        else:
            # 경로가 이미 없으면 부모 경로로 이동하여 계속 체크
            current = os.path.dirname(current)
            
    return deleted_folders

def main():
    print("=" * 60)
    print(" 4단계: 미기입(찾지 못한) 누락 파일의 빈 폴더 정리 작업을 시작합니다.")
    print("=" * 60)

    # 1. 설정 파일 읽기 및 ROOT_DIR 파악
    config_file = 'config.ini'
    data_dir = '.' # 20260604 내부 실행 가정
    
    if not os.path.exists(config_file):
        print(f"[오류] 설정 파일({config_file})이 존재하지 않습니다. 스크립트 실행 위치를 확인해주세요.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')

    try:
        data_list_path = config.get('SETTINGS', 'DATA_LIST_PATH')
        root_dir = config.get('SETTINGS', 'ROOT_DIR')
        # 만약 설정 상의 디렉터리 경로 정보가 유효하면 타겟 디렉터리 갱신
        data_dir = os.path.dirname(data_list_path) or '.'
    except Exception as e:
        print(f"[오류] config.ini 설정 정보를 로드하지 못했습니다: {e}")
        sys.exit(1)

    # 2. 최신 Missing_Files_*.xlsx 파일 검색
    search_pattern = os.path.join(data_dir, "Missing_Files_*.xlsx")
    missing_files = glob.glob(search_pattern)

    if not missing_files:
        print(f"[!] '{data_dir}' 폴더 내에서 Missing_Files_*.xlsx 파일을 자동으로 찾을 수 없습니다.")
        user_input = input("-> Missing Files 엑셀 파일의 경로를 직접 입력해주세요: ").strip()
        if not os.path.exists(user_input):
            print(f"[오류] 파일({user_input})이 존재하지 않습니다. 프로그램을 종료합니다.")
            sys.exit(1)
        target_file = user_input
    else:
        target_file = max(missing_files, key=os.path.getmtime)
        print(f"[*] 최신 누락 파일 리스트 자동 탐색 성공: {target_file}")

    # 3. 데이터 로드
    try:
        df = pd.read_excel(target_file)
    except Exception as e:
        print(f"[오류] 파일을 읽는 중 에러가 발생했습니다: {e}")
        sys.exit(1)

    required_cols = ['FULL_PATH', 'COPY_FROM_PATH']
    for col in required_cols:
        if col not in df.columns:
            print(f"[오류] 엑셀 파일에 필수 열('{col}')이 존재하지 않습니다.")
            sys.exit(1)

    # 4. 사용자가 찾지 못한(COPY_FROM_PATH 가 비어있는) 파일 필터링
    # NaN 이거나 빈 문자열인 경우
    unresolved_df = df[df['COPY_FROM_PATH'].isna() | (df['COPY_FROM_PATH'].astype(str).str.strip() == '')].copy()

    if len(unresolved_df) == 0:
        print("\n[알림] 모든 누락 파일에 복사 경로가 지정되어 있습니다. 삭제할 미사용 폴더가 없습니다.")
        sys.exit(0)

    print(f"[*] 파일을 찾지 못한 건수: {len(unresolved_df)}건")

    # 대상 디렉터리 추출
    target_dirs = []
    for idx, row in unresolved_df.iterrows():
        full_path = str(row['FULL_PATH']).strip()
        if full_path:
            dir_path = os.path.dirname(full_path)
            target_dirs.append(dir_path)

    # 중복 제거
    unique_dirs = list(set(target_dirs))
    
    # 디렉터리 깊이가 깊은(긴 경로) 순서대로 정렬하여 
    # 하위 빈 디렉터리를 먼저 지운 후 상위 빈 디렉터리가 지워지도록 유도
    unique_dirs.sort(key=len, reverse=True)

    print(f"[*] 정리 대상 폴더 분석 완료 (고유 폴더 수: {len(unique_dirs)}개)")
    print("[*] 비어있는 폴더 정리 및 삭제 시작...")

    total_deleted = []
    
    for dir_path in unique_dirs:
        # 안전장치 체크: 설정된 root_dir 의 절대경로 획득
        abs_root = os.path.abspath(root_dir)
        abs_dir = os.path.abspath(dir_path)
        
        # ROOT_DIR 하위이고 ROOT_DIR 자체가 아닌지 확인
        if abs_dir.startswith(abs_root) and abs_dir != abs_root:
            deleted = safe_removedirs(abs_dir, abs_root)
            total_deleted.extend(deleted)

    # 중복 기록 제거
    total_deleted = list(set(total_deleted))

    print("=" * 60)
    print(" 4단계 결과 요약")
    print(f" - 스캔한 미해결 폴더 수: {len(unique_dirs)}개")
    print(f" - 삭제 완료된 빈 폴더 수: {len(total_deleted)}개")
    if total_deleted:
        print(" [삭제된 폴더 리스트]")
        for deleted_path in sorted(total_deleted):
            print(f"   - {deleted_path}")
    else:
        print(" - 디렉터리 내에 다른 파일이 존재하여 삭제되지 않았거나 이미 삭제된 상태입니다.")
    print("=============================================================")

if __name__ == '__main__':
    main()
