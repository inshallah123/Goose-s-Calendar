import flet as ft
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import calendar
import json
import os
import sys
from lunarcalendar import Converter, Solar
from lunarcalendar.festival import festivals
from lunarcalendar.solarterm import solarterms
import chinese_calendar as cn_cal
LUNAR_AVAILABLE = True
HOLIDAY_AVAILABLE = True


def get_user_data_dir() -> str:
    """
    获取用户数据目录，确保程序有权限写入。
    此版本经过修正，确保在所有情况下都返回一个有效的字符串路径。
    """
    # 优先处理 Windows 平台
    if sys.platform == "win32":
        path = os.getenv("APPDATA")
        # 如果成功获取 APPDATA 路径，则使用它
        if path:
            return os.path.join(path, "GooseCalendar")
        # 如果 APPDATA 不存在（极端情况），则 fall back 到用户主目录
        # 此处不再有 return，会自然地执行到函数末尾的通用后备方案

    # 处理 macOS 平台
    elif sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~/Library/Application Support"), "GooseCalendar")

    # 通用后备方案：适用于 Linux、其他操作系统，或出现问题的 Windows
    # 在用户主目录下创建一个隐藏文件夹来存储数据，这是一个非常标准的做法。
    return os.path.join(os.path.expanduser("~"), ".GooseCalendar")

application_path = get_user_data_dir()

# 确保这个目录存在
if not os.path.exists(application_path):
    os.makedirs(application_path)

# 现在 events_file 的路径是安全的，例如 C:\\Users\\yyh\\AppData\\Roaming\\GooseCalendar\\calendar_events.json
events_file = os.path.join(application_path, "calendar_events.json")




