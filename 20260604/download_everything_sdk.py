import os
import urllib.request
import zipfile
import io

def main():
    sdk_url = "https://www.voidtools.com/Everything-SDK.zip"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dll = os.path.join(script_dir, "Everything64.dll")
    
    print("=" * 60)
    print(" Everything SDK DLL 다운로드 작업을 시작합니다. (저장 경로 명시)")
    print("=" * 60)
    print(f"[*] 다운로드 URL: {sdk_url}")
    print(f"[*] 저장 위치: {dest_dll}")
    
    try:
        # 1. SDK Zip 파일 다운로드 (메모리에 받기)
        req = urllib.request.Request(
            sdk_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            zip_data = response.read()
        print("[*] 다운로드 완료. 압축을 해제합니다...")
        
        # 2. Zip 파일에서 Everything64.dll 추출
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            dll_filename = None
            for name in z.namelist():
                if "Everything64.dll" in name:
                    dll_filename = name
                    break
            
            if not dll_filename:
                print("[오류] zip 파일 내에서 Everything64.dll을 찾을 수 없습니다.")
                return
            
            print(f"[*] SDK 내 DLL 경로: {dll_filename}")
            
            # 지정된 경로에 추출
            with open(dest_dll, "wb") as f:
                f.write(z.read(dll_filename))
        
        if os.path.exists(dest_dll):
            print(f"[+] 성공적으로 {dest_dll} 파일을 생성하였습니다. (크기: {os.path.getsize(dest_dll)} 바이트)")
        else:
            print("[오류] 파일이 정상적으로 저장되지 않았습니다.")
            
    except Exception as e:
        print(f"[오류] Everything SDK 다운로드 중 에러 발생: {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()
