# 네이버웍스 조직도 가이드 정적 페이지 배포 및 업데이트 매뉴얼 (Cmder 환경)

본 문서는 `20261015` 프로젝트의 HTML 및 관련 문서 변경 사항을 **Cmder 콘솔** 환경에서 Git 저장소(`dev` 브랜치)와 GitHub Pages 정적 웹사이트에 간편하게 반영(배포)하기 위한 명령어 사용 가이드입니다.

---

## 1. 정적 배포 구조 및 프로세스 개요

1. **원본 문서 수정**: [`20261015/Docs/naver_works_organization_duty_guide.html`](file:///d:/00_Source/devSCKwon/insight/20261015/Docs/naver_works_organization_duty_guide.html) 내용 수정.
2. **웹 배포용 파일 동기화**:
   - `Docs/` 내부 문서는 상대경로가 `../images/`이므로, 웹 호스팅 루트(`20261015/`)에 맞게 이미지 경로(`images/`)로 변환하여 [`20261015/index.html`](file:///d:/00_Source/devSCKwon/insight/20261015/index.html) 및 [`20261015/naver_works_organization_duty_guide.html`](file:///d:/00_Source/devSCKwon/insight/20261015/naver_works_organization_duty_guide.html)에 반영.
3. **Git 스테이징 및 커밋**: 수정된 파일들을 Git에 기록 (`git add` & `git commit`).
4. **원격 저장소 푸시 (`origin dev`)**: GitHub의 `dev` 브랜치로 푸시.
5. **GitHub Actions 자동 배포**: [`.github/workflows/static.yml`](file:///d:/00_Source/devSCKwon/insight/.github/workflows/static.yml) 워크플로우가 자동으로 실행되어 GitHub Pages에 최신 정적 사이트 게시.

---

## 2. 배포 원클릭 명령어 (Cmder / 터미널)

### ① 원클릭 동기화 및 배포 (추천)

`Docs/` 문서의 수정 사항을 웹 루트(`index.html` 및 `naver_works_organization_duty_guide.html`)에 이미지 경로와 함께 자동 동기화하고 즉시 GitHub에 푸시합니다:

```bash
python -c "c=open(r'20261015/Docs/naver_works_organization_duty_guide.html',encoding='utf-8').read().replace('../images/','images/');open(r'20261015/index.html','w',encoding='utf-8').write(c);open(r'20261015/naver_works_organization_duty_guide.html','w',encoding='utf-8').write(c)" && git add 20261015/ && git commit -m "docs: update 2026-10-15 naver works duty guide static pages" && git push origin dev
```

---

### ② 수동 동기화 후 배포

루트의 `naver_works_organization_duty_guide.html`을 수정한 경우:

```bash
# 1. index.html로 복사
cp 20261015/naver_works_organization_duty_guide.html 20261015/index.html

# 2. 20261015 디렉터리 스테이징 및 커밋 & 푸시
git add 20261015/ && git commit -m "docs: update 2026-10-15 naver works duty guide static pages" && git push origin dev
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
