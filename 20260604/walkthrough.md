# 실데이터 유무 파악 및 복사 자동화 프로그램 사용 가이드라인 (20260604 폴더 전용)

본 프로젝트는 데이터베이스의 연결 정보가 담긴 엑셀 목록(`DataList.xlsx`)을 기준으로 실제 파일이 물리 디렉터리에 존재하는지 확인하고, 유실된 데이터를 사용자가 매핑한 원본 경로로부터 안전하게 복사(`robocopy`)할 수 있도록 지원하는 단계별 도구 세트입니다.

모든 소스 코드와 설정 파일, 그리고 결과물이 **`20260604`** 폴더 내에서 진행되도록 정리되었습니다.

---

## 📂 최종 구현된 파일 구조

```
d:\00_Source\devSCKwon\insight/
└── 20260604/                      # 모든 소스 파일 및 작업이 일어나는 전용 폴더
    ├── DataList.xlsx              # 분석 대상 원본 DB 엑셀 파일
    ├── config.ini                 # 사용자 정의 설정 (실제 저장소 루트, 타겟 엑셀 정의)
    ├── step1_check_and_prep.py    # 1단계: 실데이터 확인, 엑셀 채색 및 부모 폴더 자동 생성
    ├── step2_filter_missing.py    # 2단계: 누락 파일 필터링 및 입력 템플릿 엑셀 생성
    └── step3_generate_robocopy.py # 3단계: 복사용 robocopy 명령어 배치 파일(.bat) 생성
```

---

## 🚀 단계별 실행 및 사용법

모든 명령어는 cmd 또는 터미널에서 **`20260604`** 디렉터리로 이동한 후 실행해주십시오.
```bash
# 20260604 폴더로 이동 (Windows cmd 기준)
cd 20260604
```

