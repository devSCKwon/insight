# Step 2-1 독립 패키지(단일 EXE, 설정, 샘플) 제작 계획

본 계획은 실제 파일이 위치한 타 네트워크 환경에서 Step 2-1 단계(`step2_1_search_everything.py`)를 독립적으로 구동할 수 있도록, 필요한 모든 구성 요소를 모은 단일 실행 패키지 폴더(`step2_1_package`)를 제작하는 것을 목표로 합니다.

## User Review Required

> [!IMPORTANT]
> - PyInstaller 단일 EXE 파일 생성 시, `Everything64.dll`이 EXE 내부에 내장(번들링)되도록 구성하여 사용자는 추가 DLL 파일 설치 없이 오직 EXE 파일 하나만 실행하면 되도록 제작합니다.
> - EXE 파일 실행 시 외부 `config.ini` 파일 및 실행 폴더 위치를 올바르게 인식하도록 기존 코드의 경로 획득 로직을 고도화(PyInstaller Frozen 환경 탐지 추가)합니다. 이 변경 사항은 기존 파이썬 스크립트 실행(Step 1, Step 3 등)과의 하위 호환성을 100% 유지합니다.

## Open Questions

> [!NOTE]
> 패키지 내부에 샘플 파일로 제공할 엑셀은 이전에 100개 행 테스트용으로 생성했던 `test_missing_100.xlsx`를 `Missing_Files_Sample.xlsx`로 이름을 변경하여 제공할 예정입니다. 이 파일 외에 추가로 포함하고 싶은 샘플 데이터나 파일이 있다면 승인 시 알려주시기 바랍니다.

## Proposed Changes

### 1) [step2_1_search_everything.py](file:///d:/00_Source/devSCKwon/insight/20260604/step2_1_search_everything.py) 수정
- PyInstaller로 패키징된 바이너리(`frozen` 상태) 환경에서도 정상 작동하도록 파일 경로 탐색 방법을 보강합니다.
- `Everything64.dll` 로드 시 `sys._MEIPASS` 지원 추가:
  ```python
  if getattr(sys, 'frozen', False):
      dll_path = os.path.join(sys._MEIPASS, 'Everything64.dll')
  else:
      dll_path = os.path.join(script_dir, 'Everything64.dll')
  ```
- `config.ini` 및 결과 파일 저장 경로의 `frozen` 지원 추가:
  ```python
  if getattr(sys, 'frozen', False):
      exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
  else:
      exe_dir = os.path.dirname(os.path.abspath(__file__))
  config_file = os.path.join(exe_dir, 'config.ini')
  ```

### 2) 독립 구동 패키지 디렉터리 생성
- `20260604` 폴더 하위에 **[NEW] [step2_1_package](file:///d:/00_Source/devSCKwon/insight/20260604/step2_1_package)** 폴더를 신설하고 다음 구성 요소를 포함합니다.
  - **`step2_1_search_everything.exe`**: PyInstaller를 통해 빌드된 단일 실행 파일.
  - **`config.ini`**: 타 네트워크의 Everything 환경에 매핑할 수 있는 가이드라인 주석이 추가된 설정 파일.
  - **`Missing_Files_Sample.xlsx`**: 원본 파일을 매칭하는 작동 원리 확인을 돕기 위한 샘플 엑셀 파일.

---

## 작업 절차 (Execution Steps)

1. **PyInstaller 설치**: 기존 가상환경 `.venv` 내에 `uv pip install pyinstaller` 명령어로 PyInstaller를 설치합니다.
2. **스크립트 경로 수정**: `step2_1_search_everything.py`를 PyInstaller 빌드 호환 구조로 업데이트합니다.
3. **EXE 빌드**: PyInstaller를 사용해 `Everything64.dll`을 포함하는 단일 파일(`--onefile`) EXE 바이너리를 빌드합니다.
   - 빌드 명령어: `pyinstaller --onefile --add-data "Everything64.dll;." step2_1_search_everything.py`
4. **패키징 폴더 구축**: 신규 폴더 `step2_1_package`를 생성하고 EXE 파일, `config.ini`, `Missing_Files_Sample.xlsx`를 한곳에 복사하여 완성합니다.

## Verification Plan

### Automated Tests
- 패키지 폴더 내부의 설정 및 샘플 엑셀 파일 배치 구조를 검사합니다.
- `.venv\Scripts\pyinstaller --version` 확인을 통해 빌드 도구 상태를 검증합니다.
- EXE 빌드 완료 후 테스트 실행을 통해 `Everything64.dll` 로드 및 `config.ini` 읽기가 정상적으로 수행되는지 동작 여부를 검사합니다.
