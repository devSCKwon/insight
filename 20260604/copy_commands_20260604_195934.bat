@echo off
chcp 949 > nul
echo =========================================
echo  robocopy 파일 복사 작업을 시작합니다.
echo =========================================

echo [1] 'DL3_PE2_QTR_GLASS_MASTER_LIST_251222.xlsx' 복사 중...
robocopy "D:\99_Download\20260529" "E:\Aras_221225\Aras\Vault\SEJINPLM\1\A0\30B249F504FDCB776F2BF0B4BBF48" "DL3_PE2_QTR_GLASS_MASTER_LIST_251222.xlsx" /R:3 /W:3 /NP

echo =========================================
echo  모든 파일 복사 작업이 완료되었습니다.
echo =========================================
pause