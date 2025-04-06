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
from tkinter import ttk
import tkinter.messagebox as msgbox

pyautogui.PAUSE = 0.015

# 설정 파일 경로
settings_file = "settings.json"
LOG_FILE = "Debug log.txt"
MAX_LOG_SIZE = 10 * 1024 * 1024

# 전역 디버그 플래그
DEBUG_ENABLED = False

def load_debug_flag():
    global DEBUG_ENABLED
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                DEBUG_ENABLED = settings.get('debug', False)
                return DEBUG_ENABLED
        else:
            DEBUG_ENABLED = False
            return False
    except Exception as e:
        print(f"설정 파일 로드 오류: {str(e)}")
        DEBUG_ENABLED = False
        return False

DEBUG_ENABLED = load_debug_flag()

def manage_log_file():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        os.rename(LOG_FILE, f"log_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        write_log("로그 파일 크기 초과, 새 파일 생성")

def write_log(message):
    message = message.strip().replace('\r', '').replace('\n', '')
    if not DEBUG_ENABLED:
        return

    manage_log_file()
    try:
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S") + f".{int(time.time() * 100) % 100:02d}]"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(timestamp + " " + message + "\n")
    except Exception as e:
        with open("error_log.txt", "a", encoding="utf-8") as ef:
            ef.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 로그 작성 오류: {str(e)}\n")

def get_settings_filename():
    program_filename = os.path.basename(sys.argv[0])
    program_name, _ = os.path.splitext(program_filename)
    match = re.search(r"(v\d+\.\d+\.\d+)", program_name)
    if match:
        version = match.group(1)
        base_name = program_name.replace(f"_{version}", "")
        settings_filename = f"{base_name}_{version}_setting.json"
    else:
        settings_filename = f"{program_name}_setting.json"
    return settings_filename

settings_file = get_settings_filename()

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "start_x": 1040, "start_y": 100, "pause": 0.015, "pausecccv": 0,
        "check_c": 626, "fil_f": 908, "dell_d": 1190, "hdell_d": 1468,
        "imgd_x": 647, "imgd_y": 659, "imgdc_x": 1040, "imgdc_y": 627,
        "button1_clicks": 0, "button2_clicks": 0, "button3_clicks": 0, "button4_clicks": 0, #1번 탭
        "ok_x": 550, "block_x": 790, "del_x": 1030, "block_del_x": 1270, "img_block_x": 1510, #2번 탭
        "debug": False
    }

def save_settings(settings_dict):
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_dict, f, ensure_ascii=False, indent=4)

settings = load_settings()

def show_warning_async(message):
    root = tk.Tk()
    root.withdraw()
    root.after(10, lambda: msgbox.showwarning("경고", message))

def ensure_cell_moved():
    original_clipboard = pyperclip.paste().strip()
    for attempt in range(3):
        keyboard.press_and_release('down')
        keyboard.press_and_release('ctrl+c')
        time.sleep(0.05)
        clipboard_content = pyperclip.paste().strip()
        if clipboard_content == "":
            keyboard.press_and_release('esc')
            pyperclip.copy(original_clipboard)
            return True
    msgbox.showwarning("경고", "셀 이동 감지 실패")
    return False

def drag_and_copy():
    pyautogui.click(settings["start_x"], settings["start_y"])

def img_dell_action():
    # 첫 번째 클릭: 쓰레기통 클릭
    pyautogui.click(settings["imgd_x"], settings["imgd_y"])
    # 두 번째 클릭: 이미지 삭제 확인
    pyautogui.click(settings["imgdc_x"], settings["imgdc_y"])
    time.sleep(0.2)
    # 세 번째 클릭: 이미지 삭제 확인 (한 번 더)
    pyautogui.click(settings["imgdc_x"], settings["imgdc_y"])

    # 색상 감지 좌표
    target_x, target_y = settings["check_c"], 250
    original_color = (26, 27, 27)  # 원래 색상
    timeout = 2.0  # 최대 대기 시간 1초
    interval = 0.05  # 색상 체크 간격 (초)

    # 색상이 (26, 27, 27)이 아닌 동안 대기 (조작 불가 상태)
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_color = pyautogui.pixel(target_x, target_y)
        write_log(f"[색상 감지] 현재 색상: {current_color} (x={target_x}, y={target_y})")
        if current_color != original_color:
            write_log("이미지 삭제 안내 발송... 색상이 (26, 27, 27)이 아님, 대기 중")
            time.sleep(interval)
            continue
        write_log("[색상 복귀 성공] (26, 27, 27) 감지됨")
        break
    else:
        write_log("[색상 복귀 실패] (26, 27, 27) 복귀 실패, 타임아웃 후 진행")


