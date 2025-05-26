#!/usr/bin/env python3
import socket
import os

SERVER_ADDR = ('0.0.0.0', 3034)  # 모든 인터페이스에서 수신
BUF_SIZE = 1500  # 1500바이트씩
FILES_DIR = './shared_files'  # 전송 가능한 파일 경로

# 파일 로드하기
def load_files():
    # 파일 저장할 딕셔너리
    files = {}
    # FILES_DIR 디렉토리에 있는 파일 가져와 파일 이름 저장
    for fname in os.listdir(FILES_DIR):
        path = os.path.join(FILES_DIR, fname)
        # 딕셔너리로 파일이름에 대한 정보 저장
        if os.path.isfile(path):
            files[fname] = {
                'path': path,
                'size': os.path.getsize(path)
            }
    return files

def main():
    # IPV4 및 UDP로 소켓 열기
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 소켓 바인딩하여 모든 IP에서 수신 가능
    sock.bind(SERVER_ADDR)
    print(f"서버 실행 중... {SERVER_ADDR}")
    # 파일 로드
    files = load_files()

    while True:
        # 최대 2048바이트를 보내기 설정
        data, client = sock.recvfrom(2048)
        msg = data.decode('utf-8', errors='ignore').strip()
        print(f"[{client}] 요청: {msg}")
        # 정보 응답
        if msg.startswith('INFO '):
            # INFO 제거
            filename = msg[5:]
            # 파일이 없을 때 404 에러 보내기
            if filename not in files:
                sock.sendto(b'404 Not Found', client)
            else:
                # 있을 때 파일의 크기를 클라이언트에게 보내기
                size = str(files[filename]['size']).encode('utf-8')
                sock.sendto(size, client)
        # 다운로드 정보
        elif msg.startswith('DOWNLOAD '):
            # DOWNLOAD 제거
            filename = msg[9:]
            # 파일이 없을 때
            if filename not in files:
                continue

            # 파일 경로 가져오기
            path = files[filename]['path']
            # 파일 경로에 있는 파일에 대해서 BUF_SIZE만큼 계속 가져온뒤 보내기
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(BUF_SIZE)
                    if not chunk:
                        break
                    sock.sendto(chunk, client)
        else:
            print(f"알 수 없는 요청: {msg}")

if __name__ == '__main__':
    main()
