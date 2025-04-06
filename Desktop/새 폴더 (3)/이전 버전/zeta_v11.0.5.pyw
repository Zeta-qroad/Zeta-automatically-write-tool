import tkinter as tk
import pyautogui
import pyperclip
import time
import json
import os
import keyboard
pyautogui.PAUSE = 0.015

# 설정을 저장할 파일 경로
settings_file = "zeta_v11.0.5_setting.json"

# 설정을 파일로부터 불러오는 함수
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    else:
        return {
            "start_x": 1040,
            "start_y": 100,
            "pause": 0.015,
            "check_c": 626, 
            "fil_f": 908, 
            "dell_d": 1190, 
            "hdell_d": 1468, 
            "imgd_x" : 550, 
            "imgd_y" : 660, 
            "imgdc_x" : 1040,
            "imgdc_y" : 627,
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
    
def common_actions():
    keyboard.press_and_release('ctrl+shift+tab')
    time.sleep(0.1)  # 키 입력 간격 추가
    keyboard.press_and_release('ctrl+v')
    time.sleep(0.05)
    keyboard.press('left')
    time.sleep(0.05)
    keyboard.press('right')
    time.sleep(0.05)
    keyboard.press_and_release('tab')
    time.sleep(0.05)
    keyboard.press_and_release('tab')
    time.sleep(0.05)
    keyboard.press_and_release('enter')

def img_dell_action(): 
    pyautogui.moveTo(settings["imgd_x"], settings["imgd_y"])
    pyautogui.click()
    pyautogui.moveTo(settings["imgdc_x"] , settings["imgdc_y"])
    pyautogui.click()
    time.sleep(0.2)
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
    settings_window.configure(bg="#1a1b1b")

    tk.Label(settings_window, text="제타복사 x좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    start_x_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    start_x_entry.pack(pady=3)
    start_x_entry.insert(0, settings["start_x"])

    tk.Label(settings_window, text="제타복사 y좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    start_y_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    start_y_entry.pack(pady=3)
    start_y_entry.insert(0, settings["start_y"])

    tk.Label(settings_window, text="입력 딜레이 ms", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    pause_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    pause_entry.pack(pady=3)
    pause_entry.insert(0, settings["pause"])

    tk.Label(settings_window, text="확인 x좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    check_c_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    check_c_entry.pack(pady=3)
    check_c_entry.insert(0, settings["check_c"])

    tk.Label(settings_window, text="검색차단 x좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    fil_f_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    fil_f_entry.pack(pady=3)
    fil_f_entry.insert(0, settings["fil_f"])
    
    tk.Label(settings_window, text="삭제 x좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    dell_d_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    dell_d_entry.pack(pady=3)
    dell_d_entry.insert(0, settings["dell_d"])

    tk.Label(settings_window, text="차단삭제 x좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    hdell_d_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    hdell_d_entry.pack(pady=3)
    hdell_d_entry.insert(0, settings["hdell_d"])

    tk.Label(settings_window, text="쓰레기통 x좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgd_x_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgd_x_entry.pack(pady=3)
    imgd_x_entry.insert(0, settings["imgd_x"])

    tk.Label(settings_window, text="쓰레기통 y좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgd_y_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgd_y_entry.pack(pady=3)
    imgd_y_entry.insert(0, settings["imgd_y"])

    tk.Label(settings_window, text="이미지 삭제 확인 x 좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgdc_x_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgdc_x_entry.pack(pady=3)
    imgdc_x_entry.insert(0, settings["imgdc_x"])

    tk.Label(settings_window, text="이미지 삭제 확인 y 좌표", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    imgdc_y_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    imgdc_y_entry.pack(pady=3)
    imgdc_y_entry.insert(0, settings["imgdc_y"])

    total_clicks = settings["button1_clicks"] + settings["button2_clicks"] + settings["button3_clicks"] + settings["button4_clicks"]
    total_clicks_label = tk.Label(settings_window, text=f"총 버튼 클릭 횟수: {total_clicks}", bg="#1c1c1c", fg="#ecf0f1", font=("Helvetica", 10))
    total_clicks_label.pack(pady=3) 

    local_button_style = {
        "width": 20,
        "height": 2,
        "bg": "#6728ff",
        "fg": "#ecf0f1",
        "font": ("Helvetica", 12, "bold"),
        "activebackground": "#5220cc",
        "activeforeground": "#1a1b1b"
    }

    tk.Button(settings_window, text="저장", command=lambda: save_settings_window(start_x_entry, start_y_entry, pause_entry, check_c_entry, fil_f_entry, dell_d_entry, hdell_d_entry, imgd_x_entry, imgd_y_entry, imgdc_x_entry, imgdc_y_entry), **local_button_style).pack(pady=9)
    tk.Button(settings_window, text="초기화", command=lambda: reset_clicks(total_clicks_label), **local_button_style).pack(pady=9)

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
root.configure(bg="#1a1b1b")  # 배경 색상 변경

button_style1 = {
    "width": 26,
    "height": 2,
    "bg": "#6728ff",  # 미드 그레이 (너무 어둡지 않고 적당한 톤)
    "fg": "#ecf0f1",  # 연한 그레이 (화이트보다 부드러움)
    "font": ("Helvetica", 12, "bold"),
    "activebackground": "#e74c3c",  # 클릭 시 밝은 그레이
    "activeforeground": "#ffffff"   # 클릭 시 화이트 텍스트
}

button_style2 = {
    "width": 12,
    "height": 2,
    "bg": "#6728ff",  # 동일한 미드 그레이 적용
    "fg": "#ecf0f1",
    "font": ("Helvetica", 12, "bold"),
    "activebackground": "#e74c3c",
    "activeforeground": "#ffffff"
}

# 1줄
frame1 = tk.Frame(root, bg="#1a1b1b")
frame1.pack(pady=5)
button1 = tk.Button(frame1, text="확인", command=on_button1_click, **button_style2)
button1.pack(side="left", padx=5)
button_img_check = tk.Button(frame1, text="실사 확인", command=on_button_img_check, **button_style2)
button_img_check.pack(side="left", padx=5)

# 2줄
frame2 = tk.Frame(root, bg="#1a1b1b")
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
settings_button = tk.Button(root, text="⚙", command=open_settings, width=2, height=1, bg="#6728ff", fg="#ecf0f1", font=("Helvetica", 12, "bold"), activebackground="#e74c3c", activeforeground="#ecf0f1")
settings_button.pack(pady=10)

# 프로그램 종료 시 설정 저장
def on_close():
    save_settings()  # 설정을 저장합니다.
    root.quit()   # Tkinter 루프를 중지합니다.
    root.destroy()   # 창을 종료합니다.

root.protocol("WM_DELETE_WINDOW", on_close)

# 메인 이벤트 루프 시작
root.mainloop()