def wait_for_ui_to_load(timeout=1.0, interval=0.05):
    start_time = time.time()
    target_x, target_y = settings["check_c"], 300
    expected_color = (67, 67, 67)  # 감지할 색상
    write_log(f"[UI 감지 시작] 기대 색상: {expected_color} (x={target_x}, y={target_y})")
    detected = False
    while time.time() - start_time < timeout:
        current_color = pyautogui.pixel(target_x, target_y)
        write_log(f"[UI 감지] 현재 색상: {current_color} (x={target_x}, y={target_y})")
        if current_color == expected_color:
            detected = True
            break
        time.sleep(interval)
    if detected:
        write_log("[UI 감지 성공] (67, 67, 67) 감지됨 → UI 전환 완료")
        return True
    else:
        write_log("[UI 감지 실패] (67, 67, 67) 감지 실패 → UI 감지 실패")
        return False

def change_tap_cccv_and_back(expected_clipboard_content, timeout=2.0, retry_delay=0.25):
    write_log(f"탭 전환 시작: 기대값={expected_clipboard_content!r}")
    time.sleep(0.05)
    start_time = time.time()
    pyautogui.hotkey('ctrl', 'shift', 'tab')
    attempt = 1
    while attempt <= 2:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            write_log(f"ERROR: 탭 전환 감지 실패 (타임아웃 {timeout}초 초과)")
            show_warning_async("탭 전환 감지 실패")
            return False
        ui_success_result = wait_for_ui_to_load(timeout=retry_delay, interval=0.05)
        if ui_success_result:
            write_log("탭 전환 감지 성공")
            break
        else:
            write_log(f"{attempt}번째 탭 전환 감지 실패, 재시도 중...")
            # if attempt == 1:
            #     pyautogui.hotkey('ctrl', 'shift', 'tab')
            attempt += 1
    if attempt > 2:
        write_log("ERROR: 두 번째 탭 전환 감지 실패 (최대 재시도 초과)")
        show_warning_async("탭 전환 감지 실패")
        return False

    start_time = time.time()
    attempt = 1
    while True:
        if time.time() - start_time >= timeout:
            write_log(f"타임아웃 {timeout}초 경과: 붙여넣기 실패")
            show_warning_async("붙여넣기 실패")
            return False

        current_clipboard = pyperclip.paste()
        if current_clipboard != expected_clipboard_content:
            write_log(f"클립보드 불일치: 현재={current_clipboard!r}, 기대값={expected_clipboard_content!r}")
            pyperclip.copy(expected_clipboard_content)
        write_log(f"{attempt}번째 붙여넣기 시도")
        pyautogui.hotkey('ctrl', 'v')
        pyperclip.copy("")
        time.sleep(0.025)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.025)
        clipboard_content = pyperclip.paste()
        write_log(f"붙여넣기 결과: {clipboard_content!r}, 기대값: {expected_clipboard_content!r}")

        # 패턴 및 내용 검증
        expected_pattern = r"^@\S+[ \t]*(.+)[ \t]*(삭제|검색차단|차단삭제|이미지 삭제)$"
        if not re.match(expected_pattern, clipboard_content):
            write_log(f"붙여넣기 값과 기댓값 불일치 현재: {clipboard_content!r}")
            write_log(f"재시도 준비 (시도 {attempt}), {retry_delay}초 대기")
            time.sleep(retry_delay)
            attempt += 1
            continue
        if clipboard_content != expected_clipboard_content:
            write_log(f"붙여넣기 실패: 입력 값 불일치 (현재={clipboard_content!r}, 기대값={expected_clipboard_content!r})")
            write_log(f"재시도 준비 (시도 {attempt}), {retry_delay}초 대기")
            time.sleep(retry_delay)
            attempt += 1
            continue
        write_log("붙여넣기 성공: 입력 값 확인됨")
        break

    if not ensure_cell_moved():
        write_log("셀 이동 실패")
        return False
    pyautogui.hotkey('ctrl', 'tab')
    write_log("탭 전환 완료")
    return True

