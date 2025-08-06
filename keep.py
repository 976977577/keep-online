import time
import pyautogui
import schedule
from datetime import datetime, time as dt_time

DEFAULT_IDLE = 600  # 默认检测时间：10分钟
DEFAULT_HOURS = "9:30-20:30"


def parse_time_range(hours: str):
    """解析时间段字符串为 datetime.time 对象"""
    start_str, end_str = hours.split('-')
    start = dt_time(*map(int, start_str.split(':')))
    end = dt_time(*map(int, end_str.split(':')))
    return start, end


def is_active_time(hours: str) -> bool:
    """判断当前时间是否在活跃时间段内"""
    start, end = parse_time_range(hours)
    now = datetime.now().time()

    if start <= end:
        return start <= now <= end
    else:  # 跨午夜
        return now >= start or now <= end


def simulate_mouse_move():
    """模拟轻微移动鼠标"""
    pyautogui.moveRel(0, 1)
    time.sleep(0.1)
    pyautogui.moveRel(0, -1)


def check_mouse_idle(idle: int, hours: str):
    """检测是否需要模拟鼠标操作"""
    if not is_active_time(hours):
        return

    if pyautogui.FAILSAFE:
        pyautogui.FAILSAFE = False

    last_pos = pyautogui.position()
    time.sleep(idle)
    current_pos = pyautogui.position()

    if current_pos == last_pos:
        simulate_mouse_move()


def run(idle: int, hours: str):
    """主运行函数"""
    schedule.every(30).seconds.do(check_mouse_idle, idle, hours)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("已手动终止程序。")


def prompt_user_for_time_range() -> str:
    """交互式选择时间段（仅两个预设）"""
    print("\n请选择活跃时间段：")
    print("1. 工作时间段（9:30-20:30）")
    print("2. 全天（00:00-23:59）")

    choice = input("请输入选项编号（1-2）：").strip()

    presets = {
        "1": "9:30-20:30",
        "2": "00:00-23:59"
    }

    if choice in presets:
        return presets[choice]
    else:
        print("无效输入，已回退为默认时间段。")
        return DEFAULT_HOURS


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="保持企业微信在线状态")
    parser.add_argument("-t", "--idle", type=int, default=DEFAULT_IDLE,
                        help="检测鼠标不动的时间（秒），默认600秒")
    parser.add_argument("-a", "--active", type=str,
                        help="活跃时间段，格式为'HH:MM-HH:MM'，如未提供将交互选择")

    args = parser.parse_args()

    active_time = args.active or prompt_user_for_time_range()

    print(f"\n脚本已启动，空闲检测时间：{args.idle} 秒（即 {args.idle // 60} 分钟）")
    print(f"当鼠标在 {args.idle} 秒（即 {args.idle // 60} 分钟）内没有任何移动时，系统将自动模拟一次轻微的鼠标移动，以防止被识别为“离开状态”。")
    print(f"活跃时间段：{active_time}\n")

    run(args.idle, active_time)
