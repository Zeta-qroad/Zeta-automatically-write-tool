import tkinter as tk
import pyautogui
import pyperclip
import time
import json
import os
import keyboard
import re
import threading
pyautogui.PAUSE = 0.015

# 설정을 저장할 파일 경로
settings_file = "zeta_v11.0.7_setting.json"

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
            "pausecccv": 0.2,
            "check_c": 626, 
            "fil_f": 908, 
            "dell_d": 1190, 
            "hdell_d": 1468, 
            "imgd_x" : 647, 
            "imgd_y" : 659, 
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

def validate_clipboard(content):
    """ 클립보드 내용이 올바른 형식인지 검증하는 함수 """
    pattern = r"^@\S+\t\S+\t(삭제|검색차단|차단삭제|이미지 삭제)$"
    return bool(re.match(pattern, content))

def check_clipboard_change_and_validate(expected_content, timeout=1.0):
    """ 
    클립보드 변경 확인 & 형식 검증 (비동기 실행 가능)
    - 최대 timeout 초 동안 변경 확인
    - 형식 검증 실패 시 False 반환
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if pyperclip.paste() == expected_content:
            if validate_clipboard(expected_content):  # 형식까지 검증
                print("✅ 클립보드 변경 확인 완료! 형식도 정상!")
                return True
            else:
                print(f"❌ 클립보드 형식 오류! 현재 값: {pyperclip.paste()}")
                return False
        time.sleep(0.05)  # 50ms 간격으로 확인
    print("❌ 클립보드 변경 실패!")
    return False  # 시간 초과 시 False 반환


def verify_clipboard_change(expected_content, timeout=1.0):
    """
    클립보드가 예상한 값으로 변경되었는지 확인하는 함수
    - 최대 timeout 초 동안 반복 확인
    - 변경되면 True 반환, 실패하면 False 반환
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if pyperclip.paste() == expected_content:
            return True
        time.sleep(0.1)  # 100ms 대기
    return False  # 시간 초과 시 False 반환

def drag_and_copy():
    pyautogui.moveTo(settings["start_x"], settings["start_y"])
    pyautogui.click()

def img_dell_action(): 
    pyautogui.moveTo(settings["imgd_x"], settings["imgd_y"])
    pyautogui.click()
    pyautogui.moveTo(settings["imgdc_x"] , settings["imgdc_y"])
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.moveTo(settings["imgdc_x"], settings["imgdc_y"] )
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.moveTo(settings["imgdc_x"], settings["imgdc_y"] )
    pyautogui.click()

