# 데이터 연결 정보 기반 실데이터 유무 확인 및 복사 자동화 프로그램 설계안

이 프로그램은 데이터베이스에서 추출된 파일 목록(`DataList.xlsx`)을 기준으로 실제 스토리지 내 파일 존재 여부를 판별하고, 누락된 파일을 편리하게 복사하여 정상화할 수 있도록 지원하는 단계별 도구 세트입니다.

## 사용자 검토 요구사항

> [!IMPORTANT]
> **디렉터리 자동 생성 기능에 대한 검토**
> 1단계에서 파일이 존재하지 않는 경우, 사용자가 누락된 파일을 직접 이동하거나 복사할 수 있도록 대상 전체 경로의 부모 디렉터리(`FULL_PATH`의 상위 폴더)를 자동으로 생성합니다. 스토리지 용량이 크거나 권한 이슈가 있을 수 있으므로 `ROOT_DIR`에 대한 쓰기 권한이 필요합니다.

> [!NOTE]
> **robocopy 명령어 형식**
> 3단계에서 생성되는 `robocopy` 명령어는 폴더 단위의 복사를 안전하게 처리하기 위해 다음 형식을 취합니다:
> `robocopy "<원본_폴더_경로>" "<대상_폴더_경로>" "<파일명>" /R:3 /W:3 /NP`
> - `/R:3` : 오류 발생 시 3회 재시도
> - `/W:3` : 재시도 간 대기 시간 3초
> - `/NP` : 진행률(%) 미표시 (로그 간소화)

---

## 제안하는 변경 사항

프로젝트 폴더 내에 다음과 같은 파일 구조를 구성하여 단계별 실행이 가능하도록 설계합니다.

```
d:\00_Source\devSCKwon\insight/
├── config.ini                     # 설정 파일 (ROOT_DIR, DATA_LIST_PATH 정의)
├── step1_check_and_prep.py        # 1단계: 실데이터 확인, 엑셀 표기 및 폴더 사전 생성
├── step2_filter_missing.py        # 2단계: 미존재 파일 필터링 및 입력용 엑셀 추출
└── step3_generate_robocopy.py     # 3단계: 사용자 입력 반영 robocopy 배치파일 생성
```

### 1. 설정 파일 (config.ini)

#### [NEW] [config.ini](file:///d:/00_Source/devSCKwon/insight/config.ini)
사용자가 직접 로컬 스토리지의 실제 저장 경로(루트 디렉터리)와 분석 대상 엑셀 경로를 입력하는 파일입니다.
```ini
[SETTINGS]
# 분석 대상 DB 엑셀 파일 경로
DATA_LIST_PATH = 20260604/DataList.xlsx

# 실제 파일들이 저장되어 있는 로컬/네트워크 스토리지의 루트 디렉터리
ROOT_DIR = D:\RealData
```

---

### 2. 1단계: 실데이터 유무 확인 및 대상 폴더 준비

#### [NEW] [step1_check_and_prep.py](file:///d:/00_Source/devSCKwon/insight/step1_check_and_prep.py)
- **역할**: `DataList.xlsx`를 읽어 각 행의 `ALLPATH` 값을 `ROOT_DIR`와 결합한 전체 경로를 생성합니다.
- **주요 로직**:
  1. `config.ini`에서 설정값 읽기.
  2. `DataList.xlsx` 로드 후, `FULL_PATH`, `FILE_EXISTS`, `COPY_FROM_PATH` 컬럼 추가.
  3. `FULL_PATH` 경로에 실제 파일이 있는지 확인 (`os.path.isfile`).
  4. 파일이 **존재하면** `FILE_EXISTS`를 `'O'`로 설정하고, 엑셀 상에서 해당 행을 **연한 초록색**으로 채우기(Style 설정).
  5. 파일이 **존재하지 않으면** `FILE_EXISTS`를 `'X'`로 설정하고, 엑셀 상에서 해당 행을 **연한 빨간색**으로 채운 뒤, `FULL_PATH`가 위치할 디렉터리를 자동 생성 (`os.makedirs(exist_ok=True)`).
  6. 결과 파일 `Result_YYYYMMDD_HHMMSS.xlsx` 저장.

