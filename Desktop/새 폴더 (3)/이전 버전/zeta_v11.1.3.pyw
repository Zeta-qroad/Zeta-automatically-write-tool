import tkinter as tk
import pyautogui
import pyperclip
import time
import json
import os
import keyboard
import re
import threading
import sys
import tkinter.messagebox as msgbox
pyautogui.PAUSE = 0.015



LOG_FILE = "log.txt"

# 기존 로그 파일 삭제 후 다시 생성
# if os.path.exists(LOG_FILE):
#         os.remove(LOG_FILE)

#   def write_log(message):
#         """ 로그 파일에 메시지를 기록 (밀리초 단위 포함) """
#         try:
#             timestamp = time.strftime("[%Y-%m-%d %H:%M:%S") + f".{int(time.time() * 100) % 100:02d}]"  # 0.01초 단위 포함
#             with open(LOG_FILE, "a", encoding="utf-8") as f:
#                 f.write(timestamp + " " + message + "\n")
#         except Exception as e:
#             with open("error_log.txt", "a", encoding="utf-8") as ef:
#                 ef.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 로그 작성 오류: {str(e)}\n")



def get_settings_filename():
    """실행 중인 프로그램의 이름을 기반으로 설정 파일명을 자동 생성"""
    
    # 실행 중인 파일명 (EXE로 실행될 수도 있으므로 sys.argv[0] 사용)
    program_filename = os.path.basename(sys.argv[0])  # 현재 실행 중인 파일 (예: zeta_v11.1.3.py)
    
    # 파일명에서 확장자 제거
    program_name, _ = os.path.splitext(program_filename)
    
    # 버전명(vX.X.X) 패턴 찾기 (예: zeta_v11.1.3)
    match = re.search(r"(v\d+\.\d+\.\d+)", program_name)
    
    if match:
        version = match.group(1)  # v11.1.3 같은 버전 문자열 추출
        base_name = program_name.replace(f"_{version}", "")  # 기존에 버전명이 포함되어 있으면 제거
        settings_filename = f"{base_name}_{version}_setting.json"  # ✅ 버전 포함하여 설정 파일명 생성
    else:
        settings_filename = f"{program_name}_setting.json"  # 버전이 없으면 기본값

    return settings_filename

settings_file = get_settings_filename()

# 설정을 파일로부터 불러오는 함수 및 초기값 설정
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            return json.load(f)
    else:
        return {
            "start_x": 1040,
            "start_y": 100,
            "pause": 0.015,
            "pausecccv": 0,
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

def check_clipboard_change_and_validate(expected_content, timeout=1.0, max_retries=3):
    """ 클립보드 내용이 기대한 값으로 변경될 때까지 최대 max_retries번 재시도 """

    for attempt in range(1, max_retries + 1):
        start_time = time.time()

        while time.time() - start_time < timeout:
            clipboard_value = pyperclip.paste()
            if clipboard_value == expected_content:
                return True  # 기대한 값이면 성공

            time.sleep(0.05)  # 50ms 대기 후 재확인

        # ✅ 마지막 재시도에서도 실패하면 경고 표시
        if attempt == max_retries:
            msgbox.showwarning("경고", "클립보드 변경 확인 실패.")

    return False  # 최대 재시도 횟수 초과 시 실패


def ensure_cell_moved():
    """ 셀 이동이 제대로 되었는지 확인하고, 한 줄씩 건너뛰는 문제 해결 """

    original_clipboard = pyperclip.paste().strip()  # 기존 클립보드 내용 저장

    for attempt in range(3):  # 최대 3번 반복
        keyboard.press_and_release('down')  # 아래 방향키 입력
        time.sleep(0.05)  # 이동 후 대기

        keyboard.press_and_release('ctrl+c')  # 현재 셀 내용 복사
        time.sleep(0.05)  # 복사 대기

        clipboard_content = pyperclip.paste().strip()  # 복사한 내용 가져오기

        # 이동한 셀이 비어있으면 정상적으로 이동한 것
        if clipboard_content == "":
            keyboard.press_and_release('esc')  # 점선 테두리 제거
            pyperclip.copy(original_clipboard)  # 클립보드 원래 내용으로 복구
            return  # 정상 이동 완료

    # 3번 시도 후에도 정상 이동이 안 되면 경고 메시지
    msgbox.showwarning("경고", "셀 이동이 정상적으로 이루어지지 않았습니다.")



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


def change_tap_cccv_and_back(expected_clipboard_content, timeout=0.5):
    time.sleep(0.01)  
    keyboard.press_and_release('ctrl+shift+tab')

    # 클립보드 변경 검증과 UI 감지를 동시에 수행
    clipboard_thread = threading.Thread(
        target=lambda: check_clipboard_change_and_validate(expected_clipboard_content, timeout),
        daemon=True
    )
    ui_thread = threading.Thread(target=wait_for_ui_to_load, args=(timeout,), daemon=True)

    clipboard_thread.start()
    ui_thread.start()

    clipboard_thread.join()
    ui_thread.join()
    
    time.sleep(0.05) 
    keyboard.press_and_release('ctrl+v')
    time.sleep(settings["pausecccv"])
    time.sleep(0.05)  

    ensure_cell_moved()
    
    pyautogui.hotkey('ctrl', 'tab')


# UI 변경 감지 (초기 색상 저장 후 비교)
def wait_for_ui_to_load(timeout=0.5):
    """ UI가 로딩될 때까지 대기 """
    start_time = time.time()
    target_x, target_y = settings["check_c"], 250
    initial_color = (26, 27, 27)  # 초기 색상

    while time.time() - start_time < timeout:
        current_color = pyautogui.pixel(target_x, target_y)
        if current_color != initial_color:
            
            return True  # UI 변경 감지됨

        time.sleep(0.025)  

    return False

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
    change_tap_cccv_and_back(modified_content) 
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
    change_tap_cccv_and_back(modified_content)
    pyautogui.moveTo(settings["fil_f"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button_img_search_block():  # 이미지 삭제 및 검색 차단
    settings["button2_clicks"] += 1
    current_position = pyautogui.position()
    drag_and_copy()
    clipboard_content = pyperclip.paste()
    modified_content = clipboard_content + "\t검색차단"
    pyperclip.copy(modified_content)
    change_tap_cccv_and_back(modified_content)
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
    change_tap_cccv_and_back(modified_content)
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
    change_tap_cccv_and_back(modified_content)
    pyautogui.moveTo(settings["hdell_d"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)


def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("설정")
    settings_window.geometry("300x830")
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
            msgbox.showerror("설정 저장 오류", "입력값 오류. 숫자만 입력하세요.")



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