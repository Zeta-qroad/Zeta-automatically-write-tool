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

# 설정 파일 경로
settings_file = "settings.json"
LOG_FILE = "Debug log.txt"

def write_log(message):
    if DEBUG:  # 전역 DEBUG 값에 따라 로그 작성
        try:
            timestamp = time.strftime("[%Y-%m-%d %H:%M:%S") + f".{int(time.time() * 100) % 100:02d}]"
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(timestamp + " " + message + "\n")
        except Exception as e:
            with open("error_log.txt", "a", encoding="utf-8") as ef:
                ef.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 로그 작성 오류: {str(e)}\n")



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

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
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
            "button4_clicks": 0,
            "debug": False
        }
    
            
# 설정을 파일에 저장하는 함수
def save_settings():
    with open(settings_file, "w") as f:
        json.dump(settings, f)

# 전역 변수로 설정값 저장
settings = load_settings()
DEBUG = settings.get("debug", False)

def show_warning_async(message):
    root = tk.Tk()
    root.withdraw()  # Tkinter 창 숨김
    root.after(10, lambda: msgbox.showwarning("경고", message))

def validate_clipboard(content):
    pattern = r"^@\S+\t\S+\t(삭제|검색차단|차단삭제|이미지 삭제)$"
    return bool(re.match(pattern, content))