---

### 3. 2단계: 존재하지 않는 파일 필터링 및 복사 필드 구성

#### [NEW] [step2_filter_missing.py](file:///d:/00_Source/devSCKwon/insight/step2_filter_missing.py)
- **역할**: 1단계에서 생성된 `Result_*.xlsx` 파일 중 파일이 없는 항목만 별도로 추출하여 사용자가 복사할 원본 경로를 쉽게 입력할 수 있는 템플릿을 만듭니다.
- **주요 로직**:
  1. 가장 최근에 생성된 `Result_*.xlsx` 파일을 검색하거나 사용자가 경로를 입력하도록 유도.
  2. `FILE_EXISTS == 'X'`인 행들만 필터링.
  3. 사용자가 찾은 대체 파일 경로를 기입할 수 있는 `COPY_FROM_PATH` 컬럼이 비어있는 상태로 `Missing_Files_YYYYMMDD_HHMMSS.xlsx` 생성.
  4. 사용자에게 이 엑셀 파일을 열어 복사하고자 하는 원본 파일의 절대 경로를 기입하도록 안내.

---

### 4. 3단계: robocopy 복사 스크립트(배치 파일) 자동 생성

#### [NEW] [step3_generate_robocopy.py](file:///d:/00_Source/devSCKwon/insight/step3_generate_robocopy.py)
- **역할**: 사용자가 `COPY_FROM_PATH`를 채워 넣은 `Missing_Files_*.xlsx` 파일을 읽어 일괄 복사를 수행할 수 있는 Windows `robocopy` 배치 파일(`.bat`)을 작성합니다.
- **주요 로직**:
  1. 사용자가 입력을 마친 `Missing_Files_*.xlsx` 파일을 로드.
  2. `COPY_FROM_PATH`에 값이 기입된 행만 추출.
  3. 각 행에 대해 원본 파일 경로(`COPY_FROM_PATH`)와 대상 경로(`FULL_PATH`)를 분해:
     - 원본 디렉터리 (`src_dir`), 원본 파일명 (`src_file`)
     - 대상 디렉터리 (`dest_dir`), 대상 파일명 (`dest_file`)
  4. `robocopy` 명령어 라인 생성:
     `robocopy "<src_dir>" "<dest_dir>" "<src_file>" /Y`
     *(참고: 파일명이 다를 경우 복사 후 이름 변경이 필요할 수 있으나, 기본적으로 복사 시 파일명은 동일하다고 가정하여 처리. 만약 파일명이 다를 경우, 임시 복사 후 `ren` 명령어를 사용하거나, Python 내에서 직접 shutil로 복사하는 예외 대응 추가)*
  5. 모든 복사 명령어를 `copy_commands_YYYYMMDD_HHMMSS.bat` 파일에 기록.
  6. 사용자에게 이 배치 파일을 관리자 권한으로 실행하도록 안내.

---

## 검증 계획

### 자동 및 수동 테스트
1. **1단계 테스트**:
   - `config.ini` 경로를 임의의 테스트용 폴더 `D:\TestData`로 설정.
   - `DataList.xlsx`를 임시 생성하거나 기존 파일의 앞부분 10개 행만 추출한 테스트용 데이터로 검증 수행.
   - 실제로 일부 파일은 경로에 배치해 두고, 일부는 비워둠.
   - 스크립트 실행 후 `Result_*.xlsx` 파일에 색상이 올바르게 채색되었는지, 존재하지 않는 파일의 폴더가 `D:\TestData/...` 아래에 잘 생성되었는지 확인.
2. **2단계 테스트**:
   - 생성된 `Result_*.xlsx`를 기반으로 `step2_filter_missing.py` 실행.
   - `Missing_Files_*.xlsx`가 잘 생성되었는지 확인 및 수동으로 `COPY_FROM_PATH` 열에 임시 원본 경로 기입.
3. **3단계 테스트**:
   - `step3_generate_robocopy.py`를 실행하여 `.bat` 배치 파일이 올바른 구문으로 생성되는지 확인.
   - 배치 파일을 실행했을 때 실제로 파일이 대상 폴더로 완벽하게 이동/복사되는지 검증.