def perform_action(action_text, final_x, img_action=False, max_retries=2, retry_delay=0.05):
    current_position = pyautogui.position()
    for attempt in range(max_retries + 1):
        drag_and_copy()
        clipboard_content = pyperclip.paste()
        write_log(f"시도 {attempt + 1}: 초기 클립보드 = {clipboard_content!r}")
        if not re.match(r"^@.+\t[\S ]+$", clipboard_content):
            write_log(f"클립보드 내용이 예상 형식(@아이디\\t이름)과 일치하지 않음: {clipboard_content!r}")
            if attempt < max_retries:
                write_log(f"재시도 준비 (시도 {attempt + 1}/{max_retries + 1}), {retry_delay}초 대기")
                time.sleep(retry_delay)
                continue
            else:
                write_log(f"최대 재시도 초과: 클립보드 내용이 예상 형식과 일치하지 않음")
                return
        modified_content = clipboard_content + f"\t{action_text}"
        pyperclip.copy(modified_content)
        try:
            actual_content = pyperclip.paste().strip().replace('\r', '').replace('\n', '')
            modified_content = modified_content.strip().replace('\r', '').replace('\n', '')
            write_log(f"시도 {attempt + 1}: 변경 후 클립보드 = {actual_content!r}, 기대값 = {modified_content!r}")
            if actual_content == modified_content:
                write_log(f"클립보드 변경 성공: {modified_content!r}")
                break
            elif attempt < max_retries:
                write_log(f"클립보드 변경 실패 (시도 {attempt + 1}/{max_retries + 1}), {retry_delay}초 후 재시도")
                time.sleep(retry_delay)
            else:
                write_log(f"최대 재시도 초과: 클립보드 변경 실패")
                show_warning_async("클립보드 변경 실패. 최대 재시도 초과.")
                return
        except Exception as e:
            write_log(f"클립보드 읽기 오류: {str(e)}")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                show_warning_async("클립보드 읽기 실패.")
                return
    if not change_tap_cccv_and_back(modified_content):
        return
    if img_action:
        img_dell_action()
    time.sleep(0.1)
    pyautogui.click(final_x, 301)
    max_clear_retries = 3
    for clear_attempt in range(max_clear_retries):
        time.sleep(0.05)
        pyperclip.copy("")
        clipboard_content = pyperclip.paste()
        write_log(f"클립보드 비우기 시도 {clear_attempt + 1}/{max_clear_retries}: 현재 클립보드 = {clipboard_content!r}")
        if clipboard_content == "":
            write_log("클립보드 비우기 성공")
            break
        elif clear_attempt < max_clear_retries - 1:
            write_log(f"클립보드 비우기 실패, 재시도 중...")
            time.sleep(retry_delay)
        else:
            write_log("최대 재시도 초과: 클립보드 비우기 실패")
            show_warning_async("클립보드 비우기 실패")
            return
    if pyperclip.paste() == "":
        pyautogui.moveTo(current_position)
        write_log(f"마우스 이동 완료: {current_position}")
    else:
        write_log("클립보드 비우기 최종 실패, 마우스 이동 생략")
        show_warning_async("클립보드 초기화 오류")

def on_button1_click():
    settings["button1_clicks"] += 1
    current_position = pyautogui.position()
    pyautogui.click(settings["check_c"], 301)
    pyautogui.moveTo(current_position)

def on_button_img_check():
    settings["button1_clicks"] += 1
    perform_action("이미지 삭제", settings["check_c"], img_action=True)

def on_button2_click():
    settings["button2_clicks"] += 1
    perform_action("검색차단", settings["fil_f"])

def on_button_img_search_block():
    settings["button2_clicks"] += 1
    perform_action("검색차단", settings["fil_f"], img_action=True)

