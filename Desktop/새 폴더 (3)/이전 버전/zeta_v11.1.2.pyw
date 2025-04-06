import tkinter as tk
from tkinter import messagebox
import pyautogui
import pyperclip
import time
import json
import os
import re

pyautogui.PAUSE = 0.015

# 설정 파일 경로
settings_file = "zeta_v11.1.2_setting.json"

# 설정을 파일로부터 불러오는 함수
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    else:
        return {
            "start_x": 1000,
            "start_y": 100,
            "pause": 0.035,
            "check_c": 515, 
            "fil_f": 742, 
            "dell_d": 950, 
            "hdell_d": 1165, 
            "imgd_x" : 550, 
            "imgd_y" : 660, 
            "imgdc_x" : 840,
            "imgdc_y" : 605,
            "button1_clicks": 0,
            "button2_clicks": 0,
            "button3_clicks": 0,
            "button4_clicks": 0,
            "timeout": 2.0,  # 클립보드 변경 감지 timeout
            "poll_interval": 0.1  # 클립보드 변경 감지 poll_interval
        }

# 설정을 파일에 저장하는 함수
def save_settings():
    with open(settings_file, "w") as f:
        json.dump(settings, f)

# 전역 변수로 설정값 저장
settings = load_settings()

# 클립보드 변경 감지 함수
def wait_for_clipboard_change(max_wait=2.0, initial_poll=0.05, max_poll=0.3):
    """
    클립보드가 expected_text로 변경될 때까지 기다립니다.
    :param expected_text: 기대하는 클립보드 텍스트
    :return: True (변경 감지) / False (시간 초과)
    """
    start_time = time.time()
    poll_interval = initial_poll

    # 정규식: 이름 (한글/영문) + 줄바꿈 + @아이디 (영문/숫자/특수문자 포함)
    pattern = re.compile(r"^[\w가-힣, ]+\n@[\w.-]+$", re.MULTILINE)

    while time.time() - start_time < max_wait:
        current_text = pyperclip.paste().strip()

        # 정규식 패턴과 일치하면 성공
        if pattern.search(current_text):
            return True

        # 폴링 간격 증가
        time.sleep(poll_interval)
        poll_interval = min(poll_interval * 1.5, max_poll)

    return False

# 클립보드 변경 속도 측정 함수
def measure_clipboard_change_speed():
    """
    클립보드 변경 속도를 측정하여 timeout과 poll_interval을 계산합니다.
    :return: (timeout, poll_interval)
    """
    test_text = "테스트 데이터"
    start_time = time.time()
    pyperclip.copy("")
    pyperclip.copy(test_text)
    while pyperclip.paste().strip() != test_text:
        time.sleep(0.01)
    elapsed_time = time.time() - start_time

    # 측정된 시간을 기반으로 파라미터 계산
    timeout = max(2.0, elapsed_time * 2)  # 안전하게 2배로 설정
    poll_interval = max(0.05, elapsed_time / 10)  # 빠른 시스템을 위해 최소값 설정
    return timeout, poll_interval

# 동적 간격을 적용한 common_actions 함수
def common_actions():
    # 작업 수행
    pyautogui.hotkey('ctrl', 'shift', 'tab')
    pyautogui.press('enter')

    if wait_for_clipboard_change(invalid_words):
        print("⚠ 경고: 클립보드 변경 감지 실패!")
        return


    pyautogui.hotkey('ctrl', 'v')
    invalid_words = ["이미지 삭제", "검색차단", "삭제", "차단삭제"]
    new_clipboard_after_paste = pyperclip.paste().strip()
    if new_clipboard_after_paste in invalid_words:
        print(f"⚠ 경고: 붙여넣기 후 잘못된 데이터 감지! (현재: {new_clipboard_after_paste})")
        return  # 중단

def drag_and_copy():
    pyautogui.moveTo(settings["start_x"], settings["start_y"])
    pyautogui.click()

def img_dell_action(): 
    pyautogui.moveTo(settings["imgd_x"], settings["imgd_y"])
    pyautogui.click()
    pyautogui.moveTo(settings["imgdc_x"] , settings["imgdc_y"])
    pyautogui.click()
    time.sleep(0.3)
    pyautogui.moveTo(settings["imgdc_x"], settings["imgdc_y"] )
    pyautogui.click()

def on_button1_click():
    settings["button1_clicks"] += 1
    current_position = pyautogui.position()
    pyautogui.moveTo(settings["check_c"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button_img_check():
    settings["button1_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    common_actions()
    pyperclip.copy("이미지 삭제")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'tab')
    img_dell_action()
    time.sleep(0.7)
    pyautogui.moveTo(settings["check_c"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button2_click():
    settings["button2_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    common_actions()
    pyperclip.copy("검색차단")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'tab')
    pyautogui.moveTo(settings["fil_f"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button_img_search_block():
    settings["button2_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    common_actions()
    pyperclip.copy("검색차단")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'tab')
    img_dell_action()
    time.sleep(1)
    pyautogui.moveTo(settings["fil_f"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button3_click():
    settings["button3_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    common_actions()
    pyperclip.copy("삭제")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'tab')
    pyautogui.moveTo(settings["dell_d"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button4_click():
    settings["button4_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    common_actions()
    pyperclip.copy("차단삭제")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'tab')
    pyautogui.moveTo(settings["hdell_d"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("설정")
    settings_window.geometry("300x840")
    settings_window.configure(bg="#2c3e50")

    # 설정 항목 및 입력 필드 생성
    settings_fields = [
        ("제타복사 x좌표", "start_x"),
        ("제타복사 y좌표", "start_y"),
        ("입력 딜레이 ms", "pause"),
        ("확인 x좌표", "check_c"),
        ("검색차단 x좌표", "fil_f"),
        ("삭제 x좌표", "dell_d"),
        ("차단삭제 x좌표", "hdell_d"),
        ("쓰레기통 x좌표", "imgd_x"),
        ("쓰레기통 y좌표", "imgd_y"),
        ("이미지 삭제 확인 x 좌표", "imgdc_x"),
        ("이미지 삭제 확인 y 좌표", "imgdc_y"),
    ]

    entries = {}
    for label_text, key in settings_fields:
        tk.Label(settings_window, text=label_text, bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
        entry = tk.Entry(settings_window, font=("Helvetica", 10))
        entry.pack(pady=3)
        entry.insert(0, settings[key])
        entries[key] = entry

    # 총 버튼 클릭 횟수 표시
    total_clicks = sum(settings[f"button{i}_clicks"] for i in range(1, 5))
    total_clicks_label = tk.Label(settings_window, text=f"총 버튼 클릭 횟수: {total_clicks}", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10))
    total_clicks_label.pack(pady=3)

    # 최적화 버튼 추가
    def optimize_clipboard_speed():
        timeout, poll_interval = measure_clipboard_change_speed()
        settings["timeout"] = timeout
        settings["poll_interval"] = poll_interval
        messagebox.showinfo("최적화 완료", f"클립보드 변경 속도 측정 완료!\nTimeout: {timeout:.2f}s, Poll Interval: {poll_interval:.2f}s")


    # 저장 및 초기화 버튼
    tk.Button(settings_window, text="저장", command=lambda: save_settings_window(entries), **button_style1).pack(pady=9)
    tk.Button(settings_window, text="초기화", command=lambda: reset_clicks(total_clicks_label), **button_style1).pack(pady=9)
    tk.Button(settings_window, text="최적화", command=optimize_clipboard_speed, **button_style1).pack(pady=9)

    def reset_clicks(label):
        settings["button1_clicks"] = 0
        settings["button2_clicks"] = 0
        settings["button3_clicks"] = 0
        settings["button4_clicks"] = 0
        label.config(text="총 버튼 클릭 횟수: 0")

    def save_settings_window(entries):
        try:
            for key, entry in entries.items():
                if key == "pause":
                    settings[key] = float(entry.get())
                else:
                    settings[key] = int(entry.get())
            pyautogui.PAUSE = settings["pause"]
            save_settings()
            settings_window.destroy()
        except ValueError as e:
            messagebox.showerror("오류", f"잘못된 입력값: {e}")
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류 발생: {e}")

# 메인 윈도우 생성
root = tk.Tk()
root.title("제타 빠른 입력 매크로")
root.geometry("300x330")
root.attributes("-topmost", True)
root.configure(bg="#2c3e50")

# 버튼 스타일
button_style1 = {
    "width": 26,
    "height": 2,
    "bg": "#3498db",
    "fg": "#ecf0f1",
    "font": ("Helvetica", 12, "bold"),
    "activebackground": "#2980b9",
    "activeforeground": "#ecf0f1"
}
button_style2 = {
    "width": 12,
    "height": 2,
    "bg": "#3498db",
    "fg": "#ecf0f1",
    "font": ("Helvetica", 12, "bold"),
    "activebackground": "#2980b9",
    "activeforeground": "#ecf0f1"
}

# 버튼 생성 및 배치
# 1줄
frame1 = tk.Frame(root, bg="#2c3e50")
frame1.pack(pady=5)
button1 = tk.Button(frame1, text="확인", command=on_button1_click, **button_style2)
button1.pack(side="left", padx=5)
button_img_check = tk.Button(frame1, text="실사 확인", command=on_button_img_check, **button_style2)
button_img_check.pack(side="left", padx=5)

# 2줄
frame2 = tk.Frame(root, bg="#2c3e50")
frame2.pack(pady=5)
button2 = tk.Button(frame2, text="검색 차단", command=on_button2_click, **button_style2)
button2.pack(side="left", padx=5)
button_img_search_block = tk.Button(frame2, text="실사 검차", command=on_button_img_search_block, **button_style2)
button_img_search_block.pack(side="left", padx=5)

# 버튼 3 (삭제)
button3 = tk.Button(root, text="삭제",command=on_button3_click, **button_style1)
button3.pack(pady=10)

# 버튼 4 (삭제 및 차단)
button4 = tk.Button(root, text="삭제 및 차단",command=on_button4_click, **button_style1)
button4.pack(pady=10)

# 설정 버튼 생성 및 배치 
settings_button = tk.Button(root, text="⚙", command=open_settings, width=2, height=1, bg="#3498db", fg="#ecf0f1", font=("Helvetica", 12, "bold"), activebackground="#2980b9", activeforeground="#ecf0f1")
settings_button.pack(pady=10)

# 설정 버튼 생성 및 배치
settings_button = tk.Button(root, text="⚙", command=open_settings, width=2, height=1, bg="#3498db", fg="#ecf0f1", font=("Helvetica", 12, "bold"), activebackground="#2980b9", activeforeground="#ecf0f1")
settings_button.pack(pady=10)

# 프로그램 종료 시 설정 저장
def on_close():
    save_settings()
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# 메인 이벤트 루프 시작
root.mainloop()