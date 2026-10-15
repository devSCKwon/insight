# 네이버웍스 조직도 담당 업무 등록 및 검색 개선 가이드

본 문서는 네이버웍스(NAVER WORKS) 조직도 내에 임직원 담당 업무를 체계적으로 등록하고, 사내 구성원들이 업무 키워드로 담당자를 신속하게 검색할 수 있도록 안내하는 가이드 프로젝트 산출물입니다.

---

## 1. 프로젝트 개요

- **프로젝트 명칭**: 네이버웍스 조직도 담당 업무 등록 및 검색 개선 가이드
- **슬로건**: "핵심 키워드 30자로 사내 소통과 업무 담당자 탐색을 한 번에 연결하다"
- **작성 기준일**: 2026년 10월 15일
- **소속 부서**: 경영지원본부 전산팀
- **적용 대상**: 전사 임직원 및 사내 구성원 전체
- **핵심 목표**:
  1. **PC앱 기본 노출(Default View) 최적화**: 1~2줄로 노출되는 화면 특성에 맞춘 30자 키워드 표준화
  2. **사용자 직접 등록 프로세스 정립**: PC웹 개인정보 - 내 프로필을 통한 자가 최신화 유도
  3. **전 디바이스 실시간 검색 지원**: PC앱, PC웹, 모바일앱 어디서나 업무명(DB, ERP, 급여 등) 검색 즉시 연결
  4. **현행 조직도 기반 표준 작성 가이드 제공**: 경영지원, 연구개발, 영업구매, 생산, 품질본부 맞춤 예시 제시

---

## 2. 산출물 파일 구성

| 파일명 | 형식 | 설명 |
| :--- | :---: | :--- |
| [**`naver_works_organization_duty_guide.html`**](file:///d:/00_Source/devSCKwon/insight/20261015/naver_works_organization_duty_guide.html) | HTML | 메인 인터랙티브 웹 뷰어 (반응형 사이드바, 갤러리 이미지 모달 팝업, 키워드 테이블, 퀵 액션 배너) |
| [**`index.html`**](file:///d:/00_Source/devSCKwon/insight/20261015/index.html) | HTML | GitHub Pages 정적 웹 호스팅용 엔트리 파일 (`naver_works_organization_duty_guide.html`과 동일) |
| [**`Docs/static_page_update_guide.md`**](file:///d:/00_Source/devSCKwon/insight/20261015/Docs/static_page_update_guide.md) | Markdown | **정적 웹페이지 배포 및 업데이트 명령어 사용 가이드 (PowerShell/Bash 명령어 및 절차 매뉴얼)** |
| [**`Docs/naver_works_organization_duty_guide_content.md`**](file:///d:/00_Source/devSCKwon/insight/20261015/Docs/naver_works_organization_duty_guide_content.md) | Markdown | 텍스트 콘텐츠 수정용 마크다운 파일 (문구 수정, 키워드 추가 후 HTML 동기화 가능) |
| [**`Docs/original_instruction.md`**](file:///d:/00_Source/devSCKwon/insight/20261015/Docs/original_instruction.md) | Markdown | 사용자 원본 지시문 및 개선 요구사항 히스토리 보관 문서 |
| [**`Docs/NAVER_WORKS_organization_download.csv`**](file:///d:/00_Source/devSCKwon/insight/20261015/Docs/NAVER_WORKS_organization_download.csv) | CSV | 현행 사내 조직도 다운로드 원본 데이터 |
| [**`images/`**](file:///d:/00_Source/devSCKwon/insight/20261015/images/) | Assets | 가이드 화면 캡처 이미지 (`1.png`: PC앱 기본 노출, `2.png`: PC웹 입력란, `3.png`: 검색 화면) |
| [**`README.md`**](file:///d:/00_Source/devSCKwon/insight/20261015/README.md) | Markdown | 본 프로젝트 개요, 구조 및 정적 웹 배포 안내 문서 |

---

## 3. 정적 웹페이지(GitHub Pages) 게시 정보

본 저장소의 `dev` 및 `master` 브랜치는 GitHub Actions(`.github/workflows/static.yml`)를 통해 GitHub Pages로 자동 배포됩니다.

- **저장소**: [devSCKwon/insight](https://github.com/devSCKwon/insight)
- **온라인 게시 URL**:
  - `https://devsckwon.github.io/insight/20261015/`
  - `https://devsckwon.github.io/insight/20261015/naver_works_organization_duty_guide.html`
- **배포 가이드 문서**: [Docs/static_page_update_guide.md](file:///d:/00_Source/devSCKwon/insight/20261015/Docs/static_page_update_guide.md)

---

## 4. 작업 히스토리

### 2026-10-15 (1차 구축)
- 원본 지시사항(`Docs/original_instruction.md`) 수집 및 분석.
- 텍스트 수정용 마크다운(`Docs/naver_works_organization_duty_guide_content.md`) 및 인터랙티브 웹페이지(`naver_works_organization_duty_guide.html`) 최초 구축.
- 3대 환경(PC앱, PC웹, 모바일앱) 특성 분석 및 3종 캡처 이미지 모달 팝업 연동.

### 2026-10-15 (2차 개선: 이미지 최적화 및 조직도 반영)
- PC웹 입력란(`images/2.png`) 이미지 크기 최적화 (정갈한 카드 비율 조정).
- 세진 조직도 다운로드 CSV(`Docs/NAVER_WORKS_organization_download.csv`)를 기반으로 부서별 30자 키워드 추천 예시 전면 개편.
- 관련 MD 문서 동기화 완료.

### 2026-10-15 (3차: GitHub Pages 정적 웹페이지 배포)
- 디렉토리 접근용 `index.html` 생성 및 GitHub Pages 배포 연동.
- Git 저장소(`origin/dev`) 푸시를 통한 자동 정적 호스팅 개시.

### 2026-10-15 (4차: 정적 페이지 배포 가이드 문서 작성)
- 원본 HTML 수정 후 간편하게 정적 페이지를 업데이트할 수 있도록 명령어 가이드 문서(`Docs/static_page_update_guide.md`) 작성.
- 인덱스 동기화, Git 커밋, 원격 푸시 절차 및 트러블슈팅 매뉴얼 완비.