def check_clipboard_change_and_validate(expected_content, timeout=1.0, interval=0.2):
    """클립보드 내용이 기대한 값으로 변경될 때까지 최대 timeout초 동안 interval 간격으로 검사"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        clipboard_value = pyperclip.paste()
        if clipboard_value == expected_content:
            return True  # 기대한 값이면 성공
        
        time.sleep(interval)  # 200ms 대기 후 재확인
    
    msgbox.showwarning("경고", "클립보드 변경 1차 검증 실패.")
    return False  # 타임아웃 초과 시 실패

def ensure_cell_moved(): # 셀 이동 감지

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
            return True  # 정상 이동 완료

    msgbox.showwarning("경고", "셀 이동 감지 실패")
    return False  # 실패 시 False 반환

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

def change_tap_cccv_and_back(expected_clipboard_content, timeout=3.0):
    write_log(f"탭 전환 시작: 기대값={expected_clipboard_content!r}")
    keyboard.press_and_release('ctrl+shift+tab')

    # UI 감지
    ui_success_result = wait_for_ui_to_load(timeout=5.0, interval=0.05)
    if not ui_success_result:
        write_log("❌ [ERROR] 탭 전환 감지 실패")
        show_warning_async("탭 전환 감지 실패")
        return False

    keyboard.press_and_release('ctrl+v')
    time.sleep(settings["pausecccv"])
    time.sleep(0.05)

    ensure_cell_moved()

    pyautogui.hotkey('ctrl', 'tab')
    return True

def wait_for_ui_to_load(timeout=3.0, interval=0.05):
    start_time = time.time()
    target_x, target_y = settings["check_c"], 250
    initial_color = (26, 27, 27)  # 초기 색상 (제타 배경색)

    write_log(f"🔍 [UI 감지 시작] 초기 색상: {initial_color} (x={target_x}, y={target_y})")

    detected = False  # 감지 여부

    while time.time() - start_time < timeout:
        current_color = pyautogui.pixel(target_x, target_y)
        write_log(f"🔍 [UI 감지] 현재 색상: {current_color} (x={target_x}, y={target_y})")

        if current_color != initial_color:
            detected = True  # 감지 성공
            break  # 즉시 루프 종료

        time.sleep(interval)  # 0.05초 대기 후 재확인

    if detected:
        write_log("✅ [UI 감지 성공] 색상 변화 감지됨 → UI 전환 완료")
        return True
    else:
        write_log("❌ [UI 감지 실패] 시간 초과 → UI 감지 실패")
        return False


def perform_action(action_text, final_x, img_action=False, max_retries=2, retry_delay=0.2):
    current_position = pyautogui.position()

    for attempt in range(max_retries + 1):  # 최대 재시도 횟수 + 1
        # 드래그 및 복사 수행
        drag_and_copy()
        
        # 초기 클립보드 값 가져오기
        clipboard_content = pyperclip.paste()
        write_log(f"시도 {attempt + 1}: 초기 클립보드 = {clipboard_content!r}")

        # 클립보드 값이 @아이디\t이름 형식인지 확인
        if not re.match(r"^@.+\t[\S ]+$", clipboard_content):
            write_log(f"❌ 클립보드 내용이 예상 형식(@아이디\\t이름)과 일치하지 않음: {clipboard_content!r}")
            if attempt < max_retries:
                write_log(f"재시도 준비 (시도 {attempt + 1}/{max_retries + 1}), {retry_delay}초 대기")
                time.sleep(retry_delay)
                continue  # 다음 시도로 넘어감
            else:
                write_log(f"❌ 최대 재시도 초과: 클립보드 내용이 예상 형식과 일치하지 않음")
                return  # 최대 횟수 초과 시 종료
        
        # 형식이 맞으면 클립보드 수정 및 검증
        modified_content = clipboard_content + f"\t{action_text}"
        pyperclip.copy(modified_content)
        
        # 변경된 클립보드 확인
        try:
            actual_content = pyperclip.paste()
            write_log(f"시도 {attempt + 1}: 변경 후 클립보드 = {actual_content!r}, 기대값 = {modified_content!r}")
            
            if actual_content == modified_content:
                write_log(f"✅ 클립보드 변경 성공: {modified_content!r}")
                break
            elif attempt < max_retries:
                write_log(f"❌ 클립보드 변경 실패 (시도 {attempt + 1}/{max_retries + 1}), {retry_delay}초 후 재시도")
                time.sleep(retry_delay)
            else:
                write_log(f"❌ 최대 재시도 초과: 클립보드 변경 실패")
                show_warning_async("클립보드 변경 감지 실패. 다시하세요 ㅋ.ㅋ")
                return
        except Exception as e:
            write_log(f"클립보드 읽기 오류: {str(e)}")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                show_warning_async("클립보드 읽기 실패.")
                return

    # write_log(f"추가 검증 시작: 기대값 = {modified_content!r}")
    # if not check_clipboard_change_and_validate(modified_content, timeout=3.0, interval=0.05):
    #     write_log("❌ 추가 클립보드 검증 실패")
    #     show_warning_async("추가 클립보드 검증 실패.")
    #     return

    if not change_tap_cccv_and_back(modified_content):
        return

    if img_action:
        img_dell_action()
        time.sleep(1)

    pyautogui.moveTo(final_x, 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

# 버튼 함수 단순화
def on_button1_click():
    settings["button1_clicks"] += 1
    current_position = pyautogui.position()
    pyautogui.moveTo(settings["check_c"], 301)
    pyautogui.click()
    pyautogui.moveTo(current_position)

def on_button_img_check(): #실사 확인
    settings["button1_clicks"] += 1
    perform_action("이미지 삭제", settings["check_c"], img_action=True)

def on_button2_click(): #검색차단
    settings["button2_clicks"] += 1
    perform_action("검색차단", settings["fil_f"])

def on_button_img_search_block(): #실사 검차
    settings["button2_clicks"] += 1
    perform_action("검색차단", settings["fil_f"], img_action=True)

def on_button3_click():# 삭제
    settings["button3_clicks"] += 1
    perform_action("삭제", settings["dell_d"])

def on_button4_click():#삭제 및 차단
    settings["button4_clicks"] += 1
    perform_action("차단삭제", settings["hdell_d"])


def open_settings():
    global DEBUG  # 전역 변수 수정용
    settings_window = tk.Toplevel()
    settings_window.title("설정")
    settings_window.geometry("330x600")
    settings_window.configure(bg="#1a1b1b")


    def create_entry(parent, label_text, var_name, row):
        """ 레이블과 입력 필드를 생성하는 함수 """
        tk.Label(parent, text=label_text, bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        entry = tk.Entry(parent, font=("Helvetica", 10))
        entry.grid(row=row, column=1, padx=5, pady=2)
        entry.insert(0, settings[var_name])
        return entry
    
        # 좌표 설정 프레임
    coord_frame = tk.LabelFrame(settings_window, text="좌표 설정", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 11, "bold"))
    coord_frame.pack(pady=10, padx=10, fill="both")

    coord_entries = {
        "제타복사 X": "start_x",
        "제타복사 Y": "start_y",
        "확인 X": "check_c",
        "검색차단 X": "fil_f",
        "삭제 X": "dell_d",
        "차단삭제 X": "hdell_d",
        "쓰레기통 X": "imgd_x",
        "쓰레기통 Y": "imgd_y",
        "이미지 삭제 확인 X": "imgdc_x",
        "이미지 삭제 확인 Y": "imgdc_y"
    }
    coord_input = {}
    for i, (label, var) in enumerate(coord_entries.items()):
        coord_input[var] = create_entry(coord_frame, label, var, i)

        # 딜레이 설정 프레임
    delay_frame = tk.LabelFrame(settings_window, text="딜레이 설정 (ms)", bg="#1a1b1b", fg="#ffffff", font=("Helvetica", 10, "bold"))
    delay_frame.pack(pady=10, padx=10, fill="both")

    def update_slider_from_entry(slider, entry):
        try:
            value = float(entry.get())
            slider.set(round(value, 3))  # 소수점 3자리까지 반영
        except ValueError:
            pass

    # 슬라이더 변경 시 입력값도 업데이트
    def update_entry_from_slider(entry, slider):
        entry.delete(0, tk.END)
        entry.insert(0, f"{slider.get():.3f}")  # 소수점 3자리 출력

    # 입력 딜레이 (슬라이더 + 입력 칸)
    input_delay_row = tk.Frame(delay_frame, bg="#1a1b1b")
    input_delay_row.pack(fill="x", padx=10, pady=2)

    tk.Label(input_delay_row, text="입력 딜레이", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(side="left")

    input_delay_entry = tk.Entry(input_delay_row, font=("Helvetica", 10), width=7)
    input_delay_entry.pack(side="right")
    input_delay_entry.insert(0, f"{settings['pause']:.3f}")

    input_delay_slider = tk.Scale(delay_frame, from_=0, to=1, resolution=0.001, orient="horizontal", length=250, bg="#1a1b1b", fg="#ecf0f1", highlightthickness=0)
    input_delay_slider.set(settings["pause"])
    input_delay_slider.pack(pady=2, fill="x", padx=10)

    # 이벤트 바인딩
    input_delay_slider.config(command=lambda val: update_entry_from_slider(input_delay_entry, input_delay_slider))
    input_delay_entry.bind("<Return>", lambda e: update_slider_from_entry(input_delay_slider, input_delay_entry))

    # 붙여넣기 딜레이 (슬라이더 + 입력 칸)
    paste_delay_row = tk.Frame(delay_frame, bg="#1a1b1b")
    paste_delay_row.pack(fill="x", padx=10, pady=2)

    tk.Label(paste_delay_row, text="붙여넣기 딜레이", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(side="left")

    paste_delay_entry = tk.Entry(paste_delay_row, font=("Helvetica", 10), width=7)
    paste_delay_entry.pack(side="right")
    paste_delay_entry.insert(0, f"{settings['pausecccv']:.3f}")

    paste_delay_slider = tk.Scale(delay_frame, from_=0, to=1, resolution=0.001, orient="horizontal", length=250, bg="#1a1b1b", fg="#ecf0f1", highlightthickness=0)
    paste_delay_slider.set(settings["pausecccv"])
    paste_delay_slider.pack(pady=2, fill="x", padx=10)



    # 이벤트 바인딩
    paste_delay_slider.config(command=lambda val: update_entry_from_slider(paste_delay_entry, paste_delay_slider))
    paste_delay_entry.bind("<Return>", lambda e: update_slider_from_entry(paste_delay_slider, paste_delay_entry))


    # 클릭 횟수 표시
    total_clicks = settings["button1_clicks"] + settings["button2_clicks"] + settings["button3_clicks"] + settings["button4_clicks"]
    total_clicks_label = tk.Label(settings_window, text=f"총 버튼 클릭 횟수: {total_clicks}", bg="#1c1c1c", fg="#ecf0f1", font=("Helvetica", 10))
    total_clicks_label.pack(pady=5)

    # 버튼 스타일
    local_button_style = {
        "width": 15,
        "height": 1,
        "bg": "#6728ff",
        "fg": "#ecf0f1",
        "font": ("Helvetica", 10, "bold"),
        "activebackground": "#5220cc",
        "activeforeground": "#1a1b1b"
    }

    # 설정 저장 함수 (입력값 검증 추가)
    def save_settings_window():
        try:
            for var in coord_entries.values():
                settings[var] = int(coord_input[var].get())

            settings["pause"] = float(input_delay_entry.get())
            settings["pausecccv"] = float(paste_delay_entry.get())

            pyautogui.PAUSE = settings["pause"]
            save_settings()
            settings_window.destroy()
        except ValueError:
            msgbox.showerror("설정 저장 오류", "입력값 오류. 숫자만 입력하세요.")



    # 버튼 프레임
    button_frame = tk.Frame(settings_window, bg="#1a1b1b")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="저장", command=save_settings_window, **local_button_style).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="초기화", command=lambda: reset_clicks(total_clicks_label), **local_button_style).grid(row=0, column=1, padx=5)
    
    footer_frame = tk.Frame(settings_window, bg="#1a1b1b")
    footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)

    # 디버그 모드 체크박스
    debug_var = tk.BooleanVar(value=DEBUG)  # 현재 DEBUG 상태로 초기화
    debug_check = tk.Checkbutton(
        footer_frame,
        text="디버그 모드",
        variable=debug_var,
        bg="#1a1b1b",
        fg="#ecf0f1",
        selectcolor="#6728ff",
        font=("Helvetica", 10)
    )
    debug_check.pack(side="left", padx=5)

    def save_settings_window():
        global DEBUG
        settings["debug"] = debug_var.get()  # 체크박스 상태를 settings에 저장
        DEBUG = settings["debug"]  # DEBUG 업데이트
        save_settings(settings)  # 설정 파일에 저장
        settings_window.destroy()
        write_log("설정 저장됨: 디버그 모드 = " + str(DEBUG))

    save_button = tk.Button(
        footer_frame,
        text="저장",
        command=save_settings_window,
        bg="#6728ff",
        fg="#ecf0f1",
        font=("Helvetica", 10)
    )
    save_button.pack(side="left", padx=5)

    # 제작자 정보
    creator_label = tk.Label(footer_frame, text="제작자: 근혁", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 9))
    creator_label.pack(side="right", padx=5)

    def reset_clicks(label):
        settings["button1_clicks"] = 0
        settings["button2_clicks"] = 0
        settings["button3_clicks"] = 0
        settings["button4_clicks"] = 0
        label.config(text="총 버튼 클릭 횟수: 0")





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