### ⚙️ 0. 환경 설정 (`config.ini`)
[config.ini](file:///d:/00_Source/devSCKwon/insight/20260604/config.ini) 파일을 열어 사용자의 실행 환경에 맞게 경로를 수정합니다.
- `DATA_LIST_PATH`: 분석 대상이 되는 파일 목록 엑셀 파일명 (기본값: `DataList.xlsx`)
- `ROOT_DIR`: 실제 파일들이 복사되어 저장될 로컬/네트워크 스토리지의 루트 디렉터리 경로

---

### 🔍 1단계: 실데이터 유무 확인 및 폴더 생성
**실행 명령어:**
```bash
uv run python step1_check_and_prep.py
```
- **수행 동작**: 
  - `DataList.xlsx`를 읽어 `ALLPATH` 값과 `ROOT_DIR`를 결합하여 전체 물리 경로를 파악합니다.
  - 파일의 존재 여부(`FILE_EXISTS`)를 판단하여 `Result_YYYYMMDD_HHMMSS.xlsx` 파일을 생성합니다.
  - 엑셀 내에서 파일이 존재하면 **연한 초록색**, 존재하지 않으면 **연한 빨간색**으로 스타일을 채색합니다.
  - **파일이 존재하지 않는 경우**, 해당 파일이 들어가야 할 부모 폴더 경로가 없다면 폴더를 자동으로 생성합니다.

---

### 📋 2단계: 누락 데이터 필터링 및 입력 서식 생성
**실행 명령어:**
```bash
uv run python step2_filter_missing.py
```
- **수행 동작**:
  - 가장 최근에 생성된 1단계 `Result_*.xlsx` 결과 파일을 자동으로 검색하여 읽어들입니다.
  - 파일이 없는(`FILE_EXISTS == 'X'`) 행만 따로 필터링하여 `Missing_Files_YYYYMMDD_HHMMSS.xlsx`를 생성합니다.
  - 사용자가 입력을 쉽게 할 수 있도록 복사용 원본 경로를 입력할 `COPY_FROM_PATH` 열을 **연한 노란색**으로 색칠하여 눈에 띄게 합니다.
- **사용자 행동 요구사항**:
  - 생성된 `Missing_Files_*.xlsx` 파일을 엽니다.
  - 노란색으로 칠해진 `COPY_FROM_PATH` 열에 사용자가 직접 찾아낸 원본 파일의 **절대 경로**를 입력하고 저장합니다.
    *(예시: `C:\Users\Name\Downloads\sejin_logo.png`)*

---

### 💾 3단계: robocopy 복사 배치 파일 생성
**실행 명령어:**
```bash
uv run python step3_generate_robocopy.py
```
- **수행 동작**:
  - 가장 최근에 생성된 `Missing_Files_*.xlsx`를 자동 탐색하여 읽습니다.
  - 사용자가 `COPY_FROM_PATH` 컬럼에 경로를 입력한 행들을 추출합니다.
  - 각 파일에 대해 안전하고 빠른 파일 복사를 수행할 수 있는 Windows `robocopy` 명령어를 생성합니다.
  - 한글 윈도우 커맨드 창(CMD)에서 한글 경로가 깨지지 않도록 **ANSI(CP949) 인코딩**으로 `copy_commands_YYYYMMDD_HHMMSS.bat` 배치 파일을 생성합니다.
- **사용자 행동 요구사항**:
  - 생성된 `.bat` 배치 파일을 더블 클릭하여 실행하거나, 관리자 권한의 CMD 창에서 실행합니다.
  - 복사가 정상 완료되면 원본 경로에 파일들이 저장됩니다.

---

## 🛠️ 최종 EXE 단일 파일 빌드 가이드 (PyInstaller 사용)

테스트를 마친 스크립트들을 최종 사용자가 파이썬 설치 없이 실행할 수 있도록 단일 실행 파일(`.exe`)로 만들 때 다음 방식을 사용하십시오.

1. **PyInstaller 설치** (`uv` 가상환경 내):
   ```bash
   uv pip install pyinstaller
   ```

2. **각 스텝별 단일 EXE 빌드 명령어**:
   `20260604` 폴더 안에서 아래 명령어를 실행하여 빌드합니다.
   ```bash
   pyinstaller --onefile --console step1_check_and_prep.py
   pyinstaller --onefile --console step2_filter_missing.py
   pyinstaller --onefile --console step3_generate_robocopy.py
   ```
   - 빌드가 완료되면 `dist/` 폴더 내에 `step1_check_and_prep.exe`, `step2_filter_missing.exe`, `step3_generate_robocopy.exe` 파일이 생성됩니다.
   - 실행 시 EXE 파일들과 동일한 경로상에 `config.ini` 파일이 존재해야 정상 작동합니다.

---

## 🧪 테스트 및 검증 결과 보고 (20260604 폴더 전용 테스트)

20260604 폴더 내에 가상 모의 테스트 환경을 재구성하여 프로그램이 정상 작동함을 완벽히 재검증하였습니다.

1. **테스트 데이터 구성**:
   - `test_real_storage/`: 타겟 실제 저장소 (대상)
   - `test_source_files/`: 사용자가 복사해 올 파일 소스 폴더
   - `TestDataList.xlsx`: folderA/file1.txt (존재), folderB/file2.txt (누락), folderC/subfolder/file3.txt (누락)로 구성된 모의 DB 목록
2. **검증 이력**:
   - `step1_check_and_prep.py`를 실행하여 존재 확인 결과가 채색된 `Result_*.xlsx` 생성 완료 및 `test_real_storage/folderB`, `test_real_storage/folderC/subfolder` 디렉터리가 생성되는 것을 확인.
   - `step2_filter_missing.py`를 실행하여 누락 파일만 필터링한 입력 대기용 `Missing_Files_*.xlsx` (입력 유도 노란색 하이라이팅 적용) 정상 생성 확인.
   - 시뮬레이션 프로그램을 통해 누락 파일의 원본 절대 경로를 노란색 열에 기입.
   - `step3_generate_robocopy.py`를 실행하여 ANSI 인코딩으로 저장된 배치 파일 `copy_commands_*.bat` 정상 생성 확인.
   - 해당 배치 파일을 실행하여 `test_real_storage`에 `file2.txt`와 `file3.txt` 파일이 완벽하게 복사 및 복원되는 것을 검증 완료.