def wait_for_clipboard(expected_content, timeout=1.0):
    """클립보드가 expected_content로 변경될 때까지 대기 (최대 timeout 초)"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if pyperclip.paste() == expected_content:
            return True
        time.sleep(0.05)  # 50ms 간격으로 확인
    return False  # 시간 초과 시 False 반환


def change_tap_cccv_and_back(expected_clipboard_content, timeout=1.0):
    time.sleep(0.05)
    keyboard.press_and_release('ctrl+shift+tab')

    clipboard_thread = threading.Thread(target=check_clipboard_change_and_validate, args=(expected_clipboard_content, timeout)) # 병렬 실행 부분
    ui_thread = threading.Thread(target=wait_for_ui_to_load, args=(timeout,))

    clipboard_thread.start()
    ui_thread.start()

    # 두 개의 작업이 끝날 때까지 기다림
    clipboard_thread.join()
    ui_thread.join()

    # 최종 검증
    if not check_clipboard_change_and_validate(expected_clipboard_content, timeout):
        print("❌ 클립보드 검증 실패! 작업 중단")
        return
    if not wait_for_ui_to_load(timeout):
        print("⚠ UI 로딩 감지 실패! 기본 대기 적용")
        time.sleep(0.2)  # UI가 안 떴을 경우 추가 대기
    
    time.sleep(settings["pausecccv"])  # 키 입력 간격 추가
    keyboard.press_and_release('ctrl+v')
    time.sleep(0.1)
    keyboard.press_and_release('down')
    time.sleep(0.05)
    pyautogui.hotkey('ctrl', 'tab')


def wait_for_ui_to_load(timeout=1.0):
    """시트가 로딩될 때까지 대기 (최대 timeout 초)"""
    start_time = time.time()

    # ✅ 감지할 위치 (설정값 기반)
    target_x, target_y = settings["check_c"], 250  
    expected_color = (255, 255, 255)  # 기본 배경색 (필요에 따라 수정)

    while time.time() - start_time < timeout:
        if pyautogui.pixel(target_x, target_y) != expected_color:
            return True  # UI가 정상적으로 로딩됨
        time.sleep(0.05)

    return False  # 시간 초과 시 False 반환

def on_button1_click(): # 확인
    settings["button1_clicks"] += 1
    current_position = pyautogui.position()
    pyautogui.moveTo(settings["check_c"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button_img_check(): #이미지 삭제 및 확인
    settings["button1_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    clipboard_content = pyperclip.paste()
    modified_content = clipboard_content + "\t이미지 삭제"
    pyperclip.copy(modified_content)
    change_tap_cccv_and_back()
    img_dell_action()
    time.sleep(1)
    pyautogui.moveTo(settings["check_c"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button2_click(): # 검색차단
    settings["button2_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    clipboard_content = pyperclip.paste()
    modified_content = clipboard_content + "\t검색차단"
    pyperclip.copy(modified_content)
    change_tap_cccv_and_back()
    pyautogui.moveTo(settings["fil_f"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button_img_search_block():# 이미지 삭제 및 검색 차단
    settings["button2_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    clipboard_content = pyperclip.paste()
    modified_content = clipboard_content + "\t검색차단"
    pyperclip.copy(modified_content)
    change_tap_cccv_and_back()
    img_dell_action()
    time.sleep(1)
    pyautogui.moveTo(settings["fil_f"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button3_click():# 삭제
    settings["button3_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    clipboard_content = pyperclip.paste()
    modified_content = clipboard_content + "\t삭제"
    pyperclip.copy(modified_content)
    change_tap_cccv_and_back()
    pyautogui.moveTo(settings["dell_d"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)


def on_button4_click(): # 삭제 및 차단
    settings["button4_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    clipboard_content = pyperclip.paste()
    modified_content = clipboard_content + "\t차단삭제"
    pyperclip.copy(modified_content)
    change_tap_cccv_and_back()
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

    tk.Label(settings_window, text="붙여넣기 딜레이 ms", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(pady=4)
    pausecccv_entry = tk.Entry(settings_window, font=("Helvetica", 10))
    pausecccv_entry.pack(pady=3)
    pausecccv_entry.insert(0, settings["pausecccv"])

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

    tk.Button(settings_window, text="저장", command=lambda: save_settings_window(start_x_entry, start_y_entry, pause_entry, pausecccv_entry, check_c_entry, fil_f_entry, dell_d_entry, hdell_d_entry, imgd_x_entry, imgd_y_entry, imgdc_x_entry, imgdc_y_entry), **local_button_style).pack(pady=9)
    tk.Button(settings_window, text="초기화", command=lambda: reset_clicks(total_clicks_label), **local_button_style).pack(pady=9)

    def reset_clicks(label):
        settings["button1_clicks"] = 0
        settings["button2_clicks"] = 0
        settings["button3_clicks"] = 0
        settings["button4_clicks"] = 0
        label.config(text="총 버튼 클릭 횟수: 0")

    def save_settings_window(start_x_entry, start_y_entry, pause_entry, pausecccv_entry, check_c_entry, fil_f_entry, dell_d_entry, hdell_d_entry, imgd_x_entry, imgd_y_entry, imgdc_x_entry, imgdc_y_entry):
        try:
            settings["start_x"] = int(start_x_entry.get())
            settings["start_y"] = int(start_y_entry.get())
            settings["pause"] = float(pause_entry.get())
            pyautogui.PAUSE = settings["pause"]
            settings["pausecccv"] = float(pausecccv_entry.get())
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