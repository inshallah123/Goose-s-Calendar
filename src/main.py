import flet as ft
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import calendar
from lunarcalendar import Converter, Solar
from lunarcalendar.festival import festivals
from lunarcalendar.solarterm import solarterms
import chinese_calendar as cn_cal
import json
import os
import time

LUNAR_AVAILABLE = True
HOLIDAY_AVAILABLE = True


def main(page: ft.Page) -> None:
    page.title = "GOOSE'S CALENDAR Version 0.0"
    page.window.width = 1200  # 增加宽度以容纳搜索框
    page.window.height = 780
    page.padding = 15
    page.bgcolor = "#F8F6F4"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT

    # ===== UI配置字典 =====
    # 颜色配置
    colors: Dict[str, str] = {
        # 主色调
        "primary": "#004163",  # 主色调，用于标题、按钮等重要元素
        "primary_light": "#004163",  # 主色调浅色版本
        "secondary": "#FF6B9D",  # 次要色彩
        "accent": "#DCEAF0",  # 强调色，用于突出按钮等
        "warning": "#DCEAF0",  # 警告色，用于警告按钮
        "success": "#EBF1EA",  # 成功色

        # 文字颜色
        "text_primary": "#004163",  # 主要文字颜色
        "text_secondary": "#577299",  # 次要文字颜色
        "text_white": "#FFFFFF",  # 白色文字
        "text_black": "#004163",  # 黑色文字

        # 背景颜色
        "background": "#FFFFFF",  # 主背景色
        "surface": "#F8F9FA",  # 表面背景色，用于卡片等

        # 日历相关颜色
        "today": "#B7D8E7",  # 今天的背景色
        "selected": "#004163",  # 选中日期的边框色
        "weekend": "#DCEAF0",  # 周末背景色
        "weekday": "#F9F6F5",  # 工作日背景色
        "holiday": "#EBCDDA",  # 节假日背景色
        "workday": "#F9F6F5",  # 调休工作日背景色
        "prev_next_month": "#FFFFFF",  # 上下月日期的淡色背景

        # 事件类型颜色（使用原始设计的鲜明颜色）
        "event_work": "#7E79B8",  # 工作事件
        "event_daily": "#9DC666",  # 日常事件
        "event_personal": "#E997AF",  # 个人生活事件
        "event_custom": "#88CE9D",  # 自定义事件
        "event_periodic": "#FF6B35",  # 周期性事件
        "custom_dates": "#FF9FF3",  # 自定义日期
        "custom_period": "#54A0FF",  # 自定义周期

        # 农历和节气颜色
        "lunar": "#6A7C83",  # 农历文字颜色
        "solar_term": "#6A7C83",  # 节气文字颜色

        # 搜索相关颜色
        "search_background": "#FFFFFF",  # 搜索框背景
        "search_border": "#E3E8ED",  # 搜索框边框
        "search_focus": "#004163",  # 搜索框聚焦时的边框
        "search_suggestion": "#F8F9FA",  # 搜索建议背景
        "search_suggestion_hover": "#E8F0FE",  # 搜索建议悬停背景
        "search_highlight": "#FFE082",  # 搜索结果高亮

        # 阴影和透明效果
        "shadow_light": "#000000",  # 浅色阴影
        "overlay_light": "#000000",  # 浅色遮罩
    }

    button_config: Dict[str, Dict] = {
        "quick_action": {
            "bgcolor": "#3C6C90",  # 统一使用主色调
            "color": "#FFFFFF",
            "radius": 20,
            "elevation": 2,
            "icon_size": 16,  # 使用现有的sizes["icon_button"]
            "spacing": 5
        }
    }

    # 字体大小配置
    font_sizes: Dict[str, int] = {
        "title_main": 36,  # 主标题字体大小
        "title_month": 28,  # 月份标题字体大小
        "date_large": 22,  # 大号日期数字
        "date_medium": 18,  # 中号日期数字
        "header": 16,  # 标题文字
        "body": 14,  # 正文文字
        "caption": 12,  # 说明文字
        "small": 11,  # 小号文字
        "tiny": 10,  # 微型文字
        "mini": 9,  # 最小文字
        "micro": 8,  # 超小文字
    }

    # 尺寸配置（新增和完善）
    sizes: Dict[str, int] = {
        "date_container_width": 135,  # 日期容器宽度
        "date_container_height": 115,  # 日期容器高度
        "weekday_header_height": 40,  # 星期标题行高度
        "event_strip_height": 14,  # 事件条高度
        "event_more_height": 12,  # "更多事件"提示高度
        "icon_button": 16,  # 图标按钮大小
        "icon_nav": 32,  # 导航图标大小
        "event_panel_width": 300,  # 事件面板宽度

        # 新增的尺寸配置
        "picker_day_button": 35,  # 日期选择器按钮大小
        "picker_weekday_width": 35,  # 星期标题宽度
        "picker_weekday_height": 25,  # 星期标题高度
        "quick_button_width": 90,  # 快速选择按钮宽度
        "quick_button_height": 40,  # 快速选择按钮高度
        "legend_indicator": 16,  # 图例指示器大小
        "year_input_width": 120,  # 年份输入框宽度
        "month_dropdown_width": 180,  # 月份下拉框宽度
        "time_unit_dropdown_width": 120,  # 时间单位下拉框宽度
        "dialog_content_width": 480,  # 对话框内容宽度
        "dialog_content_height": 520,  # 对话框内容高度
        "picker_dialog_width": 300,  # 选择器对话框宽度
        "picker_dialog_height": 400,  # 选择器对话框高度
        "period_dialog_width": 340,  # 周期对话框宽度
        "period_dialog_height": 400,  # 周期对话框高度

        # 搜索相关尺寸配置
        "search_container_width": 320,  # 搜索容器宽度
        "search_input_height": 40,  # 搜索输入框高度
        "search_suggestion_height": 300,  # 搜索建议列表最大高度
        "search_suggestion_item_height": 60,  # 搜索建议项高度
        "search_icon_size": 18,  # 搜索图标大小
        "search_clear_icon_size": 16,  # 清除图标大小
    }

    # 创建缓存字典，用于存储已计算过的日期信息，避免重复计算
    lunar_info_cache: Dict[date, Tuple[str, str, str, str]] = {}
    holiday_info_cache: Dict[date, Tuple[bool, bool, str]] = {}

    # 农历相关数据
    chinese_numbers = ["初", "十", "廿", "三"]
    chinese_digits = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    chinese_months = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]

    # 新增：事件时间选项（每2小时一个时段）
    time_options = [
        "全天", "00:00-02:00", "02:00-04:00", "04:00-06:00", "06:00-08:00",
        "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00",
        "16:00-18:00", "18:00-20:00", "20:00-22:00", "22:00-24:00"
    ]

    # 双击检测相关变量
    last_click_time = 0
    last_clicked_day = None

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
        if current_date_obj in lunar_info_cache:
            return lunar_info_cache[current_date_obj]
        if not LUNAR_AVAILABLE:
            return "", "", "", ""
        try:
            solar = Solar(year, month, day)
            lunar = Converter.Solar2Lunar(solar)
            lunar_month_str = (("闰" if lunar.isleap else "") + chinese_months[lunar.month - 1] + "月")
            actual_lunar_day_name = get_lunar_day_name(lunar.day)
            display_text = lunar_month_str if lunar.day == 1 else actual_lunar_day_name
            all_events = festivals + solarterms
            today_festivals = [fest.get_lang('zh') for fest in all_events if fest(year) == current_date_obj]
            solar_term_keywords = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨', '立夏', '小满', '芒种', '夏至',
                                   '小暑', '大暑', '立秋', '处暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪',
                                   '大雪', '冬至']
            important_festivals = ['除夕', '春节', '元宵节', '龙抬头', '端午节', '七夕', '中元节', '中秋节', '重阳节',
                                   '腊八节']
            found_solar_term = next((fest_name for fest_name in today_festivals if fest_name in solar_term_keywords),
                                    "")
            found_major_festival = ""
            if not found_solar_term:
                found_major_festival = next(
                    (fest_name for fest_name in today_festivals if fest_name in important_festivals), "")
            other_festival = ""
            if not found_solar_term and not found_major_festival and today_festivals:
                other_festival = today_festivals[0]
            if found_solar_term:
                display_text = found_solar_term
            elif found_major_festival:
                display_text = found_major_festival
            elif other_festival:
                display_text = other_festival
            result = (lunar_month_str, display_text, found_solar_term,
                      lunar_month_str if lunar.day == 1 else actual_lunar_day_name)
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
    events_file = "events.json"  # 定义事件数据文件名

    def save_events() -> None:
        """将事件数据保存到用户目录下的 events.json 文件中。"""
        try:
            data_to_save = {
                "single_events": events_data,
                "periodic_rules": periodic_events_rules
            }
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            print(f"Events saved successfully to {events_file}.")
        except Exception as e:
            print(f"保存事件到文件时出错: {e}")

    def load_events() -> None:
        """从用户目录下的 events.json 文件中加载事件数据。"""
        nonlocal events_data, periodic_events_rules
        if os.path.exists(events_file):
            try:
                with open(events_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    events_data = data.get("single_events", {})
                    periodic_events_rules = data.get("periodic_rules", [])
                    print(f"Events loaded successfully from {events_file}.")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"读取事件文件时出错: {e}. 将使用空数据。")
                events_data = {}
                periodic_events_rules = []
        else:
            print(f"未找到事件文件 '{events_file}'。将为您创建一个新的。")
            events_data = {}
            periodic_events_rules = []
            save_events()

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
        """辅助函数：检查给定日期是否匹配周期性规则，支持end_date限制"""
        start_date_str = rule.get("original_date")
        if not start_date_str: return False

        target_date_key = target_date.strftime("%Y-%m-%d")
        if target_date_key in rule.get("excluded_dates", []):
            return False

        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError:
            return False

        # 检查结束日期限制（新增功能）
        end_date_str = rule.get("end_date")
        if end_date_str:
            try:
                end_date = date.fromisoformat(end_date_str)
                if target_date > end_date:
                    return False
            except ValueError:
                pass

        period_info = rule.get("period_info", {})
        period_type = period_info.get("type")
        if target_date < start_date: return False

        if period_type == "每天":
            return True
        elif period_type == "每周":
            return (target_date - start_date).days % 7 == 0
        elif period_type == "每月":
            if target_date.day == start_date.day: return True
            try:
                target_date.replace(day=start_date.day)
                return False
            except ValueError:
                return target_date.day == calendar.monthrange(target_date.year, target_date.month)[1]
        elif period_type == "每季":
            month_diff = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
            if month_diff >= 0 and month_diff % 3 == 0:
                if target_date.day == start_date.day:
                    return True
                last_day_of_target_month = calendar.monthrange(target_date.year, target_date.month)[1]
                if start_date.day > last_day_of_target_month and target_date.day == last_day_of_target_month:
                    return True
            return False
        elif period_type == "每年":
            if target_date.month == start_date.month and target_date.day == start_date.day:
                return True
            if start_date.month == 2 and start_date.day == 29 and not calendar.isleap(target_date.year):
                return target_date.month == 2 and target_date.day == 28
            return False
        elif period_type == "自定义周期":
            interval = period_info.get("interval", 1)
            unit = period_info.get("unit", "天")
            if unit == "天":
                return (target_date - start_date).days % interval == 0
        elif period_type == "自定义日期":
            return target_date_key in period_info.get("custom_dates", [])
        return False

    def get_events_for_date(year: int, month: int, day: int) -> List[Dict]:
        """获取指定日期的事件：组合普通事件和动态计算的周期性事件，按时间排序。"""
        date_key = get_date_key(year, month, day)
        target_date = date(year, month, day)
        events_for_date = events_data.get(date_key, []).copy()
        for rule in periodic_events_rules:
            if check_if_date_matches_rule(target_date, rule):
                events_for_date.append(rule)

        # 按事件时间排序：全天事件排在最前，其他按时间顺序
        def sort_key(event):
            event_time = event.get("event_time", "全天")
            if event_time == "全天":
                return "00:00"  # 全天事件排在最前
            return event_time.split("-")[0]  # 取开始时间进行排序

        events_for_date.sort(key=sort_key)
        return events_for_date

    def add_event(year: int, month: int, day: int, title: str, category: str, description: str = "",
                  event_time: str = "全天", is_periodic: bool = False, period_info: Dict = None) -> None:
        """添加单个普通事件，新增事件时间字段。"""
        date_key = get_date_key(year, month, day)
        if date_key not in events_data:
            events_data[date_key] = []
        event = {
            "title": title,
            "category": category,
            "description": description,
            "event_time": event_time,  # 新增字段
            "is_periodic": is_periodic,
            "period_info": period_info or {},
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        events_data[date_key].append(event)
        save_events()

    def add_periodic_event(year: int, month: int, day: int, title: str, category: str,
                           description: str, event_time: str, period_info: Dict) -> None:
        """添加周期性事件规则，新增事件时间字段。"""
        rule = {
            "title": title,
            "category": category,
            "description": description,
            "event_time": event_time,  # 新增字段
            "is_periodic": True,
            "period_info": period_info,
            "original_date": get_date_key(year, month, day),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "excluded_dates": []
        }
        periodic_events_rules.append(rule)
        save_events()

    def search_events(keyword: str) -> List[Dict]:
        """搜索事件：返回包含关键词的事件及其日期信息"""
        if not keyword.strip():
            return []

        keyword = keyword.lower()
        search_results = []

        # 搜索普通事件
        for date_key, events_list in events_data.items():
            for event in events_list:
                title = event.get("title", "").lower()
                description = event.get("description", "").lower()
                category = event.get("category", "").lower()

                if keyword in title or keyword in description or keyword in category:
                    year, month, day = date_key.split('-')
                    search_results.append({
                        "event": event,
                        "date": f"{int(year)}年{int(month)}月{int(day)}日",
                        "year": int(year),
                        "month": int(month),
                        "day": int(day),
                        "type": "normal"
                    })

        # 搜索周期性事件
        for rule in periodic_events_rules:
            title = rule.get("title", "").lower()
            description = rule.get("description", "").lower()
            category = rule.get("category", "").lower()

            if keyword in title or keyword in description or keyword in category:
                original_date = rule.get("original_date", "")
                if original_date:
                    year, month, day = original_date.split('-')
                    period_type = rule.get("period_info", {}).get("type", "")
                    search_results.append({
                        "event": rule,
                        "date": f"{int(year)}年{int(month)}月{int(day)}日 ({period_type})",
                        "year": int(year),
                        "month": int(month),
                        "day": int(day),
                        "type": "periodic"
                    })

        # 按日期排序
        search_results.sort(key=lambda x: (x["year"], x["month"], x["day"]))
        return search_results

    def get_prev_next_month_dates(year: int, month: int) -> Tuple[List[int], List[int]]:
        """获取上个月末尾和下个月开头的日期，用于填充日历空白"""
        cal = calendar.monthcalendar(year, month)
        prev_month_dates = []
        next_month_dates = []

        # 获取第一周的空白天数（上个月的日期）
        first_week = cal[0]
        empty_start = first_week.count(0)
        if empty_start > 0:
            if month == 1:
                prev_year, prev_month = year - 1, 12
            else:
                prev_year, prev_month = year, month - 1
            prev_month_last_day = calendar.monthrange(prev_year, prev_month)[1]
            prev_month_dates = list(range(prev_month_last_day - empty_start + 1, prev_month_last_day + 1))

        # 获取最后一周的空白天数（下个月的日期）
        last_week = cal[-1]
        empty_end = last_week.count(0)
        if empty_end > 0:
            next_month_dates = list(range(1, empty_end + 1))

        return prev_month_dates, next_month_dates

    def create_search_component() -> ft.Container:
        """创建优雅的搜索组件"""
        search_input = ft.TextField(
            hint_text="搜索事件...",
            width=sizes["search_container_width"] - 50,
            height=sizes["search_input_height"],
            bgcolor=colors["search_background"],
            color=colors["text_primary"],
            border_color=colors["search_border"],
            focused_border_color=colors["search_focus"],
            border_radius=20,
            content_padding=ft.Padding(left=15, right=15, top=10, bottom=10),
            text_size=font_sizes["body"],
            on_change=lambda e: handle_search_input_change(e.control.value)
        )

        search_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            icon_size=sizes["search_icon_size"],
            icon_color=colors["primary"],
            tooltip="搜索事件",
            on_click=lambda e: handle_search_submit()
        )

        clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=sizes["search_clear_icon_size"],
            icon_color=colors["text_secondary"],
            tooltip="清除搜索",
            on_click=lambda e: clear_search(),
            visible=False
        )

        suggestions_container = ft.Container(
            visible=False,
            bgcolor=colors["search_background"],
            border=ft.Border.all(1, colors["search_border"]),
            border_radius=12,
            padding=5,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, colors["shadow_light"]),
                offset=ft.Offset(0, 2)
            )
        )

        search_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[search_input, search_button, clear_button],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    suggestions_container
                ],
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=sizes["search_container_width"]
        )

        def handle_search_input_change(value: str):
            """处理搜索输入变化，显示实时建议"""
            clear_button.visible = bool(value.strip())

            if value.strip():
                results = search_events(value)
                if results:
                    create_search_suggestions(results[:5])  # 最多显示5个建议
                else:
                    suggestions_container.visible = False
            else:
                suggestions_container.visible = False
            page.update()

        def handle_search_submit():
            """处理搜索提交"""
            keyword = search_input.value
            if keyword.strip():
                show_search_results_dialog(keyword)

        def clear_search():
            """清除搜索"""
            search_input.value = ""
            clear_button.visible = False
            suggestions_container.visible = False
            page.update()

        # 在 create_search_suggestions 函数中添加辅助函数
        def create_search_suggestions(results: List[Dict]):
            """创建搜索建议列表"""

            # 添加这个辅助函数来解决闭包问题
            def create_suggestion_click_handler(result_data):
                """创建建议项点击处理函数的闭包"""
                return lambda e: jump_to_search_result(result_data)

            suggestions = []
            for result in results:
                suggestion_item = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                result["event"]["title"],
                                size=font_sizes["body"],
                                color=colors["text_primary"],
                                weight=ft.FontWeight.W_500,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(
                                result["date"],
                                size=font_sizes["caption"],
                                color=colors["text_secondary"]
                            )
                        ],
                        spacing=2
                    ),
                    padding=10,
                    # 修复：使用闭包函数而不是默认参数
                    on_click=create_suggestion_click_handler(result),
                    on_hover=lambda e: handle_suggestion_hover(e),
                    border_radius=8
                )
                suggestions.append(suggestion_item)

        def handle_suggestion_hover(e: ft.ControlEvent):
            """处理建议项悬停效果"""
            if e.data == "true":
                e.control.bgcolor = colors["search_suggestion_hover"]
            else:
                e.control.bgcolor = None
            e.control.update()

        def jump_to_search_result(result: Dict):
            """跳转到搜索结果对应的日期"""
            nonlocal selected_year, selected_month, selected_day
            selected_year = result["year"]
            selected_month = result["month"]
            selected_day = result["day"]

            # 清除搜索状态
            search_input.value = ""
            clear_button.visible = False
            suggestions_container.visible = False

            # 更新日历显示
            update_calendar()
            update_event_panel()

        def show_search_results_dialog(keyword: str):
            """显示搜索结果对话框"""
            results = search_events(keyword)

            if not results:
                # 无结果对话框
                no_results_dialog = ft.AlertDialog(
                    title=ft.Text("搜索结果", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
                    content=ft.Text(f"未找到包含{keyword}的事件", color = colors["text_secondary"]),
                actions = [
                    ft.ElevatedButton(
                        "好的",
                        on_click=lambda e: page.pop_dialog(),
                        style=ft.ButtonStyle(bgcolor=colors["primary"], color=colors["text_white"])
                    )
                ]
                )
                page.show_dialog(no_results_dialog)
                return

            def jump_to_result_and_close(input_data: Dict):
                """跳转到结果并关闭对话框"""
                jump_to_search_result(input_data)
                page.pop_dialog()

            def create_result_click_handler(result_data):
                """创建结果项点击处理函数的闭包"""
                return lambda e: jump_to_result_and_close(result_data)

            # 创建结果列表
            result_items = []
            for result in results:
                event = result["event"]

                # 安全地获取事件类别对应的颜色
                category_key = f"event_{event['category'].lower()}"
                category_bgcolor = colors.get(category_key, colors["text_secondary"])

                result_item = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            event["category"],
                                            size=font_sizes["tiny"],
                                            color=colors["text_white"],
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        bgcolor=category_bgcolor,
                                        padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                                        border_radius=8
                                    ),
                                    ft.Text(
                                        result["date"],
                                        size=font_sizes["caption"],
                                        color=colors["text_secondary"]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Text(
                                event["title"],
                                size=font_sizes["body"],
                                color=colors["text_primary"],
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Text(
                                event.get("description", ""),
                                size=font_sizes["caption"],
                                color=colors["text_secondary"],
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ) if event.get("description") else ft.Container()
                        ],
                        spacing=5
                    ),
                    padding=15,
                    bgcolor=colors["surface"],
                    border_radius=10,
                    margin=ft.Margin(bottom=8),
                    on_click=create_result_click_handler(result),  # 使用闭包函数
                    animate=ft.Animation(150),  # 添加点击动画
                    on_hover=lambda e: setattr(e.control, 'bgcolor',
                                               colors["search_suggestion_hover"] if e.data == "true"
                                               else colors["surface"]) or e.control.update()  # 悬停效果
                )
                result_items.append(result_item)

            # 搜索结果对话框
            results_dialog = ft.AlertDialog(
                title=ft.Text(f"搜索{keyword}的结果 ({len(results)}条)",
                color = colors["text_primary"], weight = ft.FontWeight.BOLD),
                content = ft.Container(
                    content=ft.Column(
                    controls=result_items,
                    spacing=5,
                    scroll=ft.ScrollMode.AUTO
                ),
                width=400,
                height=400
            ),
            actions = [
                ft.TextButton(
                    "关闭",
                    on_click=lambda e: page.pop_dialog(),
                    style=ft.ButtonStyle(color=colors["text_secondary"])
                )
            ]
            )
            page.show_dialog(results_dialog)

        return search_container

    def create_month_view(year: int, month: int) -> ft.Container:
        """创建月份视图：增大日期块，显示事件摘要，填充跨月日期"""
        cal = calendar.monthcalendar(year, month)
        weekday_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        # 创建星期标题行
        weekday_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(day, size=font_sizes["header"], color=colors["text_secondary"],
                                    text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_600),
                    width=sizes["date_container_width"], height=sizes["weekday_header_height"],
                    alignment=ft.Alignment.CENTER, bgcolor=colors["surface"], border_radius=8
                ) for day in weekday_labels
            ],
            alignment=ft.MainAxisAlignment.CENTER, spacing=3
        )

        date_rows: List[ft.Row] = []
        today: date = date.today()

        # 获取上下月的填充日期
        prev_month_dates, next_month_dates = get_prev_next_month_dates(year, month)
        next_month_index = 0  # 用于追踪下个月日期的索引

        for week_index, week in enumerate(cal):
            week_controls: List[ft.Container] = []
            for day_index, day in enumerate(week):
                if day == 0:
                    # 填充上个月或下个月的日期
                    if week_index == 0 and day_index < len(prev_month_dates):
                        # 第一周，填充上个月日期
                        fill_day = prev_month_dates[day_index]
                        if month == 1:
                            fill_year, fill_month = year - 1, 12
                        else:
                            fill_year, fill_month = year, month - 1

                        # 正确计算跨月日期的 is_today 和 is_selected 状态
                        is_today_cross = (
                                fill_year == today.year and fill_month == today.month and fill_day == today.day)
                        is_selected_cross = (
                                fill_year == selected_year and fill_month == selected_month and fill_day == selected_day)

                        day_container = create_date_container(fill_year, fill_month, fill_day, True, is_today_cross,
                                                              is_selected_cross)
                    elif next_month_index < len(next_month_dates):
                        # 最后一周，填充下个月日期 - 修复：使用正确的索引逻辑
                        fill_day = next_month_dates[next_month_index]
                        next_month_index += 1  # 递增索引

                        if month == 12:
                            fill_year, fill_month = year + 1, 1
                        else:
                            fill_year, fill_month = year, month + 1

                        # 正确计算跨月日期的 is_today 和 is_selected 状态
                        is_today_cross = (
                                fill_year == today.year and fill_month == today.month and fill_day == today.day)
                        is_selected_cross = (
                                fill_year == selected_year and fill_month == selected_month and fill_day == selected_day)

                        day_container = create_date_container(fill_year, fill_month, fill_day, True, is_today_cross,
                                                              is_selected_cross)
                    else:
                        # 如果没有更多跨月日期需要填充，创建空容器
                        day_container = ft.Container(width=sizes["date_container_width"],
                                                     height=sizes["date_container_height"])
                else:
                    # 当前月的日期
                    is_today = (year == today.year and month == today.month and day == today.day)
                    is_selected = (year == selected_year and month == selected_month and day == selected_day)
                    day_container = create_date_container(year, month, day, False, is_today, is_selected)

                week_controls.append(day_container)
            date_rows.append(ft.Row(controls=week_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=3))

        return ft.Container(
            content=ft.Column(
                controls=[weekday_row, ft.Container(height=10), *date_rows],
                spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20, bgcolor=colors["background"], border_radius=16,
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=15,
                                color=ft.Colors.with_opacity(0.1, colors["shadow_light"]),
                                offset=ft.Offset(0, 5))
        )

    def create_date_container(year: int, month: int, day: int, is_other_month: bool = False,
                              is_today: bool = False, is_selected: bool = False) -> ft.Container:
        """创建单个日期容器，支持条纹状事件摘要显示"""
        day_of_week = date(year, month, day).weekday()
        is_weekend = day_of_week >= 5
        day_events = get_events_for_date(year, month, day)
        has_events = len(day_events) > 0

        # 获取农历和节假日信息
        lunar_month, lunar_day_str, solar_term, _ = get_lunar_info(year, month, day)
        is_rest_day, is_makeup_workday, holiday_name = get_holiday_info(year, month, day)

        # 确定背景色
        bg_color = colors["weekday"]
        text_color = colors["text_black"]
        border_color = None
        border_width = 0

        if is_other_month:
            # 其他月份的日期使用淡色
            bg_color = colors["prev_next_month"]
            text_color = colors["text_secondary"]
        else:
            if is_makeup_workday:
                bg_color = colors["workday"]
            elif is_rest_day:
                bg_color = colors["holiday"]
            elif is_weekend:
                bg_color = colors["weekend"]

            if is_selected:
                border_color = colors["selected"]
                border_width = 4
            if is_today:
                bg_color = colors["today"]
                text_color = colors["text_primary"]

        # 构建日期内容 - 分为上下两部分
        top_section_controls = []
        bottom_section_controls = []

        # 上半部分：数字日期和农历信息
        date_size = font_sizes["date_medium"] if has_events else font_sizes["date_large"]
        top_section_controls.append(
            ft.Text(str(day), size=date_size, color=text_color,
                    text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
        )

        # 修复：农历或节假日信息显示逻辑 - 移除is_other_month限制
        display_str = ""
        if holiday_name:
            display_str = holiday_name[:4]
        elif lunar_day_str and not has_events:  # 有事件时隐藏农历
            display_str = lunar_day_str
        elif lunar_day_str and has_events:  # 有事件时显示简化农历
            if "月" in lunar_day_str:
                display_str = lunar_day_str[:2]  # 只显示"正月"等
            else:
                display_str = lunar_day_str[:2]  # 只显示"初一"等前两字

        if display_str:
            # 修复：优先使用配置字典中的颜色，节气时使用专门的节气颜色
            if solar_term:
                lunar_text_color = colors["solar_term"]
            elif is_other_month:
                lunar_text_color = colors["text_secondary"]  # 其他月份使用次要文字颜色
            else:
                lunar_text_color = colors["lunar"]  # 使用配置字典中的农历颜色

            lunar_size = font_sizes["micro"] if has_events else font_sizes["tiny"]
            top_section_controls.append(
                ft.Text(display_str, size=lunar_size, color=lunar_text_color,
                        text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_400)
            )

        # 创建上半部分容器
        top_sections = ft.Container(
            content=ft.Column(
                controls=top_section_controls, spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            height=45 if has_events else 80,  # 有事件时压缩上半部分
            alignment=ft.Alignment.CENTER
        )

        # 下半部分：事件摘要
        if has_events and not is_other_month:
            bottom_section_controls.append(create_event_summary(day_events))
            bottom_section = ft.Container(
                content=ft.Column(
                    controls=bottom_section_controls, spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                height=65,  # 为事件摘要预留空间
                alignment=ft.Alignment.TOP_CENTER,
                bgcolor=ft.Colors.with_opacity(0.05, colors["overlay_light"]),  # 轻微的背景色区分
                border_radius=ft.BorderRadius(0, 0, 8, 8)  # 只有下方圆角
            )
        elif has_events and is_other_month:
            # 其他月份有事件时只显示小圆点
            bottom_section_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(width=3, height=3, border_radius=1.5, bgcolor=text_color)
                            for _ in range(min(len(day_events), 3))
                        ],
                        spacing=1, alignment=ft.MainAxisAlignment.CENTER
                    ),
                    height=10
                )
            )
            bottom_section = ft.Container(
                content=ft.Column(controls=bottom_section_controls),
                height=15,
                alignment=ft.Alignment.CENTER
            )
        else:
            bottom_section = ft.Container(height=5)  # 保持统一高度

        # 组合上下两部分
        date_content = ft.Column(
            controls=[top_sections, bottom_section],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START
        )

        # 创建日期容器
        day_container = ft.Container(
            content=date_content, width=sizes["date_container_width"], height=sizes["date_container_height"],
            border_radius=12, bgcolor=bg_color,
            border=ft.Border.all(border_width, border_color) if border_color else None,
            alignment=ft.Alignment.CENTER, animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_click=lambda e, d=day, y=year, m=month: handle_date_click(d, y, m),
            on_hover=lambda e: handle_hover(e),
            animate_scale=ft.Animation(100)
        )

        return day_container

    def create_event_summary(events: List[Dict]) -> ft.Container:
        """创建事件摘要显示，醒目的条纹状UI"""
        event_strips = []

        # 限制显示的事件数量，避免超出日期格
        display_events = events[:4]  # 最多显示4条事件

        for i, event in enumerate(display_events):
            time_prefix = ""
            if event.get("event_time", "全天") != "全天":
                time_text = event["event_time"]
                if "-" in time_text:
                    time_prefix = time_text.split("-")[0] + " "

            title = event["title"]
            # 根据是否有时间前缀调整标题长度
            max_title_length = 4 if time_prefix else 6
            if len(title) > max_title_length:
                title = title[:max_title_length] + ".."

            event_text = f"{time_prefix}{title}"

            # 修正：使用colors字典中的事件颜色
            category_colors = {
                "工作": colors["event_work"],
                "日常": colors["event_daily"],
                "个人生活": colors["event_personal"],
                "自定义": colors["event_custom"],
                "周期性": colors["event_periodic"]
            }
            strip_color = category_colors.get(event["category"], colors["text_secondary"])

            # 创建条纹状事件条
            event_strip = ft.Container(
                content=ft.Text(
                    event_text,
                    size=font_sizes["mini"],  # 使用配置的字体大小
                    color=colors["text_white"],
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_600,  # 加粗字体
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                bgcolor=strip_color,
                border_radius=3,
                padding=ft.Padding(left=3, right=3, top=1, bottom=1),
                margin=ft.Margin(bottom=1),
                height=sizes["event_strip_height"],  # 使用配置的高度
                alignment=ft.Alignment.CENTER
            )
            event_strips.append(event_strip)

        # 如果还有更多事件，显示省略提示
        if len(events) > 4:
            more_strip = ft.Container(
                content=ft.Text(
                    f"+{len(events) - 4}更多",
                    size=font_sizes["micro"],
                    color=colors["text_secondary"],
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_500
                ),
                bgcolor=colors["surface"],
                border_radius=3,
                padding=ft.Padding(left=3, right=3, top=1, bottom=1),
                height=sizes["event_more_height"],
                alignment=ft.Alignment.CENTER
            )
            event_strips.append(more_strip)

        return ft.Container(
            content=ft.Column(
                controls=event_strips,
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.Padding(left=2, right=2, top=2, bottom=1),
            width=sizes["date_container_width"] - 5  # 修正：基于配置计算宽度，留出边距
        )

    def handle_hover(e: ft.ControlEvent) -> None:
        """处理悬停效果：让日期格子轻盈地响应"""
        if e.data == "true":
            e.control.scale = 1.05
            e.control.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, colors["shadow_light"]),
                offset=ft.Offset(0, 3)
            )
        else:
            e.control.scale = 1.0
            e.control.shadow = None
        e.control.update()

    def handle_date_click(day: int, year: int = None, month: int = None) -> None:
        """处理日期点击：支持单击选中和双击添加事件"""
        nonlocal selected_day, selected_year, selected_month, last_click_time, last_clicked_day

        # 如果点击的是其他月份的日期，需要切换月份
        if year != selected_year or month != selected_month:
            selected_year = year
            selected_month = month
            selected_day = day
            update_calendar()
            update_event_panel()
            return

        current_time = time.time()

        # 检测双击
        if (last_clicked_day == day and
                current_time - last_click_time < 0.5):  # 0.5秒内的重复点击视为双击
            # 双击，打开添加事件对话框
            show_add_event_dialog()
        else:
            # 单击，选中日期
            selected_day = day
            update_calendar()
            update_event_panel()

        last_click_time = current_time
        last_clicked_day = day

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
        """跳转到指定年月：快速导航功能，优化快速选择"""

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

        def quick_jump_to_year(target_year: int):
            """快速跳转到指定年份，无需确认"""
            nonlocal selected_year, selected_month, selected_day
            selected_year = target_year
            selected_day = None
            update_calendar()
            update_event_panel()
            page.pop_dialog()

        month_options = [
            ft.dropdown.Option(str(month), f"{month}月 ({calendar.month_name[month]})")
            for month in range(1, 13)
        ]

        year_input = ft.TextField(
            label="输入年份", value=str(selected_year), bgcolor=colors["background"],
            color=colors["text_primary"], border_color=colors["primary"], width=sizes["year_input_width"],
            text_align=ft.TextAlign.CENTER, on_change=on_year_change, hint_text="例如: 2024"
        )

        month_dropdown = ft.Dropdown(
            label="选择月份", options=month_options, value=str(selected_month),
            bgcolor=colors["background"], color=colors["text_primary"], width=sizes["month_dropdown_width"]
        )

        current_year = datetime.now().year
        range_hint = ft.Text(
            f"支持年份: {current_year - 40} - {current_year + 40}",
            size=font_sizes["caption"], color=colors["text_secondary"], text_align=ft.TextAlign.CENTER
        )

        error_text = ft.Text(
            "", size=font_sizes["caption"], color=colors["today"],
            text_align=ft.TextAlign.CENTER, visible=False
        )

        # 修改快速年份按钮，直接跳转
        quick_year_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "去年", on_click=lambda e: quick_jump_to_year(current_year - 1),
                    style=ft.ButtonStyle(bgcolor=colors["surface"], color=colors["text_primary"], elevation=1),
                    width=sizes["quick_button_width"], height=sizes["quick_button_height"]
                ),
                ft.ElevatedButton(
                    "今年", on_click=lambda e: quick_jump_to_year(current_year),
                    style=ft.ButtonStyle(bgcolor=colors["primary_light"], color=colors["text_white"], elevation=1),
                    width=sizes["quick_button_width"], height=sizes["quick_button_height"]
                ),
                ft.ElevatedButton(
                    "明年", on_click=lambda e: quick_jump_to_year(current_year + 1),
                    style=ft.ButtonStyle(bgcolor=colors["surface"], color=colors["text_primary"], elevation=1),
                    width=sizes["quick_button_width"], height=sizes["quick_button_height"]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER, spacing=10
        )

        jump_dialog = ft.AlertDialog(
            title=ft.Text("快速跳转", color=colors["text_primary"], weight=ft.FontWeight.BOLD,
                          text_align=ft.TextAlign.CENTER),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(controls=[year_input, month_dropdown], spacing=15,
                               alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=5), range_hint, error_text, ft.Container(height=10),
                        ft.Text("快速选择年份(直接跳转):", size=font_sizes["body"], color=colors["text_secondary"],
                                text_align=ft.TextAlign.CENTER),
                        quick_year_row
                    ],
                    spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True
                ),
                width=350
            ),
            actions=[
                ft.TextButton("取消", on_click=cancel_jump, style=ft.ButtonStyle(color=colors["text_secondary"],
                                                                                 overlay_color=ft.Colors.with_opacity(
                                                                                     0.1, colors["text_secondary"]))),
                ft.ElevatedButton("跳转", on_click=handle_jump,
                                  style=ft.ButtonStyle(bgcolor=colors["accent"], color=colors["text_white"],
                                                       elevation=2))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        page.show_dialog(jump_dialog)

    calendar_container = ft.Container()
    calendar_container.content = create_month_view(selected_year, selected_month)

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
            lunar_month, _, solar_term, actual_lunar_day = get_lunar_info(selected_year, selected_month, selected_day)
            is_holiday, is_makeup_workday, holiday_name = get_holiday_info(selected_year, selected_month, selected_day)

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
                        content=ft.Text("Amaze me with your day~\nDouble click to add event",
                                        size=font_sizes["body"], color=colors["text_secondary"],
                                        text_align=ft.TextAlign.CENTER),
                        alignment=ft.Alignment.CENTER, padding=20
                    )
                )
        page.update()

    def create_event_card(event: Dict, index: int) -> ft.Container:
        """创建事件卡片：美观地展示事件信息，包含时间信息和编辑功能"""
        # 修正：使用colors字典中的事件颜色
        category_colors = {
            "工作": colors["event_work"],
            "日常": colors["event_daily"],
            "个人生活": colors["event_personal"],
            "自定义": colors["event_custom"],
            "周期性": colors["event_periodic"],
            "自定义日期": colors["custom_dates"],
            "自定义周期": colors["custom_period"]
        }

        title_text = event["title"]
        if event.get("is_periodic", False):
            period_info = event.get("period_info", {})
            period_type = period_info.get("type", "")
            if period_type == "自定义周期":
                interval = period_info.get("interval", 1)
                unit = period_info.get("unit", "")
                title_text += f" (每{interval}{unit})"
            elif period_type == "自定义日期":
                title_text += " (自定义日期)"
            elif period_type:
                title_text += f" ({period_type})"

        display_category = event["category"]
        event_time = event.get("event_time", "全天")

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(display_category, size=font_sizes["tiny"],
                                                color=colors["text_white"], weight=ft.FontWeight.BOLD),
                                bgcolor=category_colors.get(display_category, colors["text_secondary"]),
                                padding=ft.Padding(left=8, right=8, top=2, bottom=2), border_radius=10
                            ),
                            ft.Container(
                                content=ft.Text(event_time, size=font_sizes["tiny"], color=colors["text_secondary"],
                                                weight=ft.FontWeight.W_500),
                                bgcolor=colors["surface"], padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                                border_radius=8
                            ),
                            # 新增：编辑和删除按钮组
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED, icon_size=sizes["icon_button"],
                                        icon_color=colors["accent"], tooltip="编辑事件",
                                        on_click=lambda e, idx=index: edit_event_dialog(idx),
                                        style=ft.ButtonStyle(
                                            overlay_color=ft.Colors.with_opacity(0.1, colors["accent"]))
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE, icon_size=sizes["icon_button"],
                                        icon_color=colors["text_secondary"], tooltip="删除事件",
                                        on_click=lambda e, idx=index: delete_event(idx),
                                        style=ft.ButtonStyle(
                                            overlay_color=ft.Colors.with_opacity(0.1, colors["text_secondary"]))
                                    )
                                ],
                                spacing=0
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Text(title_text, size=font_sizes["body"], color=colors["text_primary"],
                            weight=ft.FontWeight.W_500),
                    ft.Text(event.get("description", ""), size=font_sizes["caption"],
                            color=colors["text_secondary"]) if event.get("description") else ft.Container()
                ],
                spacing=5
            ),
            padding=12, bgcolor=colors["surface"], border_radius=8, margin=ft.Margin(bottom=8)
        )

    def delete_event(event_index: int) -> None:
        """删除事件：智能处理普通和周期性事件，新增"删除此后"选项"""
        if not selected_day: return
        all_events_for_day = get_events_for_date(selected_year, selected_month, selected_day)
        if event_index >= len(all_events_for_day):
            print("Error: Event index out of range.")
            return

        event_to_delete = all_events_for_day[event_index]
        date_key = get_date_key(selected_year, selected_month, selected_day)
        is_periodic = event_to_delete.get("is_periodic", False)

        if is_periodic:
            original_rule = None
            for rule in periodic_events_rules:
                if (rule.get("created_at") == event_to_delete.get("created_at") and
                        rule.get("title") == event_to_delete.get("title")):
                    original_rule = rule
                    break

            if not original_rule:
                print("Error: Could not find the original periodic rule to delete.")
                return

            def delete_single_occurrence():
                """仅删除当天的事件实例"""
                if "excluded_dates" not in original_rule:
                    original_rule["excluded_dates"] = []
                if date_key not in original_rule["excluded_dates"]:
                    original_rule["excluded_dates"].append(date_key)
                save_events()
                update_calendar()
                update_event_panel()
                page.pop_dialog()

            def delete_after_date():
                """删除此后的所有周期性事件（新功能）"""
                current_selected_date = date(selected_year, selected_month, selected_day)
                end_date = current_selected_date
                original_rule["end_date"] = end_date.strftime("%Y-%m-%d")

                # 同时将当前日期加入排除列表，确保当前日期也被删除
                if "excluded_dates" not in original_rule:
                    original_rule["excluded_dates"] = []
                if date_key not in original_rule["excluded_dates"]:
                    original_rule["excluded_dates"].append(date_key)

                save_events()
                update_calendar()
                update_event_panel()
                page.pop_dialog()

            def delete_entire_series():
                """删除整个周期性事件系列"""
                periodic_events_rules.remove(original_rule)
                save_events()
                update_calendar()
                update_event_panel()
                page.pop_dialog()

            def cancel_delete():
                page.pop_dialog()

            # 增强的周期性事件删除对话框，添加"删除此后"选项
            confirm_dialog = ft.AlertDialog(
                title=ft.Text("删除周期性事件", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(f"您想如何删除周期性事件「{event_to_delete['title']}」？",
                                    color=colors["text_primary"], size=font_sizes["body"]),
                            ft.Container(height=10),
                            ft.Text("• 仅删除今天：只删除当前日期的事件实例",
                                    color=colors["text_secondary"], size=font_sizes["caption"]),
                            ft.Text("• 删除此后：删除当前日期及之后的所有事件",
                                    color=colors["text_secondary"], size=font_sizes["caption"]),
                            ft.Text("• 删除整个系列：删除所有相关的周期性事件",
                                    color=colors["text_secondary"], size=font_sizes["caption"])
                        ],
                        spacing=5
                    ),
                    width=400
                ),
                actions=[
                    ft.TextButton("取消", on_click=cancel_delete,
                                  style=ft.ButtonStyle(color=colors["text_secondary"])),
                    ft.ElevatedButton("仅删除今天", on_click=delete_single_occurrence,
                                      style=ft.ButtonStyle(bgcolor=colors["warning"], color=colors["text_white"])),
                    ft.ElevatedButton("删除此后", on_click=delete_after_date,
                                      style=ft.ButtonStyle(bgcolor=colors["accent"], color=colors["text_white"])),
                    ft.ElevatedButton("删除整个系列", on_click=delete_entire_series,
                                      style=ft.ButtonStyle(bgcolor=colors["today"], color=colors["text_white"]))
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            page.show_dialog(confirm_dialog)
        else:
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
                                      style=ft.ButtonStyle(bgcolor=colors["today"], color=colors["text_white"]))
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            page.show_dialog(confirm_dialog)

    def show_custom_dates_selector(callback_func) -> None:
        """显示自定义日期选择器：让用户优雅地选择多个特定日期"""
        selected_dates = []
        picker_year = selected_year
        picker_month = selected_month

        def update_picker_display():
            cal = calendar.monthcalendar(picker_year, picker_month)
            picker_title.value = f"{calendar.month_name[picker_month]} {picker_year}"
            picker_grid.controls.clear()

            weekday_row = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(day, size=font_sizes["caption"], color=colors["text_secondary"],
                                        text_align=ft.TextAlign.CENTER),
                        width=sizes["picker_weekday_width"], height=sizes["picker_weekday_height"],
                        alignment=ft.Alignment.CENTER)
                    for day in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                ], spacing=2
            )
            picker_grid.controls.append(weekday_row)

            for week in cal:
                week_controls = []
                for day in week:
                    if day == 0:
                        week_controls.append(ft.Container(width=sizes["picker_day_button"],
                                                          height=sizes["picker_day_button"]))
                    else:
                        date_str = f"{picker_year}-{picker_month:02d}-{day:02d}"
                        is_selected = date_str in selected_dates
                        day_btn = ft.Container(
                            content=ft.Text(str(day), size=font_sizes["caption"],
                                            color=colors["text_white"] if is_selected else colors["text_primary"],
                                            text_align=ft.TextAlign.CENTER,
                                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL),
                            width=sizes["picker_day_button"], height=sizes["picker_day_button"],
                            border_radius=17,
                            bgcolor=colors["primary"] if is_selected else colors["surface"],
                            alignment=ft.Alignment.CENTER, on_click=lambda e, d=day: toggle_date_selection(d),
                            animate=ft.Animation(duration=150)
                        )
                        week_controls.append(day_btn)
                picker_grid.controls.append(ft.Row(controls=week_controls, spacing=2))
            page.update()

        def toggle_date_selection(day: int):
            date_str = f"{picker_year}-{picker_month:02d}-{day:02d}"
            if date_str in selected_dates:
                selected_dates.remove(date_str)
            else:
                selected_dates.append(date_str)
            update_selected_dates_display()
            update_picker_display()

        def update_selected_dates_display():
            if selected_dates:
                sorted_dates = sorted(selected_dates)
                date_chips = []
                for date_str in sorted_dates:
                    year, month, day = date_str.split('-')
                    date_chip = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{month}月{day}日", size=font_sizes["small"], color=colors["text_primary"]),
                                ft.IconButton(icon=ft.Icons.CLOSE, icon_size=font_sizes["caption"],
                                              icon_color=colors["text_secondary"],
                                              on_click=lambda e, ds=date_str: remove_date(ds))
                            ], spacing=2
                        ),
                        bgcolor=colors["surface"], border_radius=15,
                        padding=ft.Padding(left=8, right=2, top=2, bottom=2),
                        margin=ft.Margin(right=5, bottom=5)
                    )
                    date_chips.append(date_chip)

                selected_dates_container.content = ft.Column(
                    controls=[
                        ft.Text("已选择的日期:", size=font_sizes["caption"], color=colors["text_secondary"]),
                        ft.Container(
                            content=ft.Column(
                                controls=[ft.Row(controls=date_chips[i:i + 3], wrap=True) for i in
                                          range(0, len(date_chips), 3)] if date_chips else [
                                    ft.Text("暂未选择", size=font_sizes["small"], color=colors["text_secondary"])],
                                spacing=2
                            ), height=80
                        )
                    ], spacing=5
                )
            else:
                selected_dates_container.content = ft.Text("请在日历上点击选择日期", size=font_sizes["caption"],
                                                           color=colors["text_secondary"])
            page.update()

        def remove_date(date_str: str):
            if date_str in selected_dates:
                selected_dates.remove(date_str)
                update_selected_dates_display()
                update_picker_display()

        def change_picker_month(delta: int):
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
            if selected_dates:
                callback_func(selected_dates)
                page.pop_dialog()

        def cancel_custom_dates():
            page.pop_dialog()

        picker_title = ft.Text(f"{calendar.month_name[picker_month]} {picker_year}",
                               size=font_sizes["header"], weight=ft.FontWeight.BOLD,
                               color=colors["text_primary"], text_align=ft.TextAlign.CENTER)
        picker_grid = ft.Column(spacing=2)
        selected_dates_container = ft.Container(
            content=ft.Text("请在日历上点击选择日期", size=font_sizes["caption"],
                            color=colors["text_secondary"]), height=100)

        custom_dates_dialog = ft.AlertDialog(
            title=ft.Text("选择自定义日期", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_size=20,
                                          on_click=lambda _: change_picker_month(-1)),
                            ft.Container(content=picker_title, expand=True, alignment=ft.Alignment.CENTER),
                            ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_size=20,
                                          on_click=lambda _: change_picker_month(1))
                        ]),
                        picker_grid, ft.Divider(), selected_dates_container
                    ], spacing=10, tight=True
                ), width=sizes["picker_dialog_width"], height=sizes["picker_dialog_height"]
            ),
            actions=[
                ft.TextButton("取消", on_click=cancel_custom_dates,
                              style=ft.ButtonStyle(color=colors["text_secondary"])),
                ft.ElevatedButton("确定", on_click=confirm_custom_dates,
                                  style=ft.ButtonStyle(bgcolor=colors["custom_dates"], color=colors["text_white"]))
            ]
        )

        update_picker_display()
        update_selected_dates_display()
        page.show_dialog(custom_dates_dialog)

    def show_custom_period_selector(callback_func) -> None:
        """显示自定义周期选择器：让用户设置个性化的重复周期"""
        interval_field = ft.TextField(
            label="间隔数字", hint_text="输入数字，如 2", value="1", bgcolor=colors["background"],
            color=colors["text_primary"], border_color=colors["primary"], width=sizes["time_unit_dropdown_width"],
            text_align=ft.TextAlign.CENTER
        )
        unit_dropdown = ft.Dropdown(
            label="时间单位", options=[ft.dropdown.Option("天"), ft.dropdown.Option("周"),
                                       ft.dropdown.Option("月"), ft.dropdown.Option("年")],
            value="月", bgcolor=colors["background"], color=colors["text_primary"],
            width=sizes["time_unit_dropdown_width"]
        )
        preview_text = ft.Text("每1月", size=font_sizes["body"], color=colors["text_primary"],
                               weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER)

        def update_preview():
            try:
                intervals = int(interval_field.value) if interval_field.value else 1
                units = unit_dropdown.value
                preview_text.value = f"每{intervals}{units}"
                page.update()
            except ValueError:
                preview_text.value = "请输入有效数字"
                page.update()

        interval_field.on_change = lambda e: update_preview()
        unit_dropdown.on_change = lambda e: update_preview()

        def confirm_custom_period():
            try:
                intervals = int(interval_field.value) if interval_field.value else 1
                if intervals > 0:
                    callback_func(intervals, unit_dropdown.value)
                    page.pop_dialog()
            except ValueError:
                pass

        def cancel_custom_period():
            page.pop_dialog()

        quick_options = [
            ("每2天", 2, "天"), ("每3天", 3, "天"), ("每2周", 2, "周"),
            ("每3周", 3, "周"), ("每2月", 2, "月"), ("每3月", 3, "月"),
            ("每半年", 6, "月"), ("每2年", 2, "年")
        ]

        quick_buttons = []
        for i in range(0, len(quick_options), 3):
            row_buttons = []
            for j in range(3):
                if i + j < len(quick_options):
                    text, interval, unit = quick_options[i + j]
                    btn = ft.ElevatedButton(
                        text, on_click=lambda e, iv=interval, ut=unit: set_quick_option(iv, ut),
                        style=ft.ButtonStyle(bgcolor=colors["surface"], color=colors["text_primary"], elevation=1),
                        width=sizes["quick_button_width"], height=sizes["quick_button_height"]
                    )
                    row_buttons.append(btn)
            if row_buttons:
                quick_buttons.append(ft.Row(controls=row_buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=10))

        def set_quick_option(intervals: int, units: str):
            interval_field.value = str(intervals)
            unit_dropdown.value = units
            update_preview()

        custom_period_dialog = ft.AlertDialog(
            title=ft.Text("设置自定义周期", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("请设置重复的间隔周期:", color=colors["text_secondary"],
                                text_align=ft.TextAlign.CENTER),
                        ft.Container(height=10),
                        ft.Row(controls=[interval_field, unit_dropdown], alignment=ft.MainAxisAlignment.CENTER,
                               spacing=15),
                        ft.Container(height=10),
                        ft.Container(content=preview_text, bgcolor=colors["surface"], padding=10, border_radius=8,
                                     alignment=ft.Alignment.CENTER),
                        ft.Container(height=15),
                        ft.Text("快速选择:", color=colors["text_secondary"], text_align=ft.TextAlign.CENTER),
                        *quick_buttons
                    ],
                    spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True
                ),
                width=sizes["period_dialog_width"], height=sizes["period_dialog_height"]
            ),
            actions=[
                ft.TextButton("取消", on_click=cancel_custom_period,
                              style=ft.ButtonStyle(color=colors["text_secondary"])),
                ft.ElevatedButton("确定", on_click=confirm_custom_period,
                                  style=ft.ButtonStyle(bgcolor=colors["custom_period"], color=colors["text_white"]))
            ]
        )
        page.show_dialog(custom_period_dialog)

    def show_add_event_dialog() -> None:
        """显示添加事件对话框：增强版，支持事件时间选择"""
        if not selected_day:
            def close_tip():
                page.pop_dialog()

            tip_dialog = ft.AlertDialog(
                title=ft.Text("提示", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
                content=ft.Text("请先点击日历上的日期，然后再添加事件哦~", color=colors["text_secondary"]),
                actions=[ft.ElevatedButton("好的", on_click=close_tip,
                                           style=ft.ButtonStyle(bgcolor=colors["primary"], color=colors["text_white"]))]
            )
            page.show_dialog(tip_dialog)
            return

        title_field = ft.TextField(label="事件标题", hint_text="请输入事件标题", bgcolor=colors["background"],
                                   color=colors["text_primary"], border_color=colors["primary"])

        category_dropdown = ft.Dropdown(
            label="事件类别",
            options=[ft.dropdown.Option("工作"), ft.dropdown.Option("日常"), ft.dropdown.Option("个人生活"),
                     ft.dropdown.Option("自定义")],
            value="日常", bgcolor=colors["background"], color=colors["text_primary"], border_color=colors["primary"]
        )

        # 新增：事件时间选择
        time_dropdown = ft.Dropdown(
            label="事件时间",
            options=[ft.dropdown.Option(time_opt) for time_opt in time_options],
            value="全天", bgcolor=colors["background"], color=colors["text_primary"], border_color=colors["primary"]
        )

        description_field = ft.TextField(
            label="事件描述（可选）", hint_text="添加一些详细描述...", multiline=True, min_lines=2,
            max_lines=4, bgcolor=colors["background"], color=colors["text_primary"], border_color=colors["primary"]
        )

        is_periodic_checkbox = ft.Checkbox(label="设置为周期性事件", value=False, active_color=colors["primary"],
                                           on_change=lambda e: toggle_periodic_options(e.control.value))

        period_dropdown = ft.Dropdown(
            label="重复周期",
            options=[
                ft.dropdown.Option("每天"), ft.dropdown.Option("每周"), ft.dropdown.Option("每月"),
                ft.dropdown.Option("每季"), ft.dropdown.Option("每年"), ft.dropdown.Option("自定义日期"),
                ft.dropdown.Option("自定义周期"),
            ],
            value="每月", bgcolor=colors["background"], color=colors["text_primary"],
            border_color=colors["primary"], visible=False, on_change=lambda e: handle_period_change(e.control.value)
        )

        periodic_info = ft.Text("提示：周期性事件将在指定周期内的所有对应日期自动创建", size=font_sizes["caption"],
                                color=colors["text_secondary"], visible=False)

        custom_config_button = ft.ElevatedButton(
            "配置自定义选项", on_click=lambda e: handle_custom_config(),
            style=ft.ButtonStyle(bgcolor=colors["accent"], color=colors["text_white"], elevation=1), visible=False
        )

        custom_result_text = ft.Text("", size=font_sizes["caption"], color=colors["text_primary"], visible=False)
        custom_config_data = {}

        def toggle_periodic_options(is_periodic: bool):
            period_dropdown.visible = is_periodic
            periodic_info.visible = is_periodic
            if not is_periodic:
                custom_config_button.visible = False
                custom_result_text.visible = False
            page.update()

        def handle_period_change(period_value: str):
            if period_value in ["自定义日期", "自定义周期"]:
                custom_config_button.visible = True
                custom_result_text.visible = False
                if period_value == "自定义日期":
                    periodic_info.value = "选择特定的多个日期来重复事件"
                else:
                    periodic_info.value = "设置自定义的重复间隔，如每2周、每3个月等"
            else:
                custom_config_button.visible = False
                custom_result_text.visible = False
                periodic_info.value = "提示：周期性事件将在指定周期内的所有对应日期自动创建"
            custom_config_data.clear()
            page.update()

        def handle_custom_config():
            period_value = period_dropdown.value
            if period_value == "自定义日期":
                def on_custom_dates_selected(selected_dates):
                    custom_config_data["custom_dates"] = selected_dates
                    count = len(selected_dates)
                    custom_result_text.value = f"已选择 {count} 个日期"
                    custom_result_text.visible = True
                    page.update()

                show_custom_dates_selector(on_custom_dates_selected)
            elif period_value == "自定义周期":
                def on_custom_period_selected(interval, unit):
                    custom_config_data["interval"] = interval
                    custom_config_data["unit"] = unit
                    custom_result_text.value = f"设置为每{interval}{unit}"
                    custom_result_text.visible = True
                    page.update()

                show_custom_period_selector(on_custom_period_selected)

        def save_event():
            if title_field.value and selected_day:
                if is_periodic_checkbox.value:
                    period_type = period_dropdown.value
                    period_info = {"type": period_type}
                    if period_type == "自定义日期":
                        if "custom_dates" in custom_config_data:
                            period_info["custom_dates"] = custom_config_data["custom_dates"]
                        else:
                            return
                    elif period_type == "自定义周期":
                        if "interval" in custom_config_data and "unit" in custom_config_data:
                            period_info["interval"] = custom_config_data["interval"]
                            period_info["unit"] = custom_config_data["unit"]
                        else:
                            return
                    add_periodic_event(
                        selected_year, selected_month, selected_day,
                        title_field.value, category_dropdown.value,
                        description_field.value or "", time_dropdown.value, period_info
                    )
                else:
                    add_event(
                        selected_year, selected_month, selected_day,
                        title_field.value, category_dropdown.value,
                        description_field.value or "", time_dropdown.value
                    )
                update_calendar()
                update_event_panel()
                page.pop_dialog()

        def cancel_dialog():
            page.pop_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text(f"为 {selected_year}年{selected_month}月{selected_day}日 添加事件",
                          color=colors["text_primary"], weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        title_field, category_dropdown, time_dropdown, description_field,
                        ft.Divider(color=colors["text_secondary"]),
                        is_periodic_checkbox, period_dropdown, periodic_info,
                        custom_config_button, custom_result_text
                    ],
                    spacing=15, tight=True
                ),
                width=sizes["dialog_content_width"], height=sizes["dialog_content_height"]
            ),
            actions=[
                ft.TextButton("取消", on_click=cancel_dialog, style=ft.ButtonStyle(color=colors["text_secondary"],
                                                                                   overlay_color=ft.Colors.with_opacity(
                                                                                       0.1, colors["text_secondary"]))),
                ft.ElevatedButton("保存事件", on_click=save_event,
                                  style=ft.ButtonStyle(bgcolor=colors["primary"], color=colors["text_white"],
                                                       elevation=2))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        page.show_dialog(dialog)

    def edit_event_dialog(event_index: int) -> None:
        """显示编辑事件对话框"""
        if not selected_day: return

        all_events_for_day = get_events_for_date(selected_year, selected_month, selected_day)
        if event_index >= len(all_events_for_day):
            print("Error: Event index out of range.")
            return

        event_to_edit = all_events_for_day[event_index]
        is_periodic = event_to_edit.get("is_periodic", False)

        # 预填充表单数据
        title_field = ft.TextField(
            label="事件标题", hint_text="请输入事件标题",
            value=event_to_edit.get("title", ""),
            bgcolor=colors["background"], color=colors["text_primary"], border_color=colors["primary"]
        )

        category_dropdown = ft.Dropdown(
            label="事件类别",
            options=[ft.dropdown.Option("工作"), ft.dropdown.Option("日常"),
                     ft.dropdown.Option("个人生活"), ft.dropdown.Option("自定义")],
            value=event_to_edit.get("category", "日常"),
            bgcolor=colors["background"], color=colors["text_primary"], border_color=colors["primary"]
        )

        time_dropdown = ft.Dropdown(
            label="事件时间",
            options=[ft.dropdown.Option(time_opt) for time_opt in time_options],
            value=event_to_edit.get("event_time", "全天"),
            bgcolor=colors["background"], color=colors["text_primary"], border_color=colors["primary"]
        )

        description_field = ft.TextField(
            label="事件描述（可选）", hint_text="添加一些详细描述...",
            value=event_to_edit.get("description", ""),
            multiline=True, min_lines=2, max_lines=4,
            bgcolor=colors["background"], color=colors["text_primary"], border_color=colors["primary"]
        )

        # 如果是周期性事件，需要特殊处理
        if is_periodic:
            def edit_single_occurrence():
                """仅编辑单个事件实例"""
                if title_field.value:
                    # 先从周期性规则中排除当前日期
                    original_rule = None
                    for rule in periodic_events_rules:
                        if (rule.get("created_at") == event_to_edit.get("created_at") and
                                rule.get("title") == event_to_edit.get("title")):
                            original_rule = rule
                            break

                    if original_rule:
                        date_key = get_date_key(selected_year, selected_month, selected_day)
                        if "excluded_dates" not in original_rule:
                            original_rule["excluded_dates"] = []
                        if date_key not in original_rule["excluded_dates"]:
                            original_rule["excluded_dates"].append(date_key)

                    # 添加新的单独事件
                    add_event(
                        selected_year, selected_month, selected_day,
                        title_field.value, category_dropdown.value,
                        description_field.value or "", time_dropdown.value
                    )

                    save_events()
                    update_calendar()
                    update_event_panel()
                    page.pop_dialog()

            def edit_entire_series():
                """编辑整个周期性事件系列"""
                if title_field.value:
                    # 找到并编辑原始规则
                    for rule in periodic_events_rules:
                        if (rule.get("created_at") == event_to_edit.get("created_at") and
                                rule.get("title") == event_to_edit.get("title")):
                            rule["title"] = title_field.value
                            rule["category"] = category_dropdown.value
                            rule["description"] = description_field.value or ""
                            rule["event_time"] = time_dropdown.value
                            break

                    save_events()
                    update_calendar()
                    update_event_panel()
                    page.pop_dialog()

            def cancel_edit():
                page.pop_dialog()

            # 周期性事件编辑对话框
            edit_dialog = ft.AlertDialog(
                title=ft.Text(f"编辑周期性事件", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("请选择编辑范围:", color=colors["text_secondary"],
                                    size=font_sizes["body"], text_align=ft.TextAlign.CENTER),
                            ft.Container(height=10),
                            title_field, category_dropdown, time_dropdown, description_field,
                            ft.Container(height=10),
                            ft.Text("注意: 编辑单个实例会将其从周期性规则中分离",
                                    color=colors["text_secondary"], size=font_sizes["caption"])
                        ],
                        spacing=15, tight=True
                    ),
                    width=sizes["dialog_content_width"], height=sizes["dialog_content_height"]
                ),
                actions=[
                    ft.TextButton("取消", on_click=cancel_edit,
                                  style=ft.ButtonStyle(color=colors["text_secondary"])),
                    ft.ElevatedButton("仅编辑今天", on_click=edit_single_occurrence,
                                      style=ft.ButtonStyle(bgcolor=colors["warning"], color=colors["text_white"])),
                    ft.ElevatedButton("编辑整个系列", on_click=edit_entire_series,
                                      style=ft.ButtonStyle(bgcolor=colors["primary"], color=colors["text_white"]))
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            page.show_dialog(edit_dialog)

        else:
            # 普通事件编辑
            def save_edited_event():
                """保存编辑后的普通事件"""
                if title_field.value:
                    date_key = get_date_key(selected_year, selected_month, selected_day)
                    if date_key in events_data and event_to_edit in events_data[date_key]:
                        # 更新事件数据
                        event_to_edit["title"] = title_field.value
                        event_to_edit["category"] = category_dropdown.value
                        event_to_edit["description"] = description_field.value or ""
                        event_to_edit["event_time"] = time_dropdown.value

                        save_events()
                        update_calendar()
                        update_event_panel()
                    page.pop_dialog()

            def cancel_edit():
                page.pop_dialog()

            # 普通事件编辑对话框
            edit_dialog = ft.AlertDialog(
                title=ft.Text(f"编辑事件", color=colors["text_primary"], weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            title_field, category_dropdown, time_dropdown, description_field
                        ],
                        spacing=15, tight=True
                    ),
                    width=sizes["dialog_content_width"], height=400
                ),
                actions=[
                    ft.TextButton("取消", on_click=cancel_edit,
                                  style=ft.ButtonStyle(color=colors["text_secondary"])),
                    ft.ElevatedButton("保存修改", on_click=save_edited_event,
                                      style=ft.ButtonStyle(bgcolor=colors["accent"], color=colors["text_white"]))
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            page.show_dialog(edit_dialog)

    # ===== 主界面布局 =====
    main_title = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("GOOSE'S CALENDAR", size=font_sizes["title_main"], color=colors["primary"],
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.LEFT),
                ft.Text("Developed by yyh, advised by Goose, with love and care:)", size=font_sizes["tiny"],
                        color=colors["text_secondary"], text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(letter_spacing=2))
            ],
            spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment.TOP_LEFT, margin=ft.Margin(bottom=20)
    )

    month_title = ft.Text(f"{calendar.month_name[selected_month]} {selected_year}",
                          size=font_sizes["title_month"], weight=ft.FontWeight.BOLD,
                          color=colors["text_primary"], text_align=ft.TextAlign.CENTER)

    nav_controls = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=colors["primary"],
                          icon_size=sizes["icon_nav"], on_click=lambda _: change_month(-1), tooltip="上个月"),
            ft.Container(content=month_title, expand=True, alignment=ft.Alignment.CENTER),
            ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=colors["primary"],
                          icon_size=sizes["icon_nav"], on_click=lambda _: change_month(1), tooltip="下个月"),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # 创建统一样式的快速操作按钮
    def create_quick_action_button(icon, text, on_click_func):
        return ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=button_config["quick_action"]["icon_size"]),
                    ft.Text(text)
                ],
                spacing=button_config["quick_action"]["spacing"]
            ),
            on_click=on_click_func,
            style=ft.ButtonStyle(
                bgcolor=button_config["quick_action"]["bgcolor"],
                color=button_config["quick_action"]["color"],
                shape=ft.RoundedRectangleBorder(radius=button_config["quick_action"]["radius"]),
                elevation=button_config["quick_action"]["elevation"]
            )
        )

    quick_actions = ft.Row(
        controls=[
            create_quick_action_button(ft.Icons.TODAY, "今天", lambda _: go_to_today()),
            create_quick_action_button(ft.Icons.CALENDAR_MONTH, "快速跳转", lambda _: jump_to_date()),
            create_quick_action_button(ft.Icons.ADD, "添加事件", lambda _: show_add_event_dialog())
        ],
        alignment=ft.MainAxisAlignment.CENTER, spacing=15
    )

    # 创建搜索组件
    search_component = create_search_component()

    legend_items = [
        (colors["today"], "今天"),
        (colors["weekday"], "工作日"),
        (colors["weekend"], "周末"),
        (colors["holiday"], "节假日")
    ]
    legend_row = ft.Row(
        controls=[
            ft.Container(content=ft.Row(controls=[
                ft.Container(width=sizes["legend_indicator"], height=sizes["legend_indicator"],
                             bgcolor=color, border_radius=4),
                ft.Text(label, size=font_sizes["small"], color=colors["text_secondary"])
            ], spacing=5))
            for color, label in legend_items
        ],
        alignment=ft.MainAxisAlignment.CENTER, spacing=15
    )

    selected_date_text = ft.Text(f"{selected_year}年{selected_month}月{selected_day}日",
                                 size=font_sizes["header"], weight=ft.FontWeight.BOLD,
                                 color=colors["text_primary"])
    events_column = ft.Column(spacing=8)

    event_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("日期详情", size=font_sizes["header"], weight=ft.FontWeight.BOLD,
                        color=colors["text_primary"]),
                selected_date_text,
                ft.Divider(color=colors["text_secondary"]),
                events_column
            ],
            spacing=10
        ),
        padding=20, bgcolor=colors["background"], border_radius=12,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                            color=ft.Colors.with_opacity(0.1, colors["shadow_light"]),
                            offset=ft.Offset(0, 2))
    )

    # 创建顶部区域：标题和搜索框
    top_section = ft.Row(
        controls=[
            ft.Container(content=main_title, expand=True),
            ft.Container(content=search_component, alignment=ft.Alignment.TOP_RIGHT)
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    main_content = ft.Column(
        controls=[
            top_section,
            nav_controls,
            ft.Container(height=10),
            quick_actions,
            ft.Container(height=10),
            legend_row,
            ft.Container(height=15),
            ft.Row(
                controls=[
                    ft.Container(content=calendar_container, expand=2),
                    ft.Container(width=20),
                    ft.Container(content=event_panel, width=sizes["event_panel_width"])
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0
    )

    page.add(main_content)
    update_event_panel()


if __name__ == "__main__":
    ft.run(main)