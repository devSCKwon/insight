# 암호화 파일 리스트 추출 및 원본 복원 정보 엑셀 저장 도구 구현 계획

이 프로젝트는 암호화된 파일이 저장되어 있는 경로를 스캔하여, 지정된 암호화 확장자를 제거한 원본 파일의 정보를 파악하고, 이를 엑셀 파일로 출력하는 파이썬 기반의 도구를 구현하는 것입니다. 또한, 사용자 PC에서 단독 실행 가능하도록 PyInstaller 설정을 제공합니다.

## 사용자 검토 요구사항

> [!NOTE]
> - **가상환경**: 루트 디렉터리에 위치한 기존 `.venv` 가상환경을 그대로 사용합니다.
> - **단독 실행 파일(EXE) 빌드**: `pyinstaller` 라이브러리를 사용하여 단독 실행 파일로 컴파일할 수 있도록 지원합니다.

## 미해결 질문

- **암호화 확장자 처리**: 만약 파일명이 `data.xlsx.enc`라면 마지막 `.enc`를 제거하고 파일명은 `data`이고 확장자는 `.xlsx`가 됩니다. 만약 암호화 확장자가 없는 파일(예: `readme.txt`)이 암호화 경로에 섞여 있을 때, 이 파일들을 무시할지 혹은 엑셀에 별도 표시할지 결정이 필요합니다. (기본적으로는 지정한 암호화 확장자로 끝나는 파일만 처리하도록 구현하겠습니다.)

## 제안된 변경 사항

---

### [암호화 파일 리스트 스캔 도구] (20260608_decrytion_fileList)

#### [NEW] [config.ini](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/config.ini)
암호화된 파일 경로, 결과 엑셀 파일 저장 경로, 대상 암호화 확장자를 설정하는 파일입니다.
```ini
[PATH]
# 암호화된 파일들이 위치한 드라이브 또는 폴더 경로
encrypted_drive_path = D:\EncryptedData
# 결과 엑셀 파일이 저장될 드라이브 또는 폴더 경로
output_drive_path = D:\OutputResult

[FILE]
# 대상 암호화 확장자 (대소문자 구분 없이 처리하며, 점(.)은 포함 여부와 상관없이 자동 처리됨)
encrypted_extension = .enc
```

#### [NEW] [decrypt_file_list.py](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/decrypt_file_list.py)
설정 파일을 읽고 지정된 디렉터리를 재귀적으로 탐색하여 암호화된 파일들의 목록을 가공한 뒤 엑셀 파일로 추출하는 메인 파이썬 스크립트입니다.
- 기능:
  - `config.ini` 파일 읽기 및 입력값 검증
  - 지정 경로 하위의 모든 파일 탐색
  - 지정한 암호화 확장자로 끝나는 파일 필터링
  - 파일 정보 추출:
    - 폴더명 (파일이 위치한 직속 부모 폴더의 이름)
    - FullPath (전체 파일 경로)
    - 원본 파일명 (암호화 확장자를 제거한 파일명)
    - 원본 확장자 (암호화 확장자를 제거한 상태의 파일 확장자)
  - 엑셀 파일 생성 및 저장
  - 에러 처리 및 진행 표시

#### [NEW] [build_exe.bat](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/build_exe.bat)
파이썬 스크립트를 단독 실행 파일(.exe)로 빌드하는 배치 스크립트입니다. `pyinstaller`를 사용하며, 콘솔 창을 표시하도록 설정하여 진행 상황이나 에러 메시지를 볼 수 있도록 지원합니다.

#### [NEW] [run_decrypt.bat](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/run_decrypt.bat)
사용자가 로컬 가상환경 환경에서 파이썬 코드를 즉시 실행해볼 수 있도록 돕는 간단한 배치 실행 스크립트입니다.

---

## 검증 계획

### 자동화 테스트
- `decrypt_file_list.py` 내부의 경로 파싱 함수 및 파일명 복원 로직을 검증하는 모의 테스트를 수행합니다.

### 수동 검증
1. 임시 암호화 테스트 폴더 생성 (예: `D:\TestEncrypted`) 및 가상 파일 생성 (`test1.docx.enc`, `test2.pdf.enc`, `subfolder/test3.xlsx.enc`, `no_enc.txt` 등)
2. `config.ini`를 적절히 설정
3. `decrypt_file_list.py` 실행
4. 지정한 `output_drive_path`에 생성된 엑셀 파일(`decrypted_file_list_YYYYMMDD_HHMMSS.xlsx`) 확인 및 데이터 정합성 검증 (폴더명, FullPath, 원본파일명, 확장자가 올바른지)
5. `pyinstaller`로 단독 실행 파일 빌드 진행 및 빌드된 `decrypt_file_list.exe`를 통해 동일 동작이 수행되는지 검증