def main(page: ft.Page) -> None:

    page.title = "GOOSE'S CALENDAR Version 0.0"
    page.window.width = 950
    page.window.height = 780
    page.padding = 15
    page.bgcolor = "#F8F6F4"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT


    # 创建缓存字典，用于存储已计算过的日期信息，避免重复计算
    lunar_info_cache: Dict[date, Tuple[str, str, str, str]] = {}
    holiday_info_cache: Dict[date, Tuple[bool, bool, str]] = {}

    # 配色方案
    colors: Dict[str, str] = {
        "primary": "#6B73FF", "primary_light": "#9B9EFF", "secondary": "#FF6B9D",
        "accent": "#4ECDC4", "warning": "#FF4757", "success": "#95E1D3",
        "text_primary": "#2C3E50", "text_secondary": "#7F8C8D", "background": "#FFFFFF",
        "surface": "#F8F9FA", "today": "#FFE66D", "selected": "#FF9500",
        "weekend": "#00C851", "weekday": "#F5F9FF", "event_work": "#4834D4",
        "event_daily": "#686DE0", "event_personal": "#FF5252", "event_custom": "#00C851",
        "event_periodic": "#FF6B35", "custom_dates": "#FF9FF3", "custom_period": "#54A0FF",
        "holiday": "#E74C3C",  "workday": "#95A5A6", "lunar": "#8B4513", "solar_term": "#228B22"
    }

    # 农历相关数据
    chinese_numbers = ["初", "十", "廿", "三"]
    chinese_digits = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    chinese_months = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]

    def get_lunar_day_name(day: int) -> str:
        """获取农历日期的中文表示"""
        if day == 10: return "初十"
        if day == 20: return "二十"
        if day == 30: return "三十"
        decade = day // 10
        unit = day % 10
        if decade == 0: return f"初{chinese_digits[unit - 1]}"
        return f"{chinese_numbers[decade]}{chinese_digits[unit - 1] if unit > 0 else '十'}"

    def get_lunar_info(year: int, month: int, day: int) -> Tuple[str, str, str, str]:
        """
        获取农历信息：返回 (农历月份, 主要显示文本, 找到的节气名称, 原始农历日名称)
        增加了缓存机制以提高性能。
        """
        current_date_obj = date(year, month, day)
        # 检查缓存中是否已有结果
        if current_date_obj in lunar_info_cache:
            return lunar_info_cache[current_date_obj]

        if not LUNAR_AVAILABLE:
            return "", "", "", ""

        try:
            # --- 原始计算逻辑保持不变 ---
            solar = Solar(year, month, day)
            lunar = Converter.Solar2Lunar(solar)

            lunar_month_str = (("闰" if lunar.isleap else "") + chinese_months[lunar.month - 1] + "月")
            actual_lunar_day_name = get_lunar_day_name(lunar.day)
            display_text = lunar_month_str if lunar.day == 1 else actual_lunar_day_name

            all_events = festivals + solarterms
            today_festivals = [fest.get_lang('zh') for fest in all_events if fest(year) == current_date_obj]

            solar_term_keywords = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨', '立夏', '小满', '芒种', '夏至', '小暑', '大暑', '立秋', '处暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至']
            important_festivals = ['除夕', '春节', '元宵节', '龙抬头', '端午节', '七夕', '中元节', '中秋节', '重阳节', '腊八节']

            found_solar_term = next((fest_name for fest_name in today_festivals if fest_name in solar_term_keywords), "")
            found_major_festival = ""
            if not found_solar_term:
                found_major_festival = next((fest_name for fest_name in today_festivals if fest_name in important_festivals), "")

            other_festival = ""
            if not found_solar_term and not found_major_festival and today_festivals:
                other_festival = today_festivals[0]

            if found_solar_term: display_text = found_solar_term
            elif found_major_festival: display_text = found_major_festival
            elif other_festival: display_text = other_festival

            # 将计算结果存入缓存
            result = (lunar_month_str, display_text, found_solar_term, lunar_month_str if lunar.day == 1 else actual_lunar_day_name)
            lunar_info_cache[current_date_obj] = result
            return result

        except Exception as e:
            print(f"Error in get_lunar_info for {year}-{month}-{day}: {e}")
            return "", "", "", ""


    def get_holiday_info(year: int, month: int, day: int) -> Tuple[bool, bool, str]:
        """
        获取节假日信息：返回 (是否休息日, 是否调休上班, 节日名称)
        增加了缓存机制和对库年份范围的异常处理。
        """
        check_date = date(year, month, day)
        # 检查缓存中是否已有结果
        if check_date in holiday_info_cache:
            return holiday_info_cache[check_date]

        if not HOLIDAY_AVAILABLE:
            return False, False, ""

        try:
            is_holiday = cn_cal.is_holiday(check_date)
            is_workday = cn_cal.is_workday(check_date)
            holiday_detail = cn_cal.get_holiday_detail(check_date)
            holiday_name = holiday_detail[1] if holiday_detail and holiday_detail[1] else ""
            is_makeup_workday = (check_date.weekday() >= 5) and is_workday
            is_statutory_holiday = is_holiday and bool(holiday_name)

            # 将计算结果存入缓存
            result = (is_statutory_holiday, is_makeup_workday, holiday_name)
            holiday_info_cache[check_date] = result
            return result

        except ValueError:
            return False, False, ""
        except Exception as e:
            print(f"Unexpected error in get_holiday_info for {year}-{month}-{day}: {e}")
            return False, False, ""

    # 事件数据管理
    events_data: Dict[str, List[Dict]] = {}  # 事件数据字典
    periodic_events_rules: List[Dict] = []  # 专门存储周期性事件规则

    # 修改后的 load_events 函数

    def load_events() -> None:
        """
        加载事件数据：从文件中恢复记录。
        如果文件不存在，则自动创建一个空的配置文件。
        """
        nonlocal events_data, periodic_events_rules

        # 初始化内存中的变量，以防万一
        events_data = {}
        periodic_events_rules = []

        # 检查文件是否存在
        if os.path.exists(events_file):
            try:
                # 如果文件存在，则尝试读取它
                with open(events_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容新结构
                    if isinstance(data, dict) and "single_events" in data:
                        events_data = data.get("single_events", {})
                        periodic_events_rules = data.get("periodic_rules", [])
                    # 兼容旧结构
                    else:
                        events_data = data
            except (json.JSONDecodeError, IOError) as e:
                # 如果文件损坏或无法读取，打印错误并使用空数据
                print(f"读取事件文件时出错: {e}. 将使用空数据。")
        else:
            # --- 核心改动在这里 ---
            # 如果文件不存在，不仅在内存中初始化，还要创建一个空的物理文件
            print("事件文件不存在，将创建一个新的。")
            try:
                # 直接调用 save_events() 函数，它会用当前的空数据创建一个新文件
                save_events()
            except IOError as e:
                print(f"创建新的事件文件时失败: {e}")

    def save_events() -> None:
        """保存事件数据：将普通事件和周期性规则分别保存到文件。"""
        try:
            with open(events_file, 'w', encoding='utf-8') as f:
                # 保存为新的数据结构
                json.dump({
                    "single_events": events_data,
                    "periodic_rules": periodic_events_rules
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存事件时出错: {e}")

    # 初始化数据
    load_events()

    # 获取当前日期信息
    current_date: datetime = datetime.now()
    selected_year: int = current_date.year
    selected_month: int = current_date.month
    selected_day: Optional[int] = current_date.day  # 当前选中的日期

    def get_date_key(year: int, month: int, day: int) -> str:
        """生成日期键：创建日期的唯一标识"""
        return f"{year}-{month:02d}-{day:02d}"

    def check_if_date_matches_rule(target_date: date, rule: Dict) -> bool:
        """辅助函数：检查给定日期是否匹配周期性规则。"""
        start_date_str = rule.get("original_date")
        if not start_date_str: return False

        target_date_key = target_date.strftime("%Y-%m-%d")
        if target_date_key in rule.get("excluded_dates", []):
            return False

        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError:
            return False

        period_info = rule.get("period_info", {})
        period_type = period_info.get("type")

        if target_date < start_date: return False

        if period_type == "每天":
            return True
        elif period_type == "每周":
            return (target_date - start_date).days % 7 == 0
        elif period_type == "每月":
            # 简单情况：日期相同
            if target_date.day == start_date.day: return True
            # 特殊情况：开始日在某月不存在（如31日），目标日是该月最后一天
            try:
                target_date.replace(day=start_date.day)
                return False  # 如果能替换，说明目标日不是该月最后一天，不匹配
            except ValueError:  # 无法替换，说明目标日是该月最后一天
                return target_date.day == calendar.monthrange(target_date.year, target_date.month)[1]

        # --- 新增的季度判断逻辑 ---
        elif period_type == "每季":
            # 首先，计算月份差值是否为3的倍数
            month_diff = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
            if month_diff >= 0 and month_diff % 3 == 0:
                # 月份正确后，再检查日期
                # 简单情况：日期相同
                if target_date.day == start_date.day:
                    return True
                # 特殊情况：处理月末日期（例如，从1月31日开始，季度事件应落在4月30日）
                last_day_of_target_month = calendar.monthrange(target_date.year, target_date.month)[1]
                if start_date.day > last_day_of_target_month and target_date.day == last_day_of_target_month:
                    return True
            return False
        # --- 结束新增逻辑 ---

        elif period_type == "每年":
            if target_date.month == start_date.month and target_date.day == start_date.day:
                return True
            # 处理闰年2月29日的情况
            if start_date.month == 2 and start_date.day == 29 and not calendar.isleap(target_date.year):
                return target_date.month == 2 and target_date.day == 28
            return False
        elif period_type == "自定义周期":
            interval = period_info.get("interval", 1)
            unit = period_info.get("unit", "天")
            if unit == "天":
                return (target_date - start_date).days % interval == 0
            # 其他自定义周期类型的匹配逻辑可以根据需要在这里扩展
            # 为简化起见，此处只实现最常见的“天”
        elif period_type == "自定义日期":
            return target_date_key in period_info.get("custom_dates", [])

        return False

    def get_events_for_date(year: int, month: int, day: int) -> List[Dict]:
        """获取指定日期的事件：组合普通事件和动态计算的周期性事件。"""
        date_key = get_date_key(year, month, day)
        target_date = date(year, month, day)

        # 1. 获取当天的普通事件
        events_for_date = events_data.get(date_key, []).copy()

        # 2. 动态检查并添加符合规则的周期性事件
        for rule in periodic_events_rules:
            if check_if_date_matches_rule(target_date, rule):
                events_for_date.append(rule)

        return events_for_date

    def add_event(year: int, month: int, day: int, title: str, category: str, description: str = "",
                  is_periodic: bool = False, period_info: Dict = None) -> None:
        """添加单个普通事件。"""
        date_key = get_date_key(year, month, day)
        if date_key not in events_data:
            events_data[date_key] = []
        event = {"title": title, "category": category, "description": description, "is_periodic": is_periodic,
                 "period_info": period_info or {}, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        events_data[date_key].append(event)
        save_events()



    def add_periodic_event(year: int, month: int, day: int, title: str, category: str,
                           description: str, period_info: Dict) -> None:
        """添加周期性事件规则：不再计算所有实例，只存储规则本身。"""
        rule = {
            "title": title,
            "category": category,
            "description": description,
            "is_periodic": True,
            "period_info": period_info,
            "original_date": get_date_key(year, month, day), # 记录起始日期
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "excluded_dates": [] # 用于“仅删除今日”功能
        }
        periodic_events_rules.append(rule)
        save_events()

    def create_month_view(year: int, month: int) -> ft.Container:
        """创建月份视图：绘制填充整个空间的大字块日历，包含农历和节假日信息"""
        cal = calendar.monthcalendar(year, month)
        weekday_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(day, size=16, color=colors["text_secondary"], text_align=ft.TextAlign.CENTER,
                                    weight=ft.FontWeight.W_600),
                    width=110, height=40, alignment=ft.Alignment.CENTER, bgcolor=colors["surface"], border_radius=8
                ) for day in weekday_labels
            ],
            alignment=ft.MainAxisAlignment.CENTER, spacing=3
        )

        date_rows: List[ft.Row] = []
        today: date = date.today()

        for week in cal:
            week_controls: List[ft.Container] = []
            for day in week:
                if day == 0:
                    week_controls.append(ft.Container(width=110, height=95))
                else:
                    is_today = (year == today.year and month == today.month and day == today.day)
                    is_selected = (year == selected_year and month == selected_month and day == selected_day)
                    day_of_week = date(year, month, day).weekday()
                    is_weekend = day_of_week >= 5

                    day_events = get_events_for_date(year, month, day)
                    has_events = len(day_events) > 0

                    lunar_month, lunar_day_str, solar_term, _ = get_lunar_info(year, month, day)
                    is_rest_day, is_makeup_workday, holiday_name = get_holiday_info(year, month, day)

                    # FIX 3: 优化颜色判断逻辑，解决节假日和周末颜色混淆问题
                    bg_color = colors["weekday"]  # 默认是工作日
                    text_color = "black"
                    border_color = None
                    border_width = 0

                    # 优先级 1: 首先判断是否为调休上班日
                    if is_makeup_workday:
                        bg_color = colors["workday"]
                    # 优先级 2: 然后判断是否为法定节假日（真正的休息日）
                    elif is_rest_day:
                        bg_color = colors["holiday"]
                    # 优先级 3: 之后判断是否为普通周末
                    elif is_weekend:
                        bg_color = colors["weekend"]
                    # 默认情况在最开始已经设置好了，即普通工作日

                    if is_selected:
                        border_color = colors["selected"]
                        border_width = 4
                    if is_today:
                        bg_color = colors["today"]
                        text_color = colors["text_primary"]

                    # 创建日期内容
                    # FIX 2: 为 date_content_controls 添加 List[ft.Control] 类型注解
                    date_content_controls: List[ft.Control] = [
                        ft.Text(str(day), size=24, color=text_color, text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.BOLD)
                    ]

                    # 统一显示附加信息（节日/农历/节气）
                    # 优先显示节日名，其次是节气/特殊农历日，最后是普通农历日
                    display_str = ""
                    if holiday_name:
                        display_str = holiday_name[:4]
                    elif lunar_day_str:
                        display_str = lunar_day_str

                    if display_str:
                        # 如果是节气，使用特殊颜色
                        lunar_text_color = colors["solar_term"] if solar_term else text_color
                        date_content_controls.append(
                            ft.Text(display_str, size=11, color=lunar_text_color, text_align=ft.TextAlign.CENTER,
                                    weight=ft.FontWeight.W_500)
                        )

                    # 添加事件指示器
                    if has_events:
                        date_content_controls.append(
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Container(width=4, height=4, border_radius=2, bgcolor=text_color)
                                        for _ in range(min(len(day_events), 3))
                                    ],
                                    spacing=2, alignment=ft.MainAxisAlignment.CENTER
                                ),
                                height=8
                            )
                        )

                    date_content = ft.Column(
                        controls=date_content_controls, spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER
                    )

                    day_container = ft.Container(
                        content=date_content, width=110, height=95, border_radius=12,
                        bgcolor=bg_color, border=ft.Border.all(border_width, border_color) if border_color else None,
                        alignment=ft.Alignment.CENTER, animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                        on_click=lambda e, d=day: handle_date_click(d),
                        on_hover=lambda e: handle_hover(e),
                        animate_scale=ft.Animation(100)
                    )
                    week_controls.append(day_container)

            date_rows.append(ft.Row(controls=week_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=3))

        return ft.Container(
            content=ft.Column(
                controls=[weekday_row, ft.Container(height=10), *date_rows],
                spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20, bgcolor=colors["background"], border_radius=16,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=15, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                                offset=ft.Offset(0, 5))
        )

    def handle_hover(e: ft.ControlEvent) -> None:
        """处理悬停效果：让日期格子轻盈地响应"""
        if e.data == "true":
            e.control.scale = 1.05
            e.control.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, 3)
            )
        else:
            e.control.scale = 1.0
            e.control.shadow = None
        e.control.update()

    def handle_date_click(day: int) -> None:
        """处理日期点击：选中日期并显示事件"""
        nonlocal selected_day
        selected_day = day
        update_calendar()
        update_event_panel()

    def change_month(delta: int) -> None:
        """切换月份：优雅地翻页"""
        nonlocal selected_year, selected_month, selected_day

        selected_month += delta
        if selected_month > 12:
            selected_month = 1
            selected_year += 1
        elif selected_month < 1:
            selected_month = 12
            selected_year -= 1

        selected_day = None

        update_calendar()
        update_event_panel()

    def jump_to_date() -> None:
        """跳转到指定年月：快速导航功能"""

        def handle_jump():
            nonlocal selected_year, selected_month, selected_day
            try:
                input_year = int(year_input.value) if year_input.value else selected_year
                input_month = int(month_dropdown.value)

                current = datetime.now().year
                if current - 40 <= input_year <= current + 40:
                    selected_year = input_year
                    selected_month = input_month
                    selected_day = None
                    update_calendar()
                    update_event_panel()
                    page.pop_dialog()
                else:
                    error_text.value = f"年份范围应在 {current - 40} 到 {current + 40} 之间"
                    error_text.visible = True
                    page.update()
            except ValueError:
                error_text.value = "请输入有效的年份数字"
                error_text.visible = True
                page.update()

        def cancel_jump():
            page.pop_dialog()

        def on_year_change():
            error_text.visible = False
            page.update()

        month_options = [
            ft.dropdown.Option(str(month), f"{month}月 ({calendar.month_name[month]})")
            for month in range(1, 13)
        ]

        year_input = ft.TextField(
            label="输入年份",
            value=str(selected_year),
            bgcolor=colors["background"],
            color=colors["text_primary"],
            border_color=colors["primary"],
            width=120,
            text_align=ft.TextAlign.CENTER,
            on_change=on_year_change,
            hint_text="例如: 2024"
        )

        month_dropdown = ft.Dropdown(
            label="选择月份",
            options=month_options,
            value=str(selected_month),
            bgcolor=colors["background"],
            color=colors["text_primary"],
            width=180
        )

        current_year = datetime.now().year
        range_hint = ft.Text(
            f"支持年份: {current_year - 40} - {current_year + 40}",
            size=12,
            color=colors["text_secondary"],
            text_align=ft.TextAlign.CENTER
        )

        error_text = ft.Text(
            "",
            size=12,
            color=colors["today"],
            text_align=ft.TextAlign.CENTER,
            visible=False
        )

        # 优化快速年份选择按钮
        quick_year_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "去年",
                    on_click=lambda e: setattr(year_input, 'value', str(current_year - 1)) or year_input.update(),
                    style=ft.ButtonStyle(
                        bgcolor=colors["surface"],
                        color=colors["text_primary"],
                        elevation=1
                    ),
                    width=80,  # 增加宽度
                    height=40  # 增加高度
                ),
                ft.ElevatedButton(
                    "今年",
                    on_click=lambda e: setattr(year_input, 'value', str(current_year)) or year_input.update(),
                    style=ft.ButtonStyle(
                        bgcolor=colors["primary_light"],
                        color="white",
                        elevation=1
                    ),
                    width=80,
                    height=40
                ),
                ft.ElevatedButton(
                    "明年",
                    on_click=lambda e: setattr(year_input, 'value', str(current_year + 1)) or year_input.update(),
                    style=ft.ButtonStyle(
                        bgcolor=colors["surface"],
                        color=colors["text_primary"],
                        elevation=1
                    ),
                    width=80,
                    height=40
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10  # 增加间距
        )

        jump_dialog = ft.AlertDialog(
            title=ft.Text(
                "快速跳转",
                color=colors["text_primary"],
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[year_input, month_dropdown],
                            spacing=15,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Container(height=5),
                        range_hint,
                        error_text,
                        ft.Container(height=10),
                        ft.Text(
                            "快速选择年份:",
                            size=14,
                            color=colors["text_secondary"],
                            text_align=ft.TextAlign.CENTER
                        ),
                        quick_year_row
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True
                ),
                width=350
            ),
            actions=[
                ft.TextButton(
                    "取消",
                    on_click=cancel_jump,
                    style=ft.ButtonStyle(
                        color=colors["text_secondary"],
                        overlay_color=ft.Colors.with_opacity(0.1, colors["text_secondary"])
                    )
                ),
                ft.ElevatedButton(
                    "跳转",
                    on_click=handle_jump,
                    style=ft.ButtonStyle(
                        bgcolor=colors["accent"],
                        color="white",
                        elevation=2
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        page.show_dialog(jump_dialog)

    def go_to_today() -> None:
        """返回今天：快速定位"""
        nonlocal selected_year, selected_month, selected_day
        today = datetime.now()
        selected_year = today.year
        selected_month = today.month
        selected_day = today.day

        update_calendar()
        update_event_panel()

    def update_calendar() -> None:
        """更新日历显示"""
        calendar_container.content = create_month_view(selected_year, selected_month)
        month_title.value = f"{calendar.month_name[selected_month]} {selected_year}"
        page.update()

    def update_event_panel() -> None:
        """更新事件面板，包含农历和节假日信息"""
        if selected_day:
            events = get_events_for_date(selected_year, selected_month, selected_day)

            # 获取农历和节假日信息
            lunar_month, _, solar_term, actual_lunar_day = get_lunar_info(selected_year, selected_month, selected_day)
            is_holiday, is_makeup_workday, holiday_name = get_holiday_info(selected_year, selected_month, selected_day)

            # 更新日期显示
            date_text = f"{selected_year}年{selected_month}月{selected_day}日"
            if "月" in actual_lunar_day:
                 date_text += f" · {actual_lunar_day}"
            else:
                 date_text += f" · 农历{actual_lunar_day}"


            if solar_term:
                date_text += f" · {solar_term}"
            if holiday_name and holiday_name not in ["周末", "工作日"]:
                date_text += f" · {holiday_name}"

            selected_date_text.value = date_text

            events_column.controls.clear()

            if events:
                for i, event in enumerate(events):
                    event_card = create_event_card(event, i)
                    events_column.controls.append(event_card)
            else:
                events_column.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "这一天还没有任何事件记录呢~",
                            size=14,
                            color=colors["text_secondary"],
                            text_align=ft.TextAlign.CENTER
                        ),
                        alignment=ft.Alignment.CENTER,
                        padding=20
                    )
                )
        page.update()

    def create_event_card(event: Dict, index: int) -> ft.Container:
        """创建事件卡片：美观地展示事件信息（已修正类别显示问题）"""
        category_colors = {
            "工作": colors["event_work"],
            "日常": colors["event_daily"],
            "个人生活": colors["event_personal"],
            "自定义": colors["event_custom"],
            # 以下颜色保留，以备将来可能的设计
            "周期性": colors["event_periodic"],
            "自定义日期": colors["custom_dates"],
            "自定义周期": colors["custom_period"]
        }

        # --- 核心修改部分 ---

        # 1. 标题处理：为周期性事件的标题添加后缀
        title_text = event["title"]
        if event.get("is_periodic", False):
            period_info = event.get("period_info", {})
            period_type = period_info.get("type", "")

            # 根据不同周期类型生成后缀
            if period_type == "自定义周期":
                interval = period_info.get("interval", 1)
                unit = period_info.get("unit", "")
                title_text += f" (每{interval}{unit})"
            elif period_type == "自定义日期":
                title_text += " (自定义日期)"
            elif period_type:  # 处理 "每天", "每周", "每月", "每季", "每年"
                title_text += f" ({period_type})"

        # 2. 类别确定：直接使用事件本身的类别，不再覆盖
        # 这确保了无论事件是否为周期性，其颜色和标签都反映原始分类
        display_category = event["category"]

        # --- 修改结束 ---

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    display_category,  # 使用正确的类别
                                    size=10,
                                    color="white",
                                    weight=ft.FontWeight.BOLD
                                ),
                                # 从字典中获取对应类别的颜色
                                bgcolor=category_colors.get(display_category, colors["text_secondary"]),
                                padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                border_radius=10
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=16,
                                icon_color=colors["text_secondary"],
                                tooltip="删除事件",
                                on_click=lambda e, idx=index: delete_event(idx),
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.with_opacity(0.1, colors["text_secondary"])
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Text(
                        title_text,  # 使用处理过的标题
                        size=14,
                        color=colors["text_primary"],
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Text(
                        event.get("description", ""),
                        size=12,
                        color=colors["text_secondary"]
                    ) if event.get("description") else ft.Container()
                ],
                spacing=5
            ),
            padding=12,
            bgcolor=colors["surface"],
            border_radius=8,
            margin=ft.Margin(bottom=8)
        )



    def delete_event(event_index: int) -> None:
        """
        删除事件（已重构）：智能处理普通和周期性事件。
        """
        if not selected_day:
            return

        # 1. 获取当天显示的完整事件列表（包括普通和周期性）
        all_events_for_day = get_events_for_date(selected_year, selected_month, selected_day)

        # 检查索引是否有效
        if event_index >= len(all_events_for_day):
            print("Error: Event index out of range.")
            return

        # 2. 准确定位到要删除的事件对象
        event_to_delete = all_events_for_day[event_index]
        date_key = get_date_key(selected_year, selected_month, selected_day)

        # 3. 判断事件类型并执行相应逻辑
        is_periodic = event_to_delete.get("is_periodic", False)

        if is_periodic:
            # --- 处理周期性事件 ---

            # 找到原始规则，因为 event_to_delete 就是从 periodic_events_rules 来的引用
            original_rule = None
            for rule in periodic_events_rules:
                # 通过创建时间和标题来唯一识别规则
                if (rule.get("created_at") == event_to_delete.get("created_at") and
                        rule.get("title") == event_to_delete.get("title")):
                    original_rule = rule
                    break

            if not original_rule:
                print("Error: Could not find the original periodic rule to delete.")
                return

            def delete_single_occurrence():
                """仅删除今日：通过添加排除日期实现"""
                if "excluded_dates" not in original_rule:
                    original_rule["excluded_dates"] = []

                # 避免重复添加
                if date_key not in original_rule["excluded_dates"]:
                    original_rule["excluded_dates"].append(date_key)

                save_events()
                update_calendar()
                update_event_panel()
                page.pop_dialog()

            def delete_entire_series():
                """删除整个系列：从规则列表中移除"""
                periodic_events_rules.remove(original_rule)
                save_events()
                update_calendar()
                update_event_panel()
                page.pop_dialog()

            def cancel_delete():
                page.pop_dialog()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("删除周期性事件", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
                content=ft.Text(f"您想如何删除周期性事件「{event_to_delete['title']}」？"),
                actions=[
                    ft.TextButton("取消", on_click=cancel_delete),
                    ft.ElevatedButton("仅删除今天", on_click=delete_single_occurrence,
                                      style=ft.ButtonStyle(bgcolor=colors["warning"], color="white")),
                    ft.ElevatedButton("删除整个系列", on_click=delete_entire_series,
                                      style=ft.ButtonStyle(bgcolor=colors["today"], color="white"))
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            page.show_dialog(confirm_dialog)

        else:
            # --- 处理普通事件 ---
            def confirm_delete():
                if date_key in events_data and event_to_delete in events_data[date_key]:
                    events_data[date_key].remove(event_to_delete)
                    if not events_data[date_key]:
                        del events_data[date_key]
                    save_events()
                    update_calendar()
                    update_event_panel()
                page.pop_dialog()

            def cancel_delete():
                page.pop_dialog()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("确认删除", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
                content=ft.Text(f"确定要删除事件「{event_to_delete['title']}」吗？"),
                actions=[
                    ft.TextButton("取消", on_click=cancel_delete),
                    ft.ElevatedButton("删除", on_click=confirm_delete,
                                      style=ft.ButtonStyle(bgcolor=colors["today"], color="white"))
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            page.show_dialog(confirm_dialog)

    def show_custom_dates_selector(callback_func) -> None:
        """显示自定义日期选择器：让用户优雅地选择多个特定日期"""

        # 存储选中的日期
        selected_dates = []

        # 当前选择器显示的年月
        picker_year = selected_year
        picker_month = selected_month

        def update_picker_display():
            """更新日期选择器的显示"""
            cal = calendar.monthcalendar(picker_year, picker_month)

            # 更新月份标题
            picker_title.value = f"{calendar.month_name[picker_month]} {picker_year}"

            # 重新创建日期网格
            picker_grid.controls.clear()

            # 星期标题
            weekday_row = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(day, size=12, color=colors["text_secondary"],
                                        text_align=ft.TextAlign.CENTER),
                        width=35, height=25, alignment=ft.Alignment.CENTER
                    ) for day in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                ],
                spacing=2
            )
            picker_grid.controls.append(weekday_row)

            # 日期行
            for week in cal:
                week_controls = []
                for day in week:
                    if day == 0:
                        week_controls.append(ft.Container(width=35, height=35))
                    else:
                        date_str = f"{picker_year}-{picker_month:02d}-{day:02d}"
                        is_selected = date_str in selected_dates

                        day_btn = ft.Container(
                            content=ft.Text(
                                str(day),
                                size=12,
                                color="white" if is_selected else colors["text_primary"],
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL
                            ),
                            width=35,
                            height=35,
                            border_radius=17,
                            bgcolor=colors["primary"] if is_selected else colors["surface"],
                            alignment=ft.Alignment.CENTER,
                            on_click=lambda e, d=day: toggle_date_selection(d),
                            animate=ft.Animation(duration=150)
                        )
                        week_controls.append(day_btn)

                picker_grid.controls.append(
                    ft.Row(controls=week_controls, spacing=2)
                )

            page.update()

        def toggle_date_selection(day: int):
            """切换日期的选中状态"""
            date_str = f"{picker_year}-{picker_month:02d}-{day:02d}"
            if date_str in selected_dates:
                selected_dates.remove(date_str)
            else:
                selected_dates.append(date_str)

            # 更新选中日期显示
            update_selected_dates_display()
            update_picker_display()

        def update_selected_dates_display():
            """更新已选日期的显示"""
            if selected_dates:
                # 按日期排序
                sorted_dates = sorted(selected_dates)
                date_chips = []

                for date_str in sorted_dates:
                    year, month, day = date_str.split('-')
                    date_chip = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{month}月{day}日", size=11, color=colors["text_primary"]),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_size=12,
                                    icon_color=colors["text_secondary"],
                                    on_click=lambda e, ds=date_str: remove_date(ds)
                                )
                            ],
                            spacing=2
                        ),
                        bgcolor=colors["surface"],
                        border_radius=15,
                        padding=ft.Padding(left=8, right=2, top=2, bottom=2),
                        margin=ft.Margin(right=5, bottom=5)
                    )
                    date_chips.append(date_chip)

                selected_dates_container.content = ft.Column(
                    controls=[
                        ft.Text("已选择的日期:", size=12, color=colors["text_secondary"]),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=date_chips[i:i + 3],
                                        wrap=True
                                    ) for i in range(0, len(date_chips), 3)
                                ] if date_chips else [ft.Text("暂未选择", size=11, color=colors["text_secondary"])],
                                spacing=2
                            ),
                            height=80
                        )
                    ],
                    spacing=5
                )
            else:
                selected_dates_container.content = ft.Text(
                    "请在日历上点击选择日期",
                    size=12,
                    color=colors["text_secondary"]
                )
            page.update()

        def remove_date(date_str: str):
            """移除选中的日期"""
            if date_str in selected_dates:
                selected_dates.remove(date_str)
                update_selected_dates_display()
                update_picker_display()

        def change_picker_month(delta: int):
            """切换选择器的月份"""
            nonlocal picker_month, picker_year
            picker_month += delta
            if picker_month > 12:
                picker_month = 1
                picker_year += 1
            elif picker_month < 1:
                picker_month = 12
                picker_year -= 1
            update_picker_display()

        def confirm_custom_dates():
            """确认自定义日期选择"""
            if selected_dates:
                callback_func(selected_dates)
                page.pop_dialog()
            else:
                # 显示提示
                pass

        def cancel_custom_dates():
            """取消自定义日期选择"""
            page.pop_dialog()

        # 创建UI组件
        picker_title = ft.Text(
            f"{calendar.month_name[picker_month]} {picker_year}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=colors["text_primary"],
            text_align=ft.TextAlign.CENTER
        )

        picker_grid = ft.Column(spacing=2)

        selected_dates_container = ft.Container(
            content=ft.Text("请在日历上点击选择日期", size=12, color=colors["text_secondary"]),
            height=100
        )

        # 创建对话框
        custom_dates_dialog = ft.AlertDialog(
            title=ft.Text(
                "选择自定义日期",
                color=colors["text_primary"],
                weight=ft.FontWeight.BOLD
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        # 月份导航
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_LEFT,
                                    icon_size=20,
                                    on_click=lambda _: change_picker_month(-1)
                                ),
                                ft.Container(content=picker_title, expand=True, alignment=ft.Alignment.CENTER),
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_RIGHT,
                                    icon_size=20,
                                    on_click=lambda _: change_picker_month(1)
                                )
                            ]
                        ),
                        # 日期选择网格
                        picker_grid,
                        ft.Divider(),
                        # 已选日期显示
                        selected_dates_container
                    ],
                    spacing=10,
                    tight=True
                ),
                width=300,
                height=400
            ),
            actions=[
                ft.TextButton(
                    "取消",
                    on_click=cancel_custom_dates,
                    style=ft.ButtonStyle(color=colors["text_secondary"])
                ),
                ft.ElevatedButton(
                    "确定",
                    on_click=confirm_custom_dates,
                    style=ft.ButtonStyle(bgcolor=colors["custom_dates"], color="white")
                )
            ]
        )

        # 初始化显示
        update_picker_display()
        update_selected_dates_display()

        page.show_dialog(custom_dates_dialog)

    def show_custom_period_selector(callback_func) -> None:
        """显示自定义周期选择器：让用户设置个性化的重复周期"""

        # 间隔数字输入
        interval_field = ft.TextField(
            label="间隔数字",
            hint_text="输入数字，如 2",
            value="1",
            bgcolor=colors["background"],
            color=colors["text_primary"],
            border_color=colors["primary"],
            width=120,
            text_align=ft.TextAlign.CENTER
        )

        # 单位选择
        unit_dropdown = ft.Dropdown(
            label="时间单位",
            options=[
                ft.dropdown.Option("天"),
                ft.dropdown.Option("周"),
                ft.dropdown.Option("月"),
                ft.dropdown.Option("年"),
            ],
            value="月",
            bgcolor=colors["background"],
            color=colors["text_primary"],
            width=120
        )

        # 预览文本
        preview_text = ft.Text(
            "每1月",
            size=14,
            color=colors["text_primary"],
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER
        )

        def update_preview():
            """更新预览文本"""
            try:
                intervals = int(interval_field.value) if interval_field.value else 1
                units = unit_dropdown.value
                preview_text.value = f"每{intervals}{units}"
                page.update()
            except ValueError:
                preview_text.value = "请输入有效数字"
                page.update()

        # 绑定变化事件
        interval_field.on_change = lambda e: update_preview()
        unit_dropdown.on_change = lambda e: update_preview()

        def confirm_custom_period():
            """确认自定义周期设置"""
            try:
                intervals = int(interval_field.value) if interval_field.value else 1
                if intervals > 0:
                    callback_func(intervals, unit_dropdown.value)
                    page.pop_dialog()
                else:
                    # 显示错误提示
                    pass
            except ValueError:
                # 显示错误提示
                pass

        def cancel_custom_period():
            """取消自定义周期设置"""
            page.pop_dialog()

        # 优化快速选择按钮
        quick_options = [
            ("每2天", 2, "天"),
            ("每3天", 3, "天"),
            ("每2周", 2, "周"),
            ("每3周", 3, "周"),
            ("每2月", 2, "月"),
            ("每3月", 3, "月"),
            ("每半年", 6, "月"),
            ("每2年", 2, "年")
        ]

        quick_buttons = []
        for i in range(0, len(quick_options), 3):  # 改为每行3个按钮
            row_buttons = []
            for j in range(3):
                if i + j < len(quick_options):
                    text, interval, unit = quick_options[i + j]
                    btn = ft.ElevatedButton(
                        text,
                        on_click=lambda e, iv=interval, ut=unit: set_quick_option(iv, ut),
                        style=ft.ButtonStyle(
                            bgcolor=colors["surface"],
                            color=colors["text_primary"],
                            elevation=1
                        ),
                        width=90,  # 增加宽度
                        height=40  # 增加高度
                    )
                    row_buttons.append(btn)

            if row_buttons:
                quick_buttons.append(
                    ft.Row(
                        controls=row_buttons,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10  # 增加间距
                    )
                )

        def set_quick_option(intervals: int, units: str):
            """设置快速选项"""
            interval_field.value = str(intervals)
            unit_dropdown.value = units
            update_preview()

        custom_period_dialog = ft.AlertDialog(
            title=ft.Text(
                "设置自定义周期",
                color=colors["text_primary"],
                weight=ft.FontWeight.BOLD
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "请设置重复的间隔周期:",
                            color=colors["text_secondary"],
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=10),
                        ft.Row(
                            controls=[interval_field, unit_dropdown],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=15
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=preview_text,
                            bgcolor=colors["surface"],
                            padding=10,
                            border_radius=8,
                            alignment=ft.Alignment.CENTER
                        ),
                        ft.Container(height=15),
                        ft.Text(
                            "快速选择:",
                            color=colors["text_secondary"],
                            text_align=ft.TextAlign.CENTER
                        ),
                        *quick_buttons
                    ],
                    spacing=10,  # 增加间距
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True
                ),
                width=340,  # 增加宽度
                height=400  # 增加高度
            ),
            actions=[
                ft.TextButton(
                    "取消",
                    on_click=cancel_custom_period,
                    style=ft.ButtonStyle(color=colors["text_secondary"])
                ),
                ft.ElevatedButton(
                    "确定",
                    on_click=confirm_custom_period,
                    style=ft.ButtonStyle(bgcolor=colors["custom_period"], color="white")
                )
            ]
        )

        page.show_dialog(custom_period_dialog)

    def show_add_event_dialog() -> None:
        """显示添加事件对话框：增强版，支持自定义周期选项"""
        if not selected_day:
            def close_tip():
                page.pop_dialog()

            tip_dialog = ft.AlertDialog(
                title=ft.Text(
                    "提示",
                    color=colors["text_primary"],
                    weight=ft.FontWeight.BOLD
                ),
                content=ft.Text(
                    "请先点击日历上的日期，然后再添加事件哦~",
                    color=colors["text_secondary"]
                ),
                actions=[
                    ft.ElevatedButton(
                        "好的",
                        on_click=close_tip,
                        style=ft.ButtonStyle(
                            bgcolor=colors["primary"],
                            color="white"
                        )
                    )
                ]
            )
            page.show_dialog(tip_dialog)
            return

        # 基本信息字段
        title_field = ft.TextField(
            label="事件标题",
            hint_text="请输入事件标题",
            bgcolor=colors["background"],
            color=colors["text_primary"],
            border_color=colors["primary"]
        )

        category_dropdown = ft.Dropdown(
            label="事件类别",
            options=[
                ft.dropdown.Option("工作"),
                ft.dropdown.Option("日常"),
                ft.dropdown.Option("个人生活"),
                ft.dropdown.Option("自定义"),
            ],
            value="日常",
            bgcolor=colors["background"],
            color=colors["text_primary"],
            border_color=colors["primary"]
        )

        description_field = ft.TextField(
            label="事件描述（可选）",
            hint_text="添加一些详细描述...",
            multiline=True,
            min_lines=2,
            max_lines=4,
            bgcolor=colors["background"],
            color=colors["text_primary"],
            border_color=colors["primary"]
        )

        # 周期性事件选项
        is_periodic_checkbox = ft.Checkbox(
            label="设置为周期性事件",
            value=False,
            active_color=colors["primary"],
            on_change=lambda e: toggle_periodic_options(e.control.value)
        )

        # 扩展的周期选项，包含自定义选项
        period_dropdown = ft.Dropdown(
            label="重复周期",
            options=[
                ft.dropdown.Option("每天"),
                ft.dropdown.Option("每周"),
                ft.dropdown.Option("每月"),
                ft.dropdown.Option("每季"),
                ft.dropdown.Option("每年"),
                ft.dropdown.Option("自定义日期"),  # 新增：自定义日期选项
                ft.dropdown.Option("自定义周期"),  # 新增：自定义周期选项
            ],
            value="每月",
            bgcolor=colors["background"],
            color=colors["text_primary"],
            border_color=colors["primary"],
            visible=False,
            on_change=lambda e: handle_period_change(e.control.value)
        )

        # 周期信息显示
        periodic_info = ft.Text(
            "提示：周期性事件将在指定周期内的所有对应日期自动创建",
            size=12,
            color=colors["text_secondary"],
            visible=False
        )

        # 自定义配置按钮
        custom_config_button = ft.ElevatedButton(
            "配置自定义选项",
            on_click=lambda e: handle_custom_config(),
            style=ft.ButtonStyle(
                bgcolor=colors["accent"],
                color="white",
                elevation=1
            ),
            visible=False
        )

        # 自定义配置结果显示
        custom_result_text = ft.Text(
            "",
            size=12,
            color=colors["text_primary"],
            visible=False
        )

        # 存储自定义配置的数据
        custom_config_data = {}

        def toggle_periodic_options(is_periodic: bool):
            """切换周期性选项的显示状态"""
            period_dropdown.visible = is_periodic
            periodic_info.visible = is_periodic
            if not is_periodic:
                custom_config_button.visible = False
                custom_result_text.visible = False
            page.update()

        def handle_period_change(period_value: str):
            """处理周期选择变化"""
            if period_value in ["自定义日期", "自定义周期"]:
                custom_config_button.visible = True
                custom_result_text.visible = False
                # 更新提示文本
                if period_value == "自定义日期":
                    periodic_info.value = "选择特定的多个日期来重复事件"
                else:
                    periodic_info.value = "设置自定义的重复间隔，如每2周、每3个月等"
            else:
                custom_config_button.visible = False
                custom_result_text.visible = False
                periodic_info.value = "提示：周期性事件将在指定周期内的所有对应日期自动创建"

            # 清空之前的自定义配置
            custom_config_data.clear()
            page.update()

        def handle_custom_config():
            """处理自定义配置"""
            period_value = period_dropdown.value

            if period_value == "自定义日期":
                def on_custom_dates_selected(selected_dates):
                    """处理自定义日期选择结果"""
                    custom_config_data["custom_dates"] = selected_dates
                    # 显示选择结果
                    count = len(selected_dates)
                    custom_result_text.value = f"已选择 {count} 个日期"
                    custom_result_text.visible = True
                    page.update()

                show_custom_dates_selector(on_custom_dates_selected)

            elif period_value == "自定义周期":
                def on_custom_period_selected(interval, unit):
                    """处理自定义周期选择结果"""
                    custom_config_data["interval"] = interval
                    custom_config_data["unit"] = unit
                    # 显示选择结果
                    custom_result_text.value = f"设置为每{interval}{unit}"
                    custom_result_text.visible = True
                    page.update()

                show_custom_period_selector(on_custom_period_selected)

        def save_event():
            """保存事件：支持新的自定义周期类型"""
            if title_field.value and selected_day:
                if is_periodic_checkbox.value:
                    # 构建周期信息
                    period_type = period_dropdown.value
                    period_info = {"type": period_type}

                    if period_type == "自定义日期":
                        if "custom_dates" in custom_config_data:
                            period_info["custom_dates"] = custom_config_data["custom_dates"]
                        else:
                            # 提示用户先配置自定义选项
                            return
                    elif period_type == "自定义周期":
                        if "interval" in custom_config_data and "unit" in custom_config_data:
                            period_info["interval"] = custom_config_data["interval"]
                            period_info["unit"] = custom_config_data["unit"]
                        else:
                            # 提示用户先配置自定义选项
                            return

                    # 添加周期性事件
                    add_periodic_event(
                        selected_year,
                        selected_month,
                        selected_day,
                        title_field.value,
                        category_dropdown.value,
                        description_field.value or "",
                        period_info
                    )
                else:
                    # 添加普通事件
                    add_event(
                        selected_year,
                        selected_month,
                        selected_day,
                        title_field.value,
                        category_dropdown.value,
                        description_field.value or ""
                    )
                update_calendar()
                update_event_panel()
                page.pop_dialog()

        def cancel_dialog():
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text(
                f"为 {selected_year}年{selected_month}月{selected_day}日 添加事件",
                color=colors["text_primary"],
                weight=ft.FontWeight.BOLD
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        title_field,
                        category_dropdown,
                        description_field,
                        ft.Divider(color=colors["text_secondary"]),
                        is_periodic_checkbox,
                        period_dropdown,
                        periodic_info,
                        custom_config_button,
                        custom_result_text
                    ],
                    spacing=15,
                    tight=True
                ),
                width=480,
                height=480
            ),
            actions=[
                ft.TextButton(
                    "取消",
                    on_click=cancel_dialog,
                    style=ft.ButtonStyle(
                        color=colors["text_secondary"],
                        overlay_color=ft.Colors.with_opacity(0.1, colors["text_secondary"])
                    )
                ),
                ft.ElevatedButton(
                    "保存事件",
                    on_click=save_event,
                    style=ft.ButtonStyle(
                        bgcolor=colors["primary"],
                        color="white",
                        elevation=2
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        page.show_dialog(dialog)

    # 创建主标题，展现应用的优雅气质
    main_title = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "GOOSE'S CALENDAR",
                    size=36,
                    color=colors["primary"],
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Developed by yyh, with love and care",
                    size=14,
                    color=colors["text_secondary"],
                    text_align=ft.TextAlign.CENTER,
                    style=ft.TextStyle(letter_spacing=2)
                )
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment.CENTER,
        margin=ft.Margin(bottom=20)
    )

    # 创建月份标题
    month_title = ft.Text(
        f"{calendar.month_name[selected_month]} {selected_year}",
        size=28,
        weight=ft.FontWeight.BOLD,
        color=colors["text_primary"],
        text_align=ft.TextAlign.CENTER
    )

    # 创建导航控件
    nav_controls = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                icon_color=colors["primary"],
                icon_size=32,
                on_click=lambda _: change_month(-1),
                tooltip="上个月"
            ),
            ft.Container(
                content=month_title,
                expand=True,
                alignment=ft.Alignment.CENTER
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                icon_color=colors["primary"],
                icon_size=32,
                on_click=lambda _: change_month(1),
                tooltip="下个月"
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # 创建快速操作按钮
    quick_actions = ft.Row(
        controls=[
            ft.ElevatedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.TODAY, size=16),
                        ft.Text("今天")
                    ],
                    spacing=5
                ),
                on_click=lambda _: go_to_today(),
                style=ft.ButtonStyle(
                    bgcolor=colors["accent"],
                    color="white",
                    shape=ft.RoundedRectangleBorder(radius=20),
                    elevation=2
                )
            ),
            ft.ElevatedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_MONTH, size=16),
                        ft.Text("快速跳转")
                    ],
                    spacing=5
                ),
                on_click=lambda _: jump_to_date(),
                style=ft.ButtonStyle(
                    bgcolor=colors["warning"],
                    color="white",
                    shape=ft.RoundedRectangleBorder(radius=20),
                    elevation=2
                )
            ),
            ft.ElevatedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ADD, size=16),
                        ft.Text("添加事件")
                    ],
                    spacing=5
                ),
                on_click=lambda _: show_add_event_dialog(),
                style=ft.ButtonStyle(
                    bgcolor=colors["primary"],
                    color="white",
                    shape=ft.RoundedRectangleBorder(radius=20),
                    elevation=2
                )
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15
    )

    # 创建图例说明
    legend_items = [
        (colors["today"], "今天"),
        (colors["selected"], "选中"),
        (colors["holiday"], "节假日"),
        (colors["workday"], "调休"),
        (colors["weekend"], "周末"),
        (colors["weekday"], "工作日")
    ]

    legend_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor=color,
                            border_radius=4
                        ),
                        ft.Text(label, size=11, color=colors["text_secondary"])
                    ],
                    spacing=5
                )
            ) for color, label in legend_items
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15
    )

    # 创建日历容器
    calendar_container = ft.Container()
    calendar_container.content = create_month_view(selected_year, selected_month)

    # 创建事件面板
    selected_date_text = ft.Text(
        f"{selected_year}年{selected_month}月{selected_day}日",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=colors["text_primary"]
    )

    events_column = ft.Column(spacing=8)

    event_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("日期详情", size=16, weight=ft.FontWeight.BOLD, color=colors["text_primary"]),
                selected_date_text,
                ft.Divider(color=colors["text_secondary"]),
                events_column
            ],
            spacing=10
        ),
        padding=20,
        bgcolor=colors["background"],
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2)
        )
    )

    # 组装主布局
    main_content = ft.Column(
        controls=[
            main_title,
            nav_controls,
            ft.Container(height=10),
            quick_actions,
            ft.Container(height=10),
            legend_row,  # 添加图例
            ft.Container(height=15),
            ft.Row(
                controls=[
                    ft.Container(
                        content=calendar_container,
                        expand=2
                    ),
                    ft.Container(width=20),
                    ft.Container(
                        content=event_panel,
                        width=300
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0
    )

    # 添加到页面
    page.add(main_content)

    # 初始化事件面板
    update_event_panel()


# 启动应用
if __name__ == "__main__":
    ft.app(main)