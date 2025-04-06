import tkinter as tk
from tkinter import messagebox
import pyautogui
import pyperclip
import time
import json
import os

pyautogui.PAUSE = 0.015

# 설정을 저장할 파일 경로
settings_file = "zeta_v11.1.1_setting.json"

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
            "button4_clicks": 0
        }

# 설정을 파일에 저장하는 함수
def save_settings():
    with open(settings_file, "w") as f:
        json.dump(settings, f)

# 전역 변수로 설정값 저장
settings = load_settings()

def drag_and_copy():
    pyautogui.moveTo(settings["start_x"], settings["start_y"])
    pyautogui.click()

    new_clipboard_before_paste = pyperclip.paste().strip()

    invalid_words = ["이미지 삭제", "검색차단", "삭제", "차단삭제"]
    if new_clipboard_before_paste in invalid_words:
        print(f"⚠ 복사 똑바로 안됨 다시 ㄱㄱ (현재: {new_clipboard_before_paste})")
        return

# 클립보드 변경 감지
def wait_for_clipboard_change(expected_text):
    """
    클립보드가 expected_text로 변경될 때까지 기다립니다.
    :param expected_text: 기대하는 클립보드 텍스트
    :return: True (변경 감지) / False (시간 초과)
    """
    start_time = time.time()
    while time.time() - start_time < settings["timeout"]:
        current_text = pyperclip.paste().strip()
        if current_text == expected_text:
            return True
        time.sleep(settings["poll_interval"])
    return False


# 클립보드 변경 속도 측정
def measure_clipboard_change_speed():
    """
    클립보드 변경 속도를 측정하여 timeout과 poll_interval을 계산합니다.
    :return: (timeout, poll_interval)
    """
    test_text = "테스트 데이터 테스트 데이터 @asd123"
    start_time = time.time()
    pyperclip.copy("")
    pyperclip.copy(test_text)
    while pyperclip.paste().strip() != test_text:
        time.sleep(0.01)
    elapsed_time = time.time() - start_time


    # 측정된 시간을 기반으로 파라미터 계산
    timeout = max(2.0, elapsed_time * 1.5)  #  1.5배로 설정
    poll_interval = max(0.05, elapsed_time / 10)  # 최소값 설정
    return timeout, poll_interval



def common_actions():
    pyautogui.hotkey('ctrl', 'shift', 'tab')
    pyautogui.press('enter')
    pyautogui.hotkey('ctrl', 'v') 
    time.sleep(0.3)
    pyautogui.press('tab', presses=2)
    pyautogui.press('enter')

def img_dell_action(): 
    pyautogui.moveTo(settings["imgd_x"], settings["imgd_y"])
    pyautogui.click()
    pyautogui.moveTo(settings["imgdc_x"] , settings["imgdc_y"])
    pyautogui.click()
    time.sleep(0.4)
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

