import os
import glob
import sys
import datetime
import configparser
import pandas as pd

def main():
    print("=" * 60)
    print(" 3단계: robocopy 복사 배치 파일 생성 작업을 시작합니다.")
    print("=" * 60)

    # 1. 설정 파일에서 타겟 폴더 정보 확인 (frozen 대응)
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        
    config_file = os.path.join(exe_dir, 'config.ini')
    data_dir = exe_dir  # 기본 경로
    
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        try:
            data_list_path = config.get('SETTINGS', 'DATA_LIST_PATH')
            data_dir = os.path.dirname(data_list_path) or exe_dir
        except Exception:
            pass

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

    required_cols = ['FULL_PATH', 'COPY_FROM_PATH', 'ALLPATH']
    for col in required_cols:
        if col not in df.columns:
            print(f"[오류] 엑셀 파일에 필수 열('{col}')이 존재하지 않습니다. 파일을 확인해주세요.")
            sys.exit(1)

    # COPY_FROM_PATH가 기입되어 있는 데이터 필터링
    # 비어있는 값 제거 (NaN 및 빈 공백 문자열 제거)
    valid_df = df[df['COPY_FROM_PATH'].notna() & (df['COPY_FROM_PATH'].astype(str).str.strip() != '')].copy()

    if len(valid_df) == 0:
        print("\n[알림] 'COPY_FROM_PATH' 열에 기입된 복사 대상 경로가 없습니다.")
        print("  Missing_Files 엑셀 파일을 열어 노란색 열에 복사할 원본 파일의 경로를 채워주세요.")
        sys.exit(0)

    print(f"[*] 복사 대상 파일 수: 총 {len(valid_df)}건 확인")

    # 4. robocopy 명령어 및 배치 파일 내용 작성
    # 한글 Windows cmd 환경(기본 ANSI/CP949 인코딩)에서 한글 경로가 깨지지 않도록 인코딩 처리가 중요합니다.
    bat_commands = []
    # 배치 파일 상단 인코딩 설정 및 안내 메시지
    bat_commands.append("@echo off")
    bat_commands.append("chcp 949 > nul") # 한글 Windows 기본 코드페이지 설정
    bat_commands.append("echo =========================================")
    bat_commands.append("echo  robocopy 파일 복사 작업을 시작합니다.")
    bat_commands.append("echo =========================================")
    bat_commands.append("")

    command_count = 0
    for idx, row in valid_df.iterrows():
        copy_from = str(row['COPY_FROM_PATH']).strip()
        dest_full_path = str(row['FULL_PATH']).strip()

        if not os.path.exists(copy_from):
            print(f"[경고] 입력된 원본 파일이 실제로 존재하지 않습니다. 스킵합니다: {copy_from}")
            continue

        # 원본 디렉터리와 파일명 분리
        src_dir = os.path.dirname(copy_from)
        src_file = os.path.basename(copy_from)

        # 대상 디렉터리와 파일명 분리
        dest_dir = os.path.dirname(dest_full_path)
        dest_file = os.path.basename(dest_full_path)

        # robocopy 특성상 원본 디렉터리와 대상 디렉터리를 쌍따옴표로 감싸 빈칸 공백 처리 대응
        # 파일명을 지정하여 개별 복사 수행
        # robocopy "[원본폴더]" "[대상폴더]" "[파일명]" /R:3 /W:3 /NP
        robocopy_cmd = f'robocopy "{src_dir}" "{dest_dir}" "{src_file}" /R:3 /W:3 /NP'
        bat_commands.append(f"echo [{command_count + 1}] '{src_file}' 복사 중...")
        bat_commands.append(robocopy_cmd)

        # 예외 상황: 원본 파일명과 대상 파일명이 서로 다른 경우 이름 변경 처리
        if src_file != dest_file:
            # 윈도우 ren 명령어는 대상 파일명만 받으므로 dest_file만 인자로 줌
            rename_cmd = f'if exist "{os.path.join(dest_dir, src_file)}" ( ren "{os.path.join(dest_dir, src_file)}" "{dest_file}" )'
            bat_commands.append(rename_cmd)
        
        bat_commands.append("")
        command_count += 1

    bat_commands.append("echo =========================================")
    bat_commands.append("echo  모든 파일 복사 작업이 완료되었습니다.")
    bat_commands.append("echo =========================================")
    bat_commands.append("pause")

    if command_count == 0:
        print("[!] 실제 복사할 파일에 유효한 정보가 없어 배치 파일 생성을 취소합니다.")
        sys.exit(0)

    # 배치 파일 저장
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bat_filename = f"copy_commands_{timestamp}.bat"
    bat_filepath = os.path.join(data_dir, bat_filename)

    try:
        # cp949 인코딩 에러를 유발하는 \xa0(줄바꿈 없는 공백)을 일반 공백으로 치환
        bat_content = '\n'.join(bat_commands).replace('\xa0', ' ')
        
        # 한글 경로 및 커맨드 창 인코딩 호환성을 위해 cp949로 저장 (인코딩 실패 문자 방지를 위해 errors='replace' 추가)
        with open(bat_filepath, 'w', encoding='cp949', errors='replace') as f:
            f.write(bat_content)
        print(f"[*] 배치 파일 생성 완료: {bat_filepath}")
    except Exception as e:
        print(f"[오류] 배치 파일을 저장하는 중 에러가 발생했습니다: {e}")
        sys.exit(1)

    print("=" * 60)
    print(f" 3단계 결과 요약")
    print(f" - 생성된 배치 파일: {bat_filepath}")
    print(f" - 생성된 복사 명령 수: {command_count}개")
    print(f" [가이드라인]")
    print(f"   - 생성된 '{bat_filepath}' 파일을 더블 클릭하여 실행하거나,")
    print(f"     관리자 권한의 명령 프롬프트(CMD)에서 실행하시면 실제 원본 스토리지 경로로 파일이 일괄 복사됩니다.")
    print("=" * 60)

if __name__ == '__main__':
    main()
