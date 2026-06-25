# 구현 완료 결과 및 검증 보고서

암호화된 파일 리스트를 스캔하고, 암호화 확장자를 제외한 원본 파일의 정보를 복원하여 엑셀 파일로 추출하는 단독 실행용 도구 개발 및 빌드를 완료하였습니다.

## 작업 완료 사항

1. **설정 파일 구성**:
   - [config.ini](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/config.ini)
   - 암호화된 파일이 저장되어 있는 드라이브 경로(`encrypted_drive_path`), 결과 엑셀이 저장될 드라이브 경로(`output_drive_path`), 그리고 암호화된 파일 확장자(`encrypted_extension` : `4dhYmt2Ei` 또는 `.4dhYmt2Ei` 형태로 지원)를 설정할 수 있습니다.

2. **메인 파이썬 스크립트 작성**:
   - [decrypt_file_list.py](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/decrypt_file_list.py)
   - `os.walk`를 사용해 지정된 암호화 파일 드라이브의 하위 폴더들을 재귀적으로 안전하게 탐색합니다.
   - 마지막 확장자가 대상 암호화 확장자(대소문자 무시)와 일치하는 경우 필터링합니다.
   - 파일의 부모 폴더명, 파일의 FullPath, 암호화 확장자가 제외된 원본 파일명, 원본 파일의 확장자를 복원하여 수집합니다.
   - `pandas`와 `openpyxl`을 사용해 디자인이 깔끔하게 입혀진 엑셀 문서를 출력합니다 (자동 열 폭 조절, 스타일 가독성 극대화).

3. **배치 파일 제공**:
   - [build_exe.bat](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/build_exe.bat): 파이썬 소스 파일을 단독 실행 파일인 `decrypt_file_list.exe`로 간편하게 빌드하고 불필요한 빌드 부산물을 정리해 줍니다.
   - [run_decrypt.bat](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/run_decrypt.bat): 빌드하지 않고 가상환경 파이썬으로 직접 실행해 리스트를 스캔할 수 있도록 편의성을 제공합니다.

4. **단독 실행 파일 빌드 완료**:
   - `PyInstaller`를 사용해 [decrypt_file_list.exe](file:///d:/00_Source/devSCKwon/insight/20260608_decrytion_fileList/decrypt_file_list.exe) 단독 실행 파일을 `20260608_decrytion_fileList` 디렉터리에 빌드 완료하였습니다.

## 검증 결과 요약

- **목업 데이터 생성**: `mock_drive`에 `.4dhYmt2Ei` 확장자를 가진 파일 5개와 일반 파일(`그림.png`) 1개를 생성하여 스캔 환경을 모사했습니다.
- **실행 결과**:
  - `decrypt_file_list.exe`는 성공적으로 구동되어 5개의 암호화 파일만을 인식했습니다.
  - 생성된 엑셀 파일 `암호화파일리스트_복원정보_20260608_163852.xlsx`를 읽어 데이터 정합성을 확인한 결과는 다음과 같습니다.

| | 폴더명 | 전체경로 (FullPath) | 원본파일명 | 원본확장자 |
|-|---|---|---|---|
| 0 | mock_drive | `.../mock_drive/문서1.xlsx.4dhYmt2Ei` | 문서1.xlsx | .xlsx |
| 1 | mock_drive | `.../mock_drive/발표자료.pptx.4dhYmt2Ei` | 발표자료.pptx | .pptx |
| 2 | subfolder | `.../mock_drive/subfolder/보고서.docx.4dhYmt2Ei` | 보고서.docx | .docx |
| 3 | subfolder2 | `.../mock_drive/subfolder2/데이터.csv.4dhYmt2Ei` | 데이터.csv | .csv |
| 4 | subfolder2 | `.../mock_drive/subfolder2/이미지.jpeg.4dhYmt2Ei` | 이미지.jpeg | .jpeg |

- 모든 항목이 누락 없이 원본 파일명 및 원본 확장자로 깔끔하게 복원되어 수집되었음을 확인했습니다.