# 이미지 삭제 및 검색 차단
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
    settings_window.geometry("300x790")
    settings_window.configure(bg="#2c3e50")

    tk.Label(settings_window, text="제타복사 x좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    start_x_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    start_x_entry.pack(pady=3)
    start_x_entry.insert(0, settings["start_x"])

    tk.Label(settings_window, text="제타복사 y좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    start_y_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    start_y_entry.pack(pady=3)
    start_y_entry.insert(0, settings["start_y"])

    tk.Label(settings_window, text="입력 딜레이", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    pause_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    pause_entry.pack(pady=3)
    pause_entry.insert(0, settings["pause"])

    tk.Label(settings_window, text="확인 x좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    check_c_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    check_c_entry.pack(pady=3)
    check_c_entry.insert(0, settings["check_c"])

    tk.Label(settings_window, text="검색차단 x좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    fil_f_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    fil_f_entry.pack(pady=3)
    fil_f_entry.insert(0, settings["fil_f"])
    
    tk.Label(settings_window, text="삭제 x좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    dell_d_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    dell_d_entry.pack(pady=3)
    dell_d_entry.insert(0, settings["dell_d"])

    tk.Label(settings_window, text="차단삭제 x좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    hdell_d_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    hdell_d_entry.pack(pady=3)
    hdell_d_entry.insert(0, settings["hdell_d"])

    tk.Label(settings_window, text="쓰레기통 x좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgd_x_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgd_x_entry.pack(pady=3)
    imgd_x_entry.insert(0, settings["imgd_x"])

    tk.Label(settings_window, text="쓰레기통 y좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgd_y_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgd_y_entry.pack(pady=3)
    imgd_y_entry.insert(0, settings["imgd_y"])

    tk.Label(settings_window, text="이미지 삭제 확인 x 좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgdc_x_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgdc_x_entry.pack(pady=3)
    imgdc_x_entry.insert(0, settings["imgdc_x"])

    tk.Label(settings_window, text="이미지 삭제 확인 y 좌표", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgdc_y_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgdc_y_entry.pack(pady=3)
    imgdc_y_entry.insert(0, settings["imgdc_y"])

    total_clicks = settings["button1_clicks"] + settings["button2_clicks"] + settings["button3_clicks"] + settings["button4_clicks"]
    total_clicks_label = tk.Label(settings_window, text=f"총 버튼 클릭 횟수: {total_clicks}", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 10))
    total_clicks_label.pack(pady=3) 

    local_button_style = {
        "width": 20,
        "height": 2,
        "bg": "#3498db",
        "fg": "#ecf0f1",
        "font": ("Helvetica", 12, "bold"),
        "activebackground": "#2980b9",
        "activeforeground": "#ecf0f1"
    }
    def optimize_clipboard_speed():
        timeout, poll_interval = measure_clipboard_change_speed()
        settings["timeout"] = timeout
        settings["poll_interval"] = poll_interval
        messagebox.showinfo("최적화 완료", f"클립보드 변경 속도 측정 완료!\nTimeout: {timeout:.2f}s, Poll Interval: {poll_interval:.2f}s")
        
    tk.Button(settings_window, text="저장", command=lambda: save_settings_window(start_x_entry, start_y_entry, pause_entry, check_c_entry, fil_f_entry, dell_d_entry, hdell_d_entry, imgd_x_entry, imgd_y_entry, imgdc_x_entry, imgdc_y_entry), **local_button_style).pack(pady=9)
    tk.Button(settings_window, text="초기화", command=lambda: reset_clicks(total_clicks_label), **local_button_style).pack(pady=9)
    tk.Button(settings_window, text="최적화", command=lambda: optimize_clipboard_speed, **local_button_style).pack(pady=9)


    def reset_clicks(label):
        settings["button1_clicks"] = 0
        settings["button2_clicks"] = 0
        settings["button3_clicks"] = 0
        settings["button4_clicks"] = 0
        label.config(text="총 버튼 클릭 횟수: 0")

    def save_settings_window(start_x_entry, start_y_entry, pause_entry, check_c_entry, fil_f_entry, dell_d_entry, hdell_d_entry, imgd_x_entry, imgd_y_entry, imgdc_x_entry, imgdc_y_entry):
        try:
            settings["start_x"] = int(start_x_entry.get())
            settings["start_y"] = int(start_y_entry.get())
            settings["pause"] = float(pause_entry.get())
            pyautogui.PAUSE = settings["pause"]
            settings["check_c"] = int(check_c_entry.get())
            settings["fil_f"] = int(fil_f_entry.get())
            settings["dell_d"] = int(dell_d_entry.get())
            settings["hdell_d"] = int(hdell_d_entry.get())
            settings["imgd_x"] = int(imgd_x_entry.get())
            settings["imgd_y"] = int(imgd_y_entry.get())
            settings["imgdc_x"] = int(imgdc_x_entry.get())
            settings["imgdc_y"] = int(imgdc_y_entry.get())
            save_settings()
            settings_window.destroy()
        except ValueError as e:
            print(f"설정 저장 중 오류 발생: {e}")


# 메인 윈도우 생성
root = tk.Tk()
root.title("제타 빠른 입력 매크로")
root.geometry("300x330")  # 창 크기 설정
root.attributes("-topmost", True)  # 창을 항상 맨 위에 있게 설정
root.configure(bg="#2c3e50")  # 배경 색상 변경

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

# 프로그램 종료 시 설정 저장
def on_close():
    save_settings()  # 설정을 저장합니다.
    root.quit()   # Tkinter 루프를 중지합니다.
    root.destroy()   # 창을 종료합니다.

root.protocol("WM_DELETE_WINDOW", on_close)

# 메인 이벤트 루프 시작
root.mainloop()
