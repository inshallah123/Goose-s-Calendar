# UI配置字典

# 颜色配置
colors: dict[str, str] = {
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

# 字体大小配置
font_sizes: dict[str, int] = {
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
sizes: dict[str, int] = {
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