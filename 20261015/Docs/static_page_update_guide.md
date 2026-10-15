# 네이버웍스 조직도 가이드 정적 페이지 배포 및 업데이트 매뉴얼 (Cmder 환경)

본 문서는 `20261015` 프로젝트의 HTML 및 관련 문서 변경 사항을 **Cmder 콘솔** 환경에서 Git 저장소(`dev` 브랜치)와 GitHub Pages 정적 웹사이트에 간편하게 반영(배포)하기 위한 명령어 사용 가이드입니다.

---

## 1. 정적 배포 구조 및 프로세스 개요

1. **원본 문서 수정**: [`naver_works_organization_duty_guide.html`](file:///d:/00_Source/devSCKwon/insight/20261015/naver_works_organization_duty_guide.html) 내용 수정.
2. **인덱스 동기화**: 디렉터리 경로 접속용 [`index.html`](file:///d:/00_Source/devSCKwon/insight/20261015/index.html)에 원본 HTML 내용을 복사(`cp` 또는 `copy`)하여 덮어쓰기.
3. **Git 스테이징 및 커밋**: 수정된 파일들을 Git에 기록 (`git add` & `git commit`).
4. **원격 저장소 푸시 (`origin dev`)**: GitHub의 `dev` 브랜치로 푸시.
5. **GitHub Actions 자동 배포**: [`.github/workflows/static.yml`](file:///d:/00_Source/devSCKwon/insight/.github/workflows/static.yml) 워크플로우가 자동으로 실행되어 GitHub Pages에 최신 정적 사이트 게시.

---

## 2. Cmder 전용 원클릭 명령어 (한 번에 실행)

Cmder 콘솔창에 아래 한 줄(One-liner) 또는 순차 명령어를 그대로 복사·붙여넣기(마우스 우클릭 또는 `Ctrl + V`)하여 실행하시면 배포가 한 번에 완료됩니다.

### ① Cmder 한 줄(One-liner) 실행 (가장 추천)

```bash
cp 20261015/naver_works_organization_duty_guide.html 20261015/index.html && git add 20261015/ && git commit -m "docs: update 2026-10-15 naver works duty guide static pages" && git push origin dev
```

---

### ② Cmder 단계별 순차 실행

```bash
# 1. 원본 HTML을 index.html로 덮어쓰기 복사 (Cmder 내장 cp 명령어)
cp 20261015/naver_works_organization_duty_guide.html 20261015/index.html

# 2. 20261015 디렉터리 변경 사항 스테이징
git add 20261015/

# 3. 커밋 생성
git commit -m "docs: update 2026-10-15 naver works duty guide static pages"

# 4. GitHub dev 브랜치로 푸시 (자동 배포 실행)
git push origin dev
```

> [!NOTE]
> **Windows 기본 명령 프롬프트(CMD) 구문을 선호하실 경우**:  
> `cp` 대신 `copy /y 20261015\naver_works_organization_duty_guide.html 20261015\index.html`을 사용하셔도 완벽하게 동작합니다.

---

## 3. 단계별 세부 명령어 및 검증 가이드

### STEP 1. 원본 HTML 내용을 `index.html`로 동기화

GitHub Pages는 폴더 URL(`.../20261015/`)로 접근했을 때 자동으로 `index.html`을 찾아 엽니다. 원본 파일 수정 후 반드시 복사를 진행해야 합니다.

- **Cmder (리눅스 호환 모드)**:
  ```bash
  cp 20261015/naver_works_organization_duty_guide.html 20261015/index.html
  ```
- **Windows CMD 네이티브 방식**:
  ```cmd
  copy /y 20261015\naver_works_organization_duty_guide.html 20261015\index.html
  ```

---

### STEP 2. 변경 파일 상태 확인 (`git status`)

변경된 파일 내역과 스테이징 대상이 정상적으로 인식되는지 확인합니다:

```bash
git status
```

> **정상 출력 예시**:
> ```text
> On branch dev
> Your branch is up to date with 'origin/dev'.
> 
> Changes not staged for commit:
>   modified:   20261015/naver_works_organization_duty_guide.html
>   modified:   20261015/index.html
> ```

---

### STEP 3. 스테이징 및 커밋 (`git add` & `git commit`)

수정된 파일들을 Git 스테이징 영역에 추가하고 커밋합니다:

```bash
# 20261015 폴더 전체 추가
git add 20261015/

# 커밋 실행
git commit -m "docs: update 2026-10-15 naver works duty guide static pages"
```

---

### STEP 4. 원격 저장소 푸시 (`git push origin dev`)

GitHub 원격 저장소의 `dev` 브랜치로 푸시합니다:

```bash
git push origin dev
```

> **동작 설명**:  
> 푸시가 완료되면 GitHub Actions의 `Deploy static content to Pages` 워크플로우가 1~2분 이내에 자동으로 실행되어 호스팅 사이트를 최신 상태로 갱신합니다.

---

### STEP 5. 배포 완료 확인 및 웹페이지 접속

배포 후 웹 브라우저에서 아래 URL로 접속하여 변경 내용이 잘 반영되었는지 확인합니다:

- **디렉터리 대표 URL**:  
  👉 [https://devsckwon.github.io/insight/20261015/](https://devsckwon.github.io/insight/20261015/)
- **파일명 직접 호출 URL**:  
  👉 [https://devsckwon.github.io/insight/20261015/naver_works_organization_duty_guide.html](https://devsckwon.github.io/insight/20261015/naver_works_organization_duty_guide.html)

> [!TIP]
> **브라우저 캐시 주의사항**:  
> 배포 직후 이전 버전 화면이 캐시되어 보일 수 있습니다. 브라우저에서 **`Ctrl + F5`**(강력 새로고침) 또는 **`Ctrl + Shift + R`**을 눌러 최신 화면을 확인하세요.

---

## 4. 문제 해결 (Troubleshooting)

| 상황 | 원인 | 해결 방법 |
| :--- | :--- | :--- |
| `Copy-Item: 명령어를 찾을 수 없습니다` | PowerShell 전용 명령어를 Cmder(CMD)에서 입력함 | `Copy-Item` 대신 Cmder 지원 명령어인 **`cp`** 또는 **`copy /y`** 사용 |
| 웹페이지에 수정 전 내용이 계속 보임 | `index.html`에 복사하지 않았거나 브라우저 캐시 | `cp ... index.html` 복사 후 커밋/푸시, 브라우저에서 `Ctrl + F5` 실행 |
| `git push` 시 reject 에러 발생 | 원격 저장소에 새로운 커밋이 이미 존재함 | `git pull origin dev --rebase` 수행 후 다시 `git push origin dev` |
| GitHub Pages 404 Not Found | GitHub Actions 배포 진행 중이거나 브랜치 불일치 | 푸시 후 약 1~2분 대기 후 재접속. 저장소의 `dev` 브랜치가 대상인지 확인 |