def on_button3_click():
    settings["button3_clicks"] += 1
    perform_action("삭제", settings["dell_d"])

def on_button4_click():
    settings["button4_clicks"] += 1
    perform_action("차단삭제", settings["hdell_d"])

def on_tab2_button1_click(): # 문제 없음
    settings["button1_clicks"] += 1
    current_position = pyautogui.position()
    pyautogui.click(settings["ok_x"], 310)
    pyautogui.moveTo(current_position)

def on_tab2_button2_click():# 노출 차단
    settings["button1_clicks"] += 1
    coords = calculate_coordinates()
    perform_action("검색차단", coords["block_x"])

def on_tab2_button3_click(): # 삭제
    settings["button1_clicks"] += 1
    coords = calculate_coordinates()
    perform_action("삭제", coords["del_x"])

def on_tab2_button4_click(): # 삭제 및 차단
    settings["button1_clicks"] += 1    
    coords = calculate_coordinates()
    perform_action("차단삭제", coords["block_del_x"])

def on_tab2_button5_click(): # 이미지 삭제 및 차단
    settings["button1_clicks"] += 1
    perform_action("검색차단", settings["img_block_x"])

def calculate_coordinates():
    ok_x = settings["ok_x"]
    img_block_x = settings["img_block_x"]
    distance = img_block_x - ok_x
    return {
        "block_x": ok_x + int(distance * (1/4)),  # 2번탭 노출 차단 X좌표
        "del_x": ok_x + int(distance * (2/4)),    # 2번탭 삭제 X좌표
        "block_del_x": ok_x + int(distance * (3/4))  # 2번탭 삭제 및 차단 X좌표
    }

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("설정")
    settings_window.geometry("330x640")
    settings_window.configure(bg="#1a1b1b")

    def create_entry(parent, label_text, var_name, row):
        tk.Label(parent, text=label_text, bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        entry = tk.Entry(parent, font=("Helvetica", 10))
        entry.grid(row=row, column=1, padx=5, pady=2)
        entry.insert(0, settings[var_name])
        return entry

    coord_frame = tk.LabelFrame(settings_window, text="캐릭터 필터링 좌표 설정", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 11, "bold"))
    coord_frame.pack(pady=10, padx=10, fill="both")

    coord_entries = {
        "제타복사 X": "start_x", "제타복사 Y": "start_y",
        "확인 X": "check_c", 
        "차단삭제 X": "hdell_d",
        "쓰레기통 X": "imgd_x", "쓰레기통 Y": "imgd_y",
        "이미지 삭제 확인 X": "imgdc_x", "이미지 삭제 확인 Y": "imgdc_y",
    }
    coord_input = {}
    for i, (label, var) in enumerate(coord_entries.items()):
        coord_input[var] = create_entry(coord_frame, label, var, i)

    # 새로운 좌표 설정 프레임 추가
    coord_frame2 = tk.LabelFrame(settings_window, text="이미지 필터링 좌표 설정", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 11, "bold"))
    coord_frame2.pack(pady=10, padx=10, fill="both")

    # 문제 없음 X 좌표
    tk.Label(coord_frame2, text="문제 없음 X:", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=2)
    ok_x_entry = tk.Entry(coord_frame2, font=("Helvetica", 10))
    ok_x_entry.grid(row=0, column=1, padx=5, pady=2)
    ok_x_entry.insert(0, settings.get("ok_x", "550"))

    # 이미지 삭제 및 차단 X 좌표
    tk.Label(coord_frame2, text="이미지 삭제 및 차단 X:", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", padx=5, pady=2)
    img_block_x_entry = tk.Entry(coord_frame2, font=("Helvetica", 10))
    img_block_x_entry.grid(row=1, column=1, padx=5, pady=2)
    img_block_x_entry.insert(0, settings.get("img_block_x", "1510"))

    delay_frame = tk.LabelFrame(settings_window, text="딜레이 설정 (ms)", bg="#1a1b1b", fg="#ffffff", font=("Helvetica", 10, "bold"))
    delay_frame.pack(pady=10, padx=10, fill="both")

    def update_slider_from_entry(slider, entry):
        try:
            value = float(entry.get())
            slider.set(round(value, 3))
        except ValueError:
            pass

    def update_entry_from_slider(entry, slider):
        entry.delete(0, tk.END)
        entry.insert(0, f"{slider.get():.3f}")

    input_delay_row = tk.Frame(delay_frame, bg="#1a1b1b")
    input_delay_row.pack(fill="x", padx=10, pady=2)
    tk.Label(input_delay_row, text="입력 딜레이", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(side="left")
    input_delay_entry = tk.Entry(input_delay_row, font=("Helvetica", 10), width=7)
    input_delay_entry.pack(side="right")
    input_delay_entry.insert(0, f"{settings['pause']:.3f}")
    input_delay_slider = tk.Scale(delay_frame, from_=0, to=1, resolution=0.001, orient="horizontal", length=250, bg="#1a1b1b", fg="#ecf0f1", highlightthickness=0)
    input_delay_slider.set(settings["pause"])
    input_delay_slider.pack(pady=2, fill="x", padx=10)
    input_delay_slider.config(command=lambda val: update_entry_from_slider(input_delay_entry, input_delay_slider))
    input_delay_entry.bind("<Return>", lambda e: update_slider_from_entry(input_delay_slider, input_delay_entry))

    paste_delay_row = tk.Frame(delay_frame, bg="#1a1b1b")
    paste_delay_row.pack(fill="x", padx=10, pady=2)
    tk.Label(paste_delay_row, text="붙여넣기 딜레이", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10)).pack(side="left")
    paste_delay_entry = tk.Entry(paste_delay_row, font=("Helvetica", 10), width=7)
    paste_delay_entry.pack(side="right")
    paste_delay_entry.insert(0, f"{settings['pausecccv']:.3f}")
    paste_delay_slider = tk.Scale(delay_frame, from_=0, to=1, resolution=0.001, orient="horizontal", length=250, bg="#1a1b1b", fg="#ecf0f1", highlightthickness=0)
    paste_delay_slider.set(settings["pausecccv"])
    paste_delay_slider.pack(pady=2, fill="x", padx=10)
    paste_delay_slider.config(command=lambda val: update_entry_from_slider(paste_delay_entry, paste_delay_slider))
    paste_delay_entry.bind("<Return>", lambda e: update_slider_from_entry(paste_delay_slider, paste_delay_entry))

    total_clicks = sum(settings[click] for click in ["button1_clicks", "button2_clicks", "button3_clicks", "button4_clicks"])
    total_clicks_label = tk.Label(settings_window, text=f"총 버튼 클릭 횟수: {total_clicks}", bg="#1a1b1b", fg="#ecf0f1", font=("Helvetica", 10))
    total_clicks_label.pack(pady=5)

    local_button_style = {
        "width": 15, "height": 1, "bg": "#6728ff", "fg": "#ecf0f1",
        "font": ("Helvetica", 10, "bold"), "activebackground": "#e74c3c",
        "activeforeground": "#ffffff"
    }

    def save_settings_window():
        try:
            # 기본 좌표값 가져오기
            settings["ok_x"] = int(ok_x_entry.get())
            settings["img_block_x"] = int(img_block_x_entry.get())
            
            # 나머지 좌표 설정
            settings["start_x"] = int(coord_input["start_x"].get())
            settings["start_y"] = int(coord_input["start_y"].get())
            settings["check_c"] = int(coord_input["check_c"].get())
            settings["hdell_d"] = int(coord_input["hdell_d"].get())
            settings["imgd_x"] = int(coord_input["imgd_x"].get())
            settings["imgd_y"] = int(coord_input["imgd_y"].get())
            settings["imgdc_x"] = int(coord_input["imgdc_x"].get())
            settings["imgdc_y"] = int(coord_input["imgdc_y"].get())
            
            # 딜레이 설정
            settings["pause"] = float(input_delay_entry.get())
            settings["pausecccv"] = float(paste_delay_entry.get())
            pyautogui.PAUSE = settings["pause"]
            
            save_settings(settings)
            settings_window.destroy()
        except ValueError:
            msgbox.showerror("설정 저장 오류", "입력값 오류. 숫자만 입력하세요.")

    button_frame = tk.Frame(settings_window, bg="#1a1b1b")
    button_frame.pack(pady=10)
    save_btn = tk.Button(button_frame, text="저장", command=save_settings_window, **local_button_style)
    save_btn.grid(row=0, column=0, padx=5)
    save_btn.bind("<Enter>", on_enter)
    save_btn.bind("<Leave>", on_leave)

    reset_btn = tk.Button(button_frame, text="초기화", command=lambda: reset_clicks(total_clicks_label), **local_button_style)
    reset_btn.grid(row=0, column=1, padx=5)
    reset_btn.bind("<Enter>", on_enter)
    reset_btn.bind("<Leave>", on_leave)

    footer_frame = tk.Frame(settings_window, bg="#1a1b1b")
    footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)

    debug_var = tk.BooleanVar(value=DEBUG_ENABLED)
    debug_check = tk.Checkbutton(
        footer_frame, text="디버그 모드", variable=debug_var,
        bg="#1a1b1b", fg="#ecf0f1", selectcolor="#6728ff", font=("Helvetica", 10)
    )
    debug_check.pack(side="left", padx=5)

    def save_debug_settings():
        global DEBUG_ENABLED
        settings["debug"] = debug_var.get()
        DEBUG_ENABLED = settings["debug"]
        save_settings(settings)
        write_log(f"설정 저장됨: 디버그 모드 = {DEBUG_ENABLED}")

    save_button = tk.Button(
        footer_frame, text="저장", command=save_debug_settings,
        bg="#6728ff", fg="#ecf0f1", font=("Helvetica", 10)
    )
    save_button.pack(side="left", padx=5)
    save_button.bind("<Enter>", on_enter)
    save_button.bind("<Leave>", on_leave)

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
root.geometry("300x330")
root.attributes("-topmost", True)
root.configure(bg="#1a1b1b")

# ttk 스타일 설정
style = ttk.Style()
style.theme_create("CustomDark", parent="alt", settings={
    "TNotebook": {
        "configure": {
            "background": "#1a1b1b",
            "borderwidth": 0,
            "highlightthickness": 0,
            "tabmargins": [0, 0, 0, 0],
            "focuscolor": "#1a1b1b"
        }
    },
    "TNotebook.Tab": {
        "configure": {
            "padding": [10, 2],
            "background": "#1a1b1b",
            "foreground": "#ecf0f1",
            "borderwidth": 0,
            "focuscolor": "#1a1b1b"
        },
        "map": {
            "background": [("selected", "#6728ff"), ("!selected", "#1a1b1b")],
            "foreground": [("selected", "#ffffff"), ("!selected", "#ecf0f1")],
            "expand": [("selected", [1, 1, 1, 0])]
        }
    },
    "TFrame": {
        "configure": {
            "background": "#1a1b1b",
            "borderwidth": 0,
            "highlightthickness": 0,
            "focuscolor": "#1a1b1b"
        }
    }
})
style.theme_use("CustomDark")

# 포커스 표시 제거
root.option_add('*focusHighlight', '#1a1b1b')
root.option_add('*highlightBackground', '#1a1b1b')
root.option_add('*highlightColor', '#1a1b1b')

# 탭 너비 계산을 위한 함수
def adjust_tab_width(event):
    try:
        tab_count = notebook.index('end')
        if tab_count > 0:
            tab_width = event.width // tab_count
            style.configure("TNotebook.Tab", width=tab_width)
    except Exception:
        pass

def on_enter(event):
    event.widget.config(bg="#3e11ab")

def on_leave(event):
    event.widget.config(bg="#6728ff")

button_style1 = {
    "width": 26, "height": 2, "bg": "#6728ff", "fg": "#ecf0f1",
    "font": ("Helvetica", 13, "bold"), "activebackground": "#e74c3c",
    "activeforeground": "#ffffff"
}

button_style2 = {
    "width": 12, "height": 2, "bg": "#6728ff", "fg": "#ecf0f1",
    "font": ("Helvetica", 13, "bold"), "activebackground": "#e74c3c",
    "activeforeground": "#ffffff"
}

# 탭 생성
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=0, pady=0)
notebook.bind("<<NotebookTabChanged>>", adjust_tab_width)
notebook.bind("<Configure>", adjust_tab_width)

# 첫 번째 탭 (기존 기능)
tab1 = ttk.Frame(notebook, style="TFrame")
notebook.add(tab1, text="캐릭터 필터링", padding=0)

frame1 = tk.Frame(tab1, bg="#1a1b1b", highlightthickness=0, bd=0)
frame1.pack(pady=5)

button1 = tk.Button(frame1, text="확인", command=on_button1_click, **button_style2)
button1.pack(side="left", padx=5)
button1.bind("<Enter>", on_enter)
button1.bind("<Leave>", on_leave)

button_img_check = tk.Button(frame1, text="실사 확인", command=on_button_img_check, **button_style2)
button_img_check.pack(side="left", padx=5)
button_img_check.bind("<Enter>", on_enter)
button_img_check.bind("<Leave>", on_leave)

frame2 = tk.Frame(tab1, bg="#1a1b1b")
frame2.pack(pady=5)

button2 = tk.Button(frame2, text="검색 차단", command=on_button2_click, **button_style2)
button2.pack(side="left", padx=5)
button2.bind("<Enter>", on_enter)
button2.bind("<Leave>", on_leave)

button_img_search_block = tk.Button(frame2, text="실사 검차", command=on_button_img_search_block, **button_style2)
button_img_search_block.pack(side="left", padx=5)
button_img_search_block.bind("<Enter>", on_enter)
button_img_search_block.bind("<Leave>", on_leave)

button3 = tk.Button(tab1, text="삭제", command=on_button3_click, **button_style1)
button3.pack(pady=5)
button3.bind("<Enter>", on_enter)
button3.bind("<Leave>", on_leave)

button4 = tk.Button(tab1, text="삭제 및 차단", command=on_button4_click, **button_style1)
button4.pack(pady=5)
button4.bind("<Enter>", on_enter)
button4.bind("<Leave>", on_leave)

# 두 번째 탭 (추가 기능)
tab2 = ttk.Frame(notebook, style="TFrame")
notebook.add(tab2, text="이미지 필터링", padding=0)

# 첫째 줄 - 문제 없음
button1 = tk.Button(tab2, text="문제 없음", command=on_tab2_button1_click, **button_style1)
button1.pack(pady=5, padx=5)
button1.bind("<Enter>", on_enter)
button1.bind("<Leave>", on_leave)

# 둘째 줄 - 노출 차단
button2 = tk.Button(tab2, text="노출 차단", command=on_tab2_button2_click, **button_style1)
button2.pack(pady=5, padx=5)
button2.bind("<Enter>", on_enter)
button2.bind("<Leave>", on_leave)

# 셋째 줄 - 삭제 / 삭제 및 차단
frame3 = tk.Frame(tab2, bg="#1a1b1b", highlightthickness=0, bd=0)
frame3.pack(pady=5)

button3 = tk.Button(frame3, text="삭제", command=on_tab2_button3_click, **button_style2)
button3.pack(side="left", padx=5)
button3.bind("<Enter>", on_enter)
button3.bind("<Leave>", on_leave)

button4 = tk.Button(frame3, text="삭제 및 차단", command=on_tab2_button4_click, **button_style2)
button4.pack(side="left", padx=5)
button4.bind("<Enter>", on_enter)
button4.bind("<Leave>", on_leave)

# 넷째 줄 - 이미지 삭제 및 차단
button5 = tk.Button(tab2, text="이미지 삭제 및 차단 (실사)", command=on_tab2_button5_click, **button_style1)
button5.pack(pady=5, padx=5)
button5.bind("<Enter>", on_enter)
button5.bind("<Leave>", on_leave)

settings_button = tk.Button(root, text="⚙", command=open_settings, width=2, height=1, bg="#6728ff", fg="#ecf0f1", font=("Helvetica", 12, "bold"), activebackground="#e74c3c", activeforeground="#ecf0f1")
settings_button.pack(pady=10)
settings_button.bind("<Enter>", on_enter)
settings_button.bind("<Leave>", on_leave)

def on_close():
    save_settings(settings)
    root.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()