# 실데이터 유무 파악 및 복사 자동화 프로그램 사용 가이드라인 (4단계 반영 완료)

본 프로젝트는 데이터베이스의 연결 정보가 담긴 엑셀 목록(`DataList.xlsx`)을 기준으로 실제 파일이 물리 디렉터리에 존재하는지 확인하고, 유실된 데이터를 사용자가 매핑한 원본 경로로부터 안전하게 복사(`robocopy`)할 수 있도록 지원하는 단계별 도구 세트입니다.

---

## 📂 최종 구현된 파일 구조

모든 소스 코드와 설정 파일, 그리고 결과물이 **`20260604`** 폴더 하위에서 깔끔하게 작동합니다.

```
d:\00_Source\devSCKwon\insight/
└── 20260604/                      # 모든 소스 파일 및 작업이 일어나는 전용 폴더
    ├── DataList.xlsx              # 분석 대상 원본 DB 엑셀 파일
    ├── config.ini                 # 사용자 정의 설정 (실제 저장소 루트, 타겟 엑셀 정의)
    ├── step1_check_and_prep.py    # 1단계: 실데이터 확인, 엑셀 채색 및 부모 폴더 자동 생성
    ├── step2_filter_missing.py    # 2단계: 누락 파일 필터링 및 입력 템플릿 엑셀 생성
    ├── step3_generate_robocopy.py # 3단계: 복사용 robocopy 명령어 배치 파일(.bat) 생성
    └── step4_cleanup_unused_dirs.py # 4단계 (옵션): 파일을 찾지 못해 비어 있는 채로 남겨진 폴더 청소
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
- `ROOT_DIR`: 실제 파일들이 복사되어 저장될 로컬/네트워크 스토리지의 루트 디렉터리 경로 (현재 `E:\Aras_221225\Aras\Vault\SEJINPLM`로 설정됨)

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

### 🧹 4단계 (옵션): 미기입(찾지 못한) 누락 파일의 빈 폴더 정리
**실행 명령어:**
```bash
uv run python step4_cleanup_unused_dirs.py
```
- **수행 동작**:
  - 사용자가 결국 파일을 찾지 못해 `COPY_FROM_PATH`를 **비워둔 채 저장한** `Missing_Files_*.xlsx`를 읽습니다.
  - 해당 파일들을 위해 1단계에서 불필요하게 선제 생성되었던 빈 디렉터리들을 탐색하여 안전하게 삭제합니다.
- **주요 안전장치 및 구현 로직**:
  - **비어있는 폴더만 삭제**: 디렉터리 내부에 다른 유효한 파일이나 폴더가 존재할 경우 절대 삭제하지 않고 보존합니다.
  - **ROOT_DIR 경계 제한**: 실수로 시스템 폴더나 저장소 외부의 디렉터리가 삭제되는 것을 막기 위해, 반드시 설정된 `ROOT_DIR` 하위의 폴더들만 삭제되도록 안전 장치가 적용되어 있습니다.
  - **상위 폴더 재귀 삭제**: 하위 디렉터리 삭제 후, 부모 디렉터리도 비게 되면 `ROOT_DIR` 경계에 도달하기 전까지 연속적으로(재귀적으로) 청소합니다.

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
   pyinstaller --onefile --console step4_cleanup_unused_dirs.py
   ```
   - 빌드가 완료되면 `dist/` 폴더 내에 4개의 단일 실행파일(`.exe`)이 생성됩니다.
   - 실행 시 EXE 파일들과 동일한 경로상에 `config.ini` 파일이 존재해야 정상 작동합니다.

---

## 🧪 테스트 및 검증 결과 보고 (4단계 포함)

가상 모의 환경을 만들어 프로그램의 안정성을 성공적으로 재검증하였습니다.

1. **테스트 시나리오 데이터 구성**:
   - `file1.txt` (존재함)
   - `file2.txt` (누락됨 -> 사용자가 끝내 파일을 찾지 못해 복사 경로를 비워둠)
   - `file3.txt` (누락됨 -> 사용자가 복사 경로를 정상 매핑하여 복사 완료함)
2. **4단계 검증 이력**:
   - `file3.txt`가 정상 복사되어 존재하는 `folderC/subfolder`는 비어있지 않으므로 삭제 대상에서 자동으로 안전하게 보존되었습니다.
   - 원본 경로를 찾지 못해 기입하지 않은 `file2.txt` 대상 폴더 `folderB`는 내부가 비어있었으므로 정상 스캔되어 삭제되었습니다.
   - 디렉터리 내에 다른 파일이 들어있는 경우의 보존 기능과 완전히 빈 하위 폴더만 계층적으로 안전하게 정리해주는 로직의 동작 신뢰성을 최종 입증 완료했습니다.
