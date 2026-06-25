@echo off
chcp 949 > nul
echo =========================================
echo  robocopy 파일 복사 작업을 시작합니다.
echo =========================================

echo [1] 'file3.txt' 복사 중...
robocopy "d:\00_Source\devSCKwon\insight\20260604\test_source_files" "d:\00_Source\devSCKwon\insight\20260604\test_real_storage\folderC\subfolder" "file3.txt" /R:3 /W:3 /NP

echo =========================================
echo  모든 파일 복사 작업이 완료되었습니다.
echo =========================================
pause