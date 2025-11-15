from ctypes import *
import time
user32 = windll.user32  # 调用鼠标锁定功能所需库

#=====================================================================================================================================================================#
if starting:
    # 功能开关定义，True为开启，False为关闭
    mouselock = False  # 固定鼠标光标开关
    mouselock1 = True  # 固定鼠标光标相关开关
    
    Frontview_tracking = False  # 狗斗追逐视角模式开关
    Rearview_tracking = False  # 狗斗追逐视角模式反转x轴
    Tracking_revjoyaxisx = True  # 狗斗追逐视角模式取消x轴自动回中增稳
    
    # 轴开关
    vjoyaxis = True  # 轴开关
    vjoyaxis_x = True  # x轴开关
    vjoyaxis_y = True  # y轴开关
    
    th_vjoyaxis = True  # 滚轮油门轴开关
    th_vjoyaxisL = True  # 左油门轴开关
    th_vjoyaxisR = True  # 右油门轴开关
    th_vjoyaxisrz = True  # 滚轮油门轴开关
    AB_throttle = False  # 油门加力开关
    
    Re_vjoyaxisx = True  # 滚转轴自动归中开关
    Re_vjoyaxisy = True  # 俯仰轴自动归中开关
    
    # 映射vJoy设备号
    v = vJoy[0]
    v1 = vJoy[1]  # 视角缩放控制设备
    # vjoy最大轴行程
    a_max = 8 + v.axisMax
    a_min = -8 - v.axisMax
    
    # 配平定义
    Trimp_centerX = 0
    Trimp_centerY = 0
    Trimp_centerZ = 0
    # 视角重定位 代码实现同配平
    View_Trimp_centerX = 0
    View_Trimp_centerY = 0
    View_Trimp_centerZ = 0
    
    # 鼠标轴定义
    vjoyaxisX = 0
    vjoyaxisY = 0
    
    th_axisR = a_min  # 右油门初始值
    th_axisL = a_min  # 左油门初始值
    th_axisrz = a_max  # 油混初始值
    
    center_redurz = 1
    center_redux = 1
    center_reduy = 1
    # 键盘脚舵刹车轴定义
    rud_axis = 0
    br_axisL = a_min  # 左刹车初始值
    br_axisR = a_min  # 右刹车初始值
    # 视角轴定义
    view_vjoyaxis = True  # 轴开关
    view_vjoyaxis_y = True  # y轴开关
    view_vjoyaxisX = 0
    view_vjoyaxisY = 0
    view_Trimp_centerX = 0
    view_Trimp_centerY = 0
    view_center_redux = 1
    view_center_reduy = 1
    view_vx_max = 0
    view_vx_min = 0
    view_vy_min = 0
    view_vy_max = 0
    # 一些其他定义
    vx_max = 0
    vx_min = 0
    vy_min = 0
    vy_max = 0
    m_redu0x = 0  # x轴曲率相关
    m_redu0y = 0  # y轴曲率相关
    
    # 直升机模式开关
    helicopter = False  # 旋翼机模式切换开关
    propeller = False

    # 鼠标动态速度补偿参数
    last_mouse_deltaX = 0  # 上一帧X轴鼠标位移
    last_mouse_deltaY = 0  # 上一帧Y轴鼠标位移
    # 摇杆动态补偿参数（独立）
    stick_max_speed_multi = 1.3  # 摇杆最大速度倍率（1.0~1.5）
    stick_speed_sens = 8         # 摇杆速度敏感度
    # 视角动态补偿参数（独立）
    view_max_speed_multi = 1.2   # 视角最大速度倍率（1.0~1.5）
    view_speed_sens = 10         # 视角速度敏感度

    # 视角缩放核心参数
    zoom_max_travel = 16390  # 缩放轴最大行程
    zoom_levels = [
        zoom_max_travel,    # 0: 最小缩放（缩小）
        13000,              # 1: 正常视角
        0,                  # 2: 轴中心位置
        -zoom_max_travel // 2,  # 3: 中度放大
        -zoom_max_travel    # 4: 最大放大
    ]
    current_zoom_level = 1        # 默认正常视角
    temp_zoom_level = None        # 长按临时保存的档位
    alt_zoom_cache = None         # 缓存Alt+滚轮的精细值
    zoom_axis = zoom_levels[current_zoom_level]  # 当前缩放轴值
    last_alt_zoom_value = zoom_levels[current_zoom_level]  # Alt+滚轮缩放值
    smooth_factor = 0.15          # 平滑过渡系数
    click_threshold = 200         # 单击/长按判定阈值(毫秒)
    zoom_in_press_time = 0        # 放大键时间戳
    zoom_out_press_time = 0       # 缩小键时间戳
    is_click_handled = False      # 单击事件处理标记
    is_alt_zoom_active = False    # Alt+滚轮激活状态
    fine_zoom_step = zoom_max_travel // 50  # Alt+滚轮精细步长

    # 新增：缩放等级对应的视角灵敏度倍率（核心新增参数）
    # 等级0-4：缩放越大（视角越近），倍率越小（移动越慢）
    zoom_sens_multipliers = [1.0, 0.8, 0.5, 0.3, 0.15]
    # 用于Alt+滚轮精细缩放时的动态倍率计算
    current_zoom_sens_multi = zoom_sens_multipliers[current_zoom_level]
    
    # fire_enabled = True  # 初始默认开启开火
    # alt_c_last_press = 0  # 记录Alt+C最后一次按下的时间（用于防抖）
    # alt_c_press_interval = 300  # 按键防抖间隔（毫秒，避免一次按下被多次识别）
#======================================================================================================================================================================================#    
#==========================================================================灵敏度设置（核心分离优化）=====================================================================================#
x, y = 1720, 720  # 固定鼠标光标在屏幕上的像素坐标(x, y)

# 1. 全局总灵敏度（影响所有鼠标控制，作为基础倍率）
global_sens = 1.0  # 全局总倍率（0.8=降低20%，1.2=提高20%）

# 2. 摇杆控制灵敏度（鼠标控制滚转/俯仰，独立调节）
stick_base_sens = 1.8  # 摇杆基础灵敏度（原m_sens）
stick_vx_sens = 0.9     # 摇杆X轴（滚转）独立灵敏度
stick_vy_sens = 0.9     # 摇杆Y轴（俯仰）独立灵敏度

# 3. 视角控制灵敏度（鼠标控制视角，完全独立调节）
view_base_sens = 30.0   # 视角基础灵敏度（与摇杆分离）
view_vx_sens = 0.8      # 视角X轴（水平）独立灵敏度
view_vy_sens = 0.8      # 视角Y轴（垂直）独立灵敏度

#4. 键盘控制摇杆灵敏度
key_stick_base_sens = 6.0  #键盘原灵敏度度
key_stick_vx_sens = 0.9   #摇杆键盘控制 X轴灵敏度
key_stick_vy_sens = 0.9   #摇杆键盘控制 Y轴灵敏度

# 新增：油门独立灵敏度参数（与摇杆、视角完全分离）
throttle_base_sens = 8.0  # 油门基础灵敏度（替代原stick_base_sens的作用）

# 其他参数
key_sens = 300  # 键盘灵敏度
view_max_angle = 0.6 * a_max  # 视角最大范围
view_min_angle = 0.6 * a_min  # 视角最小范围

m_reduz = 0  # 中心缩减（键盘脚舵曲率）
m_redux = 2  # 中心缩减（摇杆x轴曲率）
m_reduy = 2  # 中心缩减（摇杆y轴曲率）

view_m_reduz = 0
view_m_redux = 0
view_m_reduy = 0
m_reduViewtrackingx = -0.5  # 追逐视角模式的x轴曲率
m_reduViewtrackingy = -0.4  # 追逐视角模式的y轴曲率

# 狗斗追逐模式灵敏度（独立）
stick_vx_sensFront = 1.66  # 前视追逐视角X轴灵敏度
stick_vy_sensFront = 1.2   # 前视追逐视角Y轴灵敏度
stick_vx_sensRear = 11.0   # 后视追逐视角X轴灵敏度
stick_vy_sensRear = 3.0    # 后视追逐视角Y轴灵敏度

# 油门灵敏度参数
th_sensm = 1.275  # 油门轴1、2灵敏度
th_sensn = 0.125  # 油门轴微调灵敏度
th_sensrz = 0.5   # 油混灵敏度
th_sensh = 0.5    # 直升机总矩灵敏度
th_sensprop = 0.5  # 螺旋桨油门灵敏度

ABth_postion = 0.7  # 加力位置
IDth_postion = 0    # 怠速位置

rud_inc = 150  # 键盘脚舵灵敏度
rudreturn_sens = 400  # 脚舵回复速率

br_inc = 1500  # 刹车增加速率
br_dnc = 400   # 刹车回复速率


current_time = time.time() * 1000  # 毫秒级时间戳

#======================================================================== 开关键盘按键映射设置 ===============================================================================#
toggle_mouselock = False  # 关闭鼠标固定
key_rudderRight = keyboard.getKeyDown(Key.D)  # 右蹬舵
key_rudderLeft = keyboard.getKeyDown(Key.A)   # 左蹬舵
key_centerrud = keyboard.getKeyDown(Key.A) & keyboard.getKeyDown(Key.D)  # 左右同时蹬舵归中
key_TrimprudR = keyboard.getKeyDown(Key.D) & keyboard.getKeyDown(Key.LeftControl)  # 蹬舵向右配平
key_TrimprudL = keyboard.getKeyDown(Key.A) & keyboard.getKeyDown(Key.LeftControl)  # 蹬舵向左配平
key_TrimprudZero = keyboard.getKeyDown(Key.D) & keyboard.getKeyDown(Key.A) & keyboard.getKeyDown(Key.LeftControl)  # 蹬舵配平归中

key_vjoyaxisX_left = keyboard.getKeyDown(Key.Q) & keyboard.getKeyDown(Key.LeftControl)  # 摇杆左配平
key_vjoyaxisX_right = keyboard.getKeyDown(Key.E) & keyboard.getKeyDown(Key.LeftControl)  # 摇杆右配平
key_vjoyaxisY_front = keyboard.getKeyDown(Key.W) & keyboard.getKeyDown(Key.LeftControl)  # 摇杆向前配平
key_vjoyaxisY_behind = keyboard.getKeyDown(Key.S) & keyboard.getKeyDown(Key.LeftControl)  # 摇杆向后配平

key_Button_LeftCtrl = keyboard.getKeyDown(Key.LeftControl)

key_thidle = keyboard.getKeyDown(Key.Insert)  # 滚轮总矩卡位解锁
key_throttleL = keyboard.getKeyDown(Key.LeftArrow)  # 左油门单独控制
key_throttleR = keyboard.getKeyDown(Key.RightArrow)  # 右油门单独控制
key_throttlerz = keyboard.getKeyDown(Key.LeftArrow) & keyboard.getKeyDown(Key.RightArrow)  # 油混控制
key_throttle = keyboard.getKeyDown(Key.LeftArrow) | keyboard.getKeyDown(Key.RightArrow)

Key_ForceTrimp = keyboard.getKeyDown(Key.T)  # 杆力配平
Key_Trimpcenter = keyboard.getKeyDown(Key.LeftControl) & keyboard.getKeyDown(Key.C)  # 配平复位

key_helicopter = keyboard.getKeyDown(Key.NumberLock)  # 直升机模式切换
key_propeller = keyboard.getKeyDown(Key.Delete)  # 螺旋桨模式切换

# key_Button1 = keyboard.getKeyDown(Key.Space)  # 武器开火
key_Button1 = mouse.getButton(0) #武器开火，鼠标左键
key_Button2 = keyboard.getKeyDown(Key.Space) & keyboard.getKeyDown(Key.RightAlt)  # 武器释放

key_vjoyaxisX = keyboard.getKeyDown(Key.Q) | keyboard.getKeyDown(Key.E)  # 键盘控制滚转
key_vjoyaxisY = keyboard.getKeyDown(Key.C) | keyboard.getKeyDown(Key.LeftShift)  # 键盘控制俯仰

key_throttle_key = keyboard.getKeyDown(Key.W) | keyboard.getKeyDown(Key.S)  # 键盘控制总距

key_ButtonC = keyboard.getKeyDown(Key.C)
key_ButtonLeftShift = keyboard.getKeyDown(Key.LeftShift)
key_ButtonQ = keyboard.getKeyDown(Key.Q)
key_ButtonE = keyboard.getKeyDown(Key.E)

key_ButtonW = keyboard.getKeyDown(Key.W)
key_ButtonS = keyboard.getKeyDown(Key.S)

# 视角缩放控制按键
key_zoom_in = mouse.getButton(3)    # 放大键（侧键前）
key_zoom_out = mouse.getButton(4)   # 缩小键（侧键后）
key_zoom_reset = mouse.getButton(2) # 鼠标中键（重置视角）
key_alt = keyboard.getKeyDown(Key.LeftAlt)  # Alt键状态

#======================================================================================================================================================================================#
#======================================================================== 鼠标按键映射设置 ===============================================================================#
key_vjoyaxis = not keyboard.getKeyDown(Key.LeftAlt)  # 默认开启摇杆控制（左Alt切换视角）
Key_Frontviewtracking = False  # 追逐视角模式开关
Key_Rearviewtracking = False   # 后视追逐模式开关

key_Button3 = False
key_Button4 = False
key_Button5 = False
key_Button6 = False
key_Button7 = False

key_view_vjoyaxis = keyboard.getKeyDown(Key.LeftAlt)  # 左Alt开启视角控制
Key_view_Trimp = mouse.getButton(2) & keyboard.getKeyDown(Key.LeftAlt)  # 视角重居中
Key_view_Trimpcenter = keyboard.getKeyDown(Key.RightAlt) & keyboard.getKeyDown(Key.T)  # 视角配平复位

# if keyboard.getKeyDown(Key.LeftAlt) and keyboard.getKeyDown(Key.C):
#     # 检查是否超过防抖间隔（避免短时间内重复触发）
#     if current_time - alt_c_last_press > alt_c_press_interval:
#         fire_enabled = not fire_enabled  # 翻转状态（开→关 或 关→开）
#         alt_c_last_press = current_time  # 更新最后按下时间
#         # 可选：输出状态提示（调试用）
#         # if fire_enabled:
#         #     print("开火已开启")
#         # else:
#         #     print("开火已关闭")

#======================================================================================================================================================================================#
#======================================================================== 开启轴命令/模式 ==================================================================================#
if key_vjoyaxis:  # 开启摇杆、油门映射
    vjoyaxis = True
    th_vjoyaxis = True
else:  # 关闭摇杆、油门映射
    vjoyaxis = False

# 视角控制开关
if key_view_vjoyaxis:
    view_vjoyaxis = True
else:
    view_vjoyaxis = False

if Key_Frontviewtracking:  # 追逐视角模式
    if (not helicopter):
        Frontview_tracking = True
        Re_vjoyaxisx = False
        m_redu0x = m_reduViewtrackingx
        m_redu0y = m_reduViewtrackingy
        mouselock1 = False
        if Key_Rearviewtracking:
            if (not vjoyaxis):
                Rearview_tracking = True
                vjoyaxis = True
        else:
            Rearview_tracking = False
    if not vjoyaxis:
        th_vjoyaxis = False
else:
    th_vjoyaxis = True
    Frontview_tracking = False
    m_redu0x = m_redux
    m_redu0y = m_reduy
    mouselock1 = True
    Re_vjoyaxisx = True

if key_propeller:  # 螺旋桨模式切换
    propeller = not propeller
    
if key_helicopter:  # 直升机模式切换
    helicopter = not helicopter
    Re_vjoyaxisx = not Re_vjoyaxisx

if (helicopter):  # 直升机配平
    th_sens = th_sensh    
    if Key_ForceTrimp | key_Button4:
        Trimp_centerX = vjoyaxisX
        Trimp_centerY = vjoyaxisY
    if Key_Trimpcenter | key_Button5:
        Trimp_centerX = 0
        if vjoyaxisX != Trimp_centerX * 0.1:
            vjoyaxisX -= (vjoyaxisX - Trimp_centerX) * 0.1 
        Trimp_centerY = 0
    if key_rudderLeft | key_rudderRight:
        Trimp_centerZ = rud_axis 
    if key_rudderLeft & key_rudderRight:
        Trimp_centerZ = 0    
    
# 摇杆不移动时回中
if(not key_vjoyaxisX):
    if vjoyaxisX >= vx_max : 
        vx_max = vjoyaxisX
    if vjoyaxisX <= vx_min: 
        vx_min = vjoyaxisX
    if mouse.deltaX ==0 :
        if vjoyaxisX > Trimp_centerX:
            vjoyaxisX -= (vjoyaxisX - Trimp_centerX) * 0.3
            vx_max -= (vjoyaxisX - Trimp_centerX) * 0.3
        if vjoyaxisX < Trimp_centerX:
            vjoyaxisX -= (vjoyaxisX - Trimp_centerX) * 0.3
            vx_min -= (vjoyaxisX - Trimp_centerX) * 0.3

# 摇杆不移动时回中
if(not key_vjoyaxisY):
    if vjoyaxisY >= vy_max:
        vy_max = vjoyaxisY
    if vjoyaxisY <= vy_min :
        vy_min = vjoyaxisY
    if mouse.deltaY == 0: 
        if vjoyaxisY > Trimp_centerY:
            vjoyaxisY -= (vjoyaxisY - Trimp_centerY) * 0.3
            vy_max -= (vjoyaxisY - Trimp_centerY) * 0.3
        if vjoyaxisY < Trimp_centerY:
            vjoyaxisY -= (vjoyaxisY - Trimp_centerY) * 0.3
            vy_min -= (vjoyaxisY - Trimp_centerY) * 0.3

# 键盘控制
if(key_vjoyaxisX & (not key_Button_LeftCtrl)):
    if(key_ButtonE):
        if m_redu0x > 0:
            vjoyaxisX += (key_sens * key_stick_vx_sens * key_stick_base_sens * 0.48 * global_sens) / center_redux
        else:
            vjoyaxisX += (key_sens * key_stick_vx_sens * key_stick_base_sens * 0.48 * global_sens) * center_redux
    if(key_ButtonQ):
        if m_redu0x > 0:
            vjoyaxisX -= (key_sens * key_stick_vx_sens * key_stick_base_sens * 0.48 * global_sens) / center_redux
        else:
            vjoyaxisX -= (key_sens * key_stick_vx_sens * key_stick_base_sens * 0.48 * global_sens) * center_redux
if(key_vjoyaxisY& (not key_Button_LeftCtrl)):
    if(key_ButtonLeftShift):
        if m_redu0y > 0:
            vjoyaxisY += (key_sens * key_stick_vy_sens * key_stick_base_sens * global_sens) / center_reduy
        else:
            vjoyaxisY += (key_sens * key_stick_vy_sens * key_stick_base_sens * global_sens) * center_reduy
    if(key_ButtonC):
        if m_redu0x > 0:
            vjoyaxisY -= (key_sens * key_stick_vy_sens * key_stick_base_sens * global_sens) / center_reduy
        else:
            vjoyaxisY -= (key_sens * key_stick_vy_sens * key_stick_base_sens * global_sens) * center_reduy

# 键盘总距
if(key_throttle_key& (not key_Button_LeftCtrl)):
    if(key_ButtonW):
            th_axisrz -= key_sens * throttle_base_sens* 0.04 * global_sens
    if(key_ButtonS):
            th_axisrz += key_sens * throttle_base_sens* 0.04 * global_sens

#=======================================================================================================================================================================#
#=============================================================固定鼠标光标=====================================================================================#
if toggle_mouselock:
    mouselock = not mouselock
    
if (mouselock):
    if (mouselock1):
        user32.SetCursorPos(x,y)  # 固定鼠标位置

#======================================================================== 视角缩放控制逻辑（含灵敏度倍率计算）===============================================================================#
# 计算当前缩放等级对应的视角灵敏度倍率（核心新增逻辑）
if is_alt_zoom_active and alt_zoom_cache is None:
    # Alt+滚轮精细缩放时，根据当前值动态计算倍率
    # 将缩放值映射到0-4的等级范围
    normalized_zoom = (last_alt_zoom_value + zoom_max_travel) / (2 * zoom_max_travel)  # 0~1范围
    level_range = len(zoom_sens_multipliers) - 1  # 4
    mapped_level = min(max(0, normalized_zoom * level_range), level_range)  # 0~4范围
    
    # 计算上下两个等级的插值权重
    lower_level = int(mapped_level)
    upper_level = min(lower_level + 1, level_range)
    weight = mapped_level - lower_level
    
    # 线性插值计算当前倍率
    current_zoom_sens_multi = (zoom_sens_multipliers[lower_level] * (1 - weight) + 
                              zoom_sens_multipliers[upper_level] * weight)
else:
    # 固定档位时直接使用对应倍率
    current_zoom_sens_multi = zoom_sens_multipliers[current_zoom_level]

if key_zoom_reset:
    current_zoom_level = 1
    temp_zoom_level = None
    alt_zoom_cache = None
    last_alt_zoom_value = zoom_levels[current_zoom_level]  
    target_zoom = zoom_levels[current_zoom_level]
    is_alt_zoom_active = False
else:
    side_button_pressed = False
    prev_is_alt_active = is_alt_zoom_active

    # 放大键处理（侧键3：值减小→放大）
    if key_zoom_in:
        side_button_pressed = True
        if prev_is_alt_active:
            differences = [abs(last_alt_zoom_value - level) for level in zoom_levels]
            closest_idx = differences.index(min(differences))
            temp_zoom_level = closest_idx
            alt_zoom_cache = last_alt_zoom_value
            is_alt_zoom_active = False

        if zoom_in_press_time == 0:
            zoom_in_press_time = time.time() * 1000
            is_click_handled = False
        else:
            if (time.time() * 1000 - zoom_in_press_time) > click_threshold and not is_click_handled:
                if temp_zoom_level is not None and temp_zoom_level < len(zoom_levels) - 1:
                    temp_zoom_level += 1
                is_click_handled = True
    else:
        if zoom_in_press_time > 0:
            if (time.time() * 1000 - zoom_in_press_time) <= click_threshold and not is_click_handled:
                if alt_zoom_cache is not None:
                    differences = [abs(alt_zoom_cache - level) for level in zoom_levels]
                    current_zoom_level = differences.index(min(differences))
                    alt_zoom_cache = None
                elif current_zoom_level < len(zoom_levels) - 1:
                    current_zoom_level += 1
                last_alt_zoom_value = zoom_levels[current_zoom_level]
            else:
                if alt_zoom_cache is not None:
                    last_alt_zoom_value = alt_zoom_cache
                    alt_zoom_cache = None
                elif temp_zoom_level is not None:
                    current_zoom_level = temp_zoom_level
                    last_alt_zoom_value = zoom_levels[current_zoom_level]
            zoom_in_press_time = 0
            temp_zoom_level = None
            is_click_handled = False

    # 缩小键处理（侧键4：值增大→缩小）
    if key_zoom_out:
        side_button_pressed = True
        if prev_is_alt_active:
            differences = [abs(last_alt_zoom_value - level) for level in zoom_levels]
            closest_idx = differences.index(min(differences))
            temp_zoom_level = closest_idx
            alt_zoom_cache = last_alt_zoom_value
            is_alt_zoom_active = False

        if zoom_out_press_time == 0:
            zoom_out_press_time = time.time() * 1000
            is_click_handled = False
        else:
            if (time.time() * 1000 - zoom_out_press_time) > click_threshold and not is_click_handled:
                if temp_zoom_level is not None and temp_zoom_level > 0:
                    temp_zoom_level -= 1
                is_click_handled = True
    else:
        if zoom_out_press_time > 0:
            if (time.time() * 1000 - zoom_out_press_time) <= click_threshold and not is_click_handled:
                if alt_zoom_cache is not None:
                    differences = [abs(alt_zoom_cache - level) for level in zoom_levels]
                    current_zoom_level = differences.index(min(differences))
                    alt_zoom_cache = None
                elif current_zoom_level > 0:
                    current_zoom_level -= 1
                last_alt_zoom_value = zoom_levels[current_zoom_level]
            else:
                if alt_zoom_cache is not None:
                    last_alt_zoom_value = alt_zoom_cache
                    alt_zoom_cache = None
                elif temp_zoom_level is not None:
                    current_zoom_level = temp_zoom_level
                    last_alt_zoom_value = zoom_levels[current_zoom_level]
            zoom_out_press_time = 0
            temp_zoom_level = None
            is_click_handled = False

    # Alt+滚轮逻辑（上滚放大，下滚缩小）
    if key_alt and mouse.wheel != 0:
        is_alt_zoom_active = True
        if mouse.wheel > 0:
            last_alt_zoom_value -= fine_zoom_step
        else:
            last_alt_zoom_value += fine_zoom_step
        last_alt_zoom_value = max(min(last_alt_zoom_value, zoom_max_travel), -zoom_max_travel)
        target_zoom = last_alt_zoom_value
    elif is_alt_zoom_active and not side_button_pressed:
        target_zoom = last_alt_zoom_value
    else:
        if temp_zoom_level is not None:
            target_zoom = zoom_levels[temp_zoom_level]
        else:
            target_zoom = zoom_levels[current_zoom_level]

# 平滑过渡到目标值
zoom_axis += (target_zoom - zoom_axis) * smooth_factor

#=========================================================================滚轮双发油门/总矩=============================================================================#
if (th_vjoyaxis) and not (key_alt and mouse.wheel != 0):
    if a_max * ( 1 - IDth_postion) > th_axisL > a_min * ABth_postion:
        if a_max * ( 1 - IDth_postion) > th_axisR > a_min * ABth_postion: 
                AB_throttle = False
                
    if key_thidle:
        AB_throttle = True
        th_sens = th_sensn
    else:
        th_sens = th_sensm
        if (helicopter):
            th_sens = th_sensh
        else:
            if (propeller):
                th_sens = th_sensprop
                AB_throttle = True
            else:
                th_sens = th_sensm            
        
    if (th_vjoyaxisL):
        th_axisL -= (mouse.wheel * th_sens * throttle_base_sens * global_sens)
    if not propeller:
        if (th_vjoyaxisR):
            th_axisR -= (mouse.wheel * th_sens * throttle_base_sens * global_sens)
    else:
        if key_throttleR :
            th_axisR -= (mouse.wheel * th_sens * throttle_base_sens * global_sens)
            
    if key_throttleL :
        th_vjoyaxisR = False
    else:
        th_vjoyaxisR = True
        
    if key_throttleR :
        th_vjoyaxisL = False
    else:
        th_vjoyaxisL = True
        
    if key_throttleL & key_throttleR:
        if th_axisR > th_axisL:
            th_axisR = th_axisL
        else:
            th_axisL = th_axisR

    if (AB_throttle):
        if th_axisL < a_min:
            th_axisL = a_min 
        if th_axisR < a_min :
            th_axisR = a_min
        if th_axisL > a_max:
            th_axisL = a_max
        if th_axisR > a_max:
            th_axisR = a_max    
    else: 
        if th_axisL < a_min * ABth_postion:
            th_axisL = a_min * ABth_postion
        if th_axisR < a_min * ABth_postion:
            th_axisR = a_min * ABth_postion
        if th_axisL > a_max * ( 1 - IDth_postion):
            th_axisL = a_max * ( 1 - IDth_postion)
        if th_axisR > a_max * ( 1 - IDth_postion):
            th_axisR = a_max * ( 1 - IDth_postion)
            
if (th_vjoyaxisrz) and not (key_alt and mouse.wheel != 0):
    th_axisrz -= (mouse.wheel * th_sensrz * throttle_base_sens * global_sens)

if th_axisrz > a_max:
    th_axisrz = a_max
elif th_axisrz < a_min:
    th_axisrz = a_min

if key_throttlerz:
        th_vjoyaxis = False
        th_vjoyaxisL = False
        th_vjoyaxisR = False
        th_vjoyaxisrz = True
else:
        th_vjoyaxis = True
        th_vjoyaxisrz = False

#=======================================================================踩舵与刹车====================================================================================#
# 脚舵
if m_reduz > 0:
    m_redu = m_reduz + 1
elif m_reduz <= 0:
    m_redu = -m_reduz + 1
    
if rud_axis > 0: 
    center_redurz = 7 * m_redu ** (1 - (rud_axis / a_max))
elif rud_axis < 0:
    center_redurz = 7 * m_redu ** (1 - (rud_axis / a_min))
    
if key_rudderRight:
    rud_axis += (rud_inc* 9 * global_sens) / center_redurz
elif rud_axis > Trimp_centerZ:
    rud_axis -= rudreturn_sens
if key_rudderLeft:
    rud_axis -= (rud_inc* 9 * global_sens) / center_redurz
elif rud_axis < Trimp_centerZ:
    rud_axis += rudreturn_sens
            
if key_centerrud:
    if rud_axis > Trimp_centerZ:
        rud_axis -= rudreturn_sens
    if rud_axis < Trimp_centerZ:
        rud_axis += rudreturn_sens
            
if key_TrimprudR | key_TrimprudL:
    Trimp_centerZ = rud_axis

if key_TrimprudZero | Key_Trimpcenter:
    Trimp_centerZ = 0
    
if rud_axis > a_max:
    rud_axis = a_max
elif rud_axis < a_min:
    rud_axis = a_min
    
# 刹车
if rud_axis <= a_min:
    br_axisL += br_inc
else:
    br_axisL -= br_dnc
if rud_axis >= a_max:
    br_axisR += br_inc
else:
    br_axisR -= br_dnc
        
if key_centerrud:
    if Trimp_centerZ + a_min * 0.1 <= rud_axis <= Trimp_centerZ + a_max * 0.1:
        br_axisL += br_inc 
        br_axisR += br_inc
else:
    if br_axisL != a_min:
        br_axisL -= br_dnc
    if br_axisR != a_min:    
        br_axisR -= br_dnc            
    
if br_axisL > a_max:
    br_axisL = a_max
elif br_axisL < a_min:
    br_axisL = a_min
    
if br_axisR > a_max:
    br_axisR = a_max
elif br_axisR < a_min:
    br_axisR = a_min
    
#=====================================================================摇杆控制（独立灵敏度）==============================================================================#    
if (vjoyaxis): 
    
    if m_redu0x < 0:
        m_redu3 = -m_redu0x + 1 
    else:
        m_redu3 = m_redu0x + 1 
    if m_redu0y < 0:
        m_redu4 = -m_redu0y + 1
    else:
        m_redu4 = m_redu0y + 1
        
    if vjoyaxisX > Trimp_centerX: 
        center_redux = m_redu3 ** (1 - (vjoyaxisX / a_max))
    elif vjoyaxisX < Trimp_centerX:
        center_redux = m_redu3 ** (1 - (vjoyaxisX / a_min))
    if vjoyaxisY > Trimp_centerY: 
        center_reduy = m_redu4 ** (1 - (vjoyaxisY / a_max))
    elif vjoyaxisY < Trimp_centerY:
        center_reduy = m_redu4 ** (1 - (vjoyaxisY / a_min))             

    if(vjoyaxis_x):
        if (Frontview_tracking):
            if (Rearview_tracking):
                if m_redu0x > 0:
                    vjoyaxisX -= (mouse.deltaX * stick_vx_sensRear * stick_base_sens * 0.48 * global_sens) / center_redux
                else:
                    vjoyaxisX -= (mouse.deltaX * stick_vx_sensRear * stick_base_sens * 0.48 * global_sens) * center_redux
                if vjoyaxisY >= Trimp_centerY + a_max * 0.4:
                    if vjoyaxisX != Trimp_centerX * 0.1:
                        vjoyaxisX -= (vjoyaxisX - Trimp_centerX) * 0.5 
                if vjoyaxisX >= Trimp_centerX + a_max * 0.35:
                    vjoyaxisX = Trimp_centerX + a_max * 0.35
                if vjoyaxisX <= Trimp_centerX + a_min * 0.35:
                    vjoyaxisX = Trimp_centerX + a_min * 0.35
            else:
                if m_redu0x > 0:
                    vjoyaxisX += (mouse.deltaX * stick_vx_sensFront * stick_base_sens * 0.48 * global_sens) / center_redux
                else:
                    vjoyaxisX += (mouse.deltaX * stick_vx_sensFront * stick_base_sens * 0.48 * global_sens) * center_redux
                if vjoyaxisX >= Trimp_centerX + a_max * 0.5:
                    vjoyaxisX = Trimp_centerX + a_max * 0.5
                if vjoyaxisX <= Trimp_centerX + a_min * 0.5:
                    vjoyaxisX = Trimp_centerX + a_min * 0.5
        else:
            # 摇杆X轴动态补偿（独立参数）
            mouse_speedX = abs(mouse.deltaX - last_mouse_deltaX)
            speed_multiX = 1.0 + min(mouse_speedX / stick_speed_sens, stick_max_speed_multi - 1.0)
            
            if m_redu0x > 0:
                vjoyaxisX += (mouse.deltaX * stick_vx_sens * stick_base_sens * 30 * speed_multiX * global_sens) / center_redux
            else:
                vjoyaxisX += (mouse.deltaX * stick_vx_sens * stick_base_sens * 30 * speed_multiX * global_sens) * center_redux
            
            if vjoyaxisX > a_max:
                vjoyaxisX = a_max
                vx_max = a_max
            elif vjoyaxisX < a_min:
                vjoyaxisX = a_min
                vx_max = a_min
            last_mouse_deltaX = mouse.deltaX
                    
    if (vjoyaxis_y):
        if (Frontview_tracking):
            if vjoyaxisY >= Trimp_centerY:
                if key_Button4:
                    if m_redu0y > 0:
                        vjoyaxisY -= (mouse.deltaY * stick_vy_sensRear * stick_base_sens * 0.5 * global_sens) / center_reduy
                    else:
                        vjoyaxisY -= (mouse.deltaY * stick_vy_sensRear * stick_base_sens * 0.5 * global_sens) * center_reduy
                else:
                    if m_redu0y > 0:
                        vjoyaxisY -= (mouse.deltaY * stick_vy_sensFront * stick_base_sens * 0.5 * global_sens) / center_reduy
                    else:
                        vjoyaxisY -= (mouse.deltaY * stick_vy_sensFront * stick_base_sens * 0.5 * global_sens) * center_reduy
            else:
                vjoyaxisY = Trimp_centerY
        else:
            # 摇杆Y轴动态补偿（独立参数）
            mouse_speedY = abs(mouse.deltaY - last_mouse_deltaY)
            speed_multiY = 1.0 + min(mouse_speedY / stick_speed_sens, stick_max_speed_multi - 1.0)
            
            if m_redu0y > 0:
                if vjoyaxisY >= Trimp_centerY:
                    vjoyaxisY += (mouse.deltaY * stick_vy_sens * stick_base_sens * 14.4 * speed_multiY * global_sens) / center_reduy
                else:
                    vjoyaxisY += (mouse.deltaY * stick_vy_sens * stick_base_sens * 14.4 * speed_multiY * global_sens) / center_reduy
            else:
                if vjoyaxisY >= Trimp_centerY:
                    vjoyaxisY += (mouse.deltaY * stick_vy_sens * stick_base_sens * 14.4 * speed_multiY * global_sens) * center_reduy
                else:
                    vjoyaxisY += (mouse.deltaY * stick_vy_sens * stick_base_sens * 14.4 * speed_multiY * global_sens) * center_reduy
            
            if vjoyaxisY > a_max:
                vjoyaxisY = a_max
                vy_max = a_max
            elif vjoyaxisY < a_min:
                vjoyaxisY = a_min
                vy_max = a_min
            last_mouse_deltaY = mouse.deltaY
        
# 摇杆自动回中
if (Re_vjoyaxisx):
    if mouse.deltaX <= 1.5 : 
        if vjoyaxisX >= vx_max : 
            vx_max = vjoyaxisX
        elif vjoyaxisX < vx_max * 0.98:
            if vjoyaxisX > Trimp_centerX:
                vjoyaxisX -= (vjoyaxisX - Trimp_centerX) * 0.04 
                vx_max -= (vjoyaxisX - Trimp_centerX) * 0.04 
        if vjoyaxisX <= vx_min: 
            vx_min = vjoyaxisX
        elif vjoyaxisX > vx_min * 0.98:
            if vjoyaxisX < Trimp_centerX:
                vjoyaxisX -= (vjoyaxisX - Trimp_centerX) * 0.04 
                vx_min -= (vjoyaxisX - Trimp_centerX) * 0.04  

if (Re_vjoyaxisy):
    if mouse.deltaY <= 1.5 : 
        if vjoyaxisY >= vy_max:
            vy_max = vjoyaxisY
        elif vjoyaxisY < vy_max * 0.95: 
            if vjoyaxisY > Trimp_centerY:
                vjoyaxisY -= (vjoyaxisY - Trimp_centerY) * 0.02 
                vy_max -= (vjoyaxisY - Trimp_centerY) * 0.02 
        if vjoyaxisY <= vy_min :
            vy_min = vjoyaxisY
        elif vjoyaxisY > vy_min * 0.95: 
            if vjoyaxisY < Trimp_centerY:
                vjoyaxisY -= (vjoyaxisY - Trimp_centerY) * 0.02 
                vy_min -= (vjoyaxisY - Trimp_centerY) * 0.02

if Key_ForceTrimp:
    Trimp_centerX = vjoyaxisX
    Trimp_centerY = vjoyaxisY
if Key_Trimpcenter:
    Trimp_centerX = 0
    Trimp_centerY = 0
    Trimp_centerZ = 0
if(key_vjoyaxisY_front) :
    Trimp_centerY -= key_sens * stick_vy_sens * 0.24 * global_sens
if(key_vjoyaxisY_behind):
    Trimp_centerY += key_sens * stick_vy_sens * 0.24 * global_sens
if(key_vjoyaxisX_left):
    Trimp_centerX -= key_sens * stick_vx_sens * 0.5 * global_sens
if(key_vjoyaxisX_right):
    Trimp_centerX += key_sens * stick_vx_sens * 0.5 * global_sens
if Key_view_Trimp:
    view_Trimp_centerX = view_vjoyaxisX
    view_Trimp_centerY = view_vjoyaxisY
if Key_Trimpcenter:
    view_Trimp_centerX = 0
    view_Trimp_centerY = 0
    view_Trimp_centerZ = 0

#=====================================================================视角控制（含缩放灵敏度调节）==============================================================================#
if (view_vjoyaxis): 
    
    if m_redu0x < 0:
        m_redu3 = -m_redu0x + 1 
    else:
        m_redu3 = m_redu0x + 1 
    if m_redu0y < 0:
        m_redu4 = -m_redu0y + 1
    else:
        m_redu4 = m_redu0y + 1
        
    if view_vjoyaxisX > view_Trimp_centerX: 
        view_center_redux = m_redu3 ** (1 - (view_vjoyaxisX / a_max))
    elif view_vjoyaxisX < view_Trimp_centerX:
        view_center_redux = m_redu3 ** (1 - (view_vjoyaxisX / a_min))
    if view_vjoyaxisY > view_Trimp_centerY: 
        view_center_reduy = m_redu4 ** (1 - (view_vjoyaxisY / a_max))
    elif view_vjoyaxisY < view_Trimp_centerY:
        view_center_reduy = m_redu4 ** (1 - (view_vjoyaxisY / a_min))             

    if (Frontview_tracking):
        if (Rearview_tracking):
            # 应用缩放灵敏度倍率（核心修改点）
            scaled_sens = stick_vx_sensRear * current_zoom_sens_multi
            if m_redu0x > 0:
                view_vjoyaxisX -= (mouse.deltaX * scaled_sens * view_base_sens * 0.48 * global_sens) / view_center_redux
            else:
                view_vjoyaxisX -= (mouse.deltaX * scaled_sens * view_base_sens * 0.48 * global_sens) * view_center_redux
            view_vjoyaxisX = max(min(view_vjoyaxisX, view_max_angle), view_min_angle)
            if view_vjoyaxisY >= view_Trimp_centerY + a_max * 0.4:
                if view_vjoyaxisX != view_Trimp_centerX * 0.1:
                    view_vjoyaxisX -= (view_vjoyaxisX - view_Trimp_centerX) * 0.5 
            if view_vjoyaxisX >= view_Trimp_centerX + a_max * 0.35:
                view_vjoyaxisX = view_Trimp_centerX + a_max * 0.35
            if view_vjoyaxisX <= view_Trimp_centerX + a_min * 0.35:
                view_vjoyaxisX = view_Trimp_centerX + a_min * 0.35
        else:
            # 应用缩放灵敏度倍率（核心修改点）
            scaled_sens = stick_vx_sensFront * current_zoom_sens_multi
            if m_redu0x > 0:
                view_vjoyaxisX += (mouse.deltaX * scaled_sens * view_base_sens * 0.48 * global_sens) / view_center_redux
            else:
                view_vjoyaxisX += (mouse.deltaX * scaled_sens * view_base_sens * 0.48 * global_sens) * view_center_redux
            view_vjoyaxisX = max(min(view_vjoyaxisX, view_max_angle), view_min_angle)
            if view_vjoyaxisX >= view_Trimp_centerX + a_max * 0.5:
                view_vjoyaxisX = view_Trimp_centerX + a_max * 0.5
            if view_vjoyaxisX <= view_Trimp_centerX + a_min * 0.5:
                view_vjoyaxisX = view_Trimp_centerX + a_min * 0.5
    else:
        # 视角X轴动态补偿+缩放倍率（核心修改点）
        mouse_speedX = abs(mouse.deltaX - last_mouse_deltaX)
        speed_multiX = 1.0 + min(mouse_speedX / view_speed_sens, view_max_speed_multi - 1.0)
        
        if m_redu0x > 0:
            view_vjoyaxisX += (mouse.deltaX * view_vx_sens * view_base_sens * 0.48 * speed_multiX * 
                              global_sens * current_zoom_sens_multi) / view_center_redux
        else:
            view_vjoyaxisX += (mouse.deltaX * view_vx_sens * view_base_sens * 0.48 * speed_multiX * 
                              global_sens * current_zoom_sens_multi) * view_center_redux
        
        view_vjoyaxisX = max(min(view_vjoyaxisX, view_max_angle), view_min_angle)
        if view_vjoyaxisX > a_max:
            view_vjoyaxisX = a_max
            view_vx_max = a_max
        elif view_vjoyaxisX < a_min:
            view_vjoyaxisX = a_min
            view_vx_max = a_min
                
if (view_vjoyaxis_y):
    if (Frontview_tracking):
        if view_vjoyaxisY >= view_Trimp_centerY:
            if key_Button4:
                # 应用缩放灵敏度倍率（核心修改点）
                scaled_sens = stick_vy_sensRear * current_zoom_sens_multi
                if m_redu0y > 0:
                    view_vjoyaxisY -= (mouse.deltaY * scaled_sens * view_base_sens * 0.5 * global_sens) / view_center_reduy
                else:
                    view_vjoyaxisY -= (mouse.deltaY * scaled_sens * view_base_sens * 0.5 * global_sens) * view_center_reduy
            else:
                # 应用缩放灵敏度倍率（核心修改点）
                scaled_sens = stick_vy_sensFront * current_zoom_sens_multi
                if m_redu0y > 0:
                    view_vjoyaxisY -= (mouse.deltaY * scaled_sens * view_base_sens * 0.5 * global_sens) / view_center_reduy
                else:
                    view_vjoyaxisY -= (mouse.deltaY * scaled_sens * view_base_sens * 0.5 * global_sens) * view_center_reduy
            view_vjoyaxisY = max(min(view_vjoyaxisY, view_max_angle), view_min_angle)
        else:
            view_vjoyaxisY = view_Trimp_centerY
    else:
        # 视角Y轴动态补偿+缩放倍率（核心修改点）
        mouse_speedY = abs(mouse.deltaY - last_mouse_deltaY)
        speed_multiY = 1.0 + min(mouse_speedY / view_speed_sens, view_max_speed_multi - 1.0)
        
        if m_redu0y > 0:
            if view_vjoyaxisY >= view_Trimp_centerY:
                view_vjoyaxisY += (mouse.deltaY * view_vy_sens * view_base_sens * 0.48 * speed_multiY * 
                                  global_sens * current_zoom_sens_multi) / view_center_reduy
            else:
                view_vjoyaxisY += (mouse.deltaY * view_vy_sens * view_base_sens * 0.48 * speed_multiY * 
                                  global_sens * current_zoom_sens_multi) / view_center_reduy
        else:
            if view_vjoyaxisY >= view_Trimp_centerY:
                view_vjoyaxisY += (mouse.deltaY * view_vy_sens * view_base_sens * 0.48 * speed_multiY * 
                                  global_sens * current_zoom_sens_multi) * view_center_reduy 
            else:
                view_vjoyaxisY += (mouse.deltaY * view_vy_sens * view_base_sens * 0.48 * speed_multiY * 
                                  global_sens * current_zoom_sens_multi) * view_center_reduy
        
        view_vjoyaxisY = max(min(view_vjoyaxisY, view_max_angle), view_min_angle)
        if view_vjoyaxisY > a_max:
            view_vjoyaxisY = a_max
            view_vy_max = a_max
        elif view_vjoyaxisY < a_min:
            view_vjoyaxisY = a_min
            view_vy_max = a_min

if not key_view_vjoyaxis:
    view_vjoyaxisX = view_Trimp_centerX
    view_vjoyaxisY = view_Trimp_centerY

#========================================================================== vjoy 轴与按钮映射 =========================================================================#
v.x = int(round(vjoyaxisX))  # 滚转轴
v.y = vjoyaxisY  # 俯仰轴
v.z = rud_axis  # 键盘脚舵
v.slider = th_axisL  # 左发油门
v.dial = th_axisR  # 右发油门
v.rz = th_axisrz  # 滚轮油混
v.rx = int(round(view_vjoyaxisX))  # 水平视角轴
v.ry = view_vjoyaxisY  # 垂直视角轴
v1.z = int(round(zoom_axis))  # 视角缩放轴

if key_Button2:
    v.setButton(0,False)
else:
    v.setButton(0,key_Button1)
    # v.setButton(0, key_Button1 and fire_enabled)

v.setButton(1,key_Button2)

if not Key_Frontviewtracking:
    v.setButton(2,key_Button3)
else:
    v.setButton(2,False)
    
if vjoyaxis:
    if (helicopter):
        v.setButton(3,key_Button4)

v.setButton(4,key_Button5)

v.setButton(7,mouse.getButton(1))

v.setButton(8,key_ButtonC)
v.setButton(9,key_ButtonLeftShift)
v.setButton(10,key_ButtonQ)
v.setButton(11,key_ButtonE)

#=====================================================================================================================================================================#
#======== 调试 ========#
# 不调试时请注释掉，不然会增加CPU使用率
# diagnostics.watch(v.x)    # 滚转轴
# diagnostics.watch(v.y)    # 俯仰轴
# diagnostics.watch(v.slider)  # 左油门
# diagnostics.watch(v.dial)    # 右油门
# diagnostics.watch(v.rx)      # 水平视角
# diagnostics.watch(v.ry)      # 水平视角
# diagnostics.watch(v.rz)      # 油混
# diagnostics.watch(rud_axis)  # 脚舵
# diagnostics.watch(Trimp_centerZ)  # 脚舵配平
# diagnostics.watch(v1.z)  # 视角缩放值
# diagnostics.watch(current_zoom_level) # 缩放等级
# diagnostics.watch(is_alt_zoom_active)  # Alt+滚轮状态
# diagnostics.watch(current_zoom_sens_multi)  # 当前视角灵敏度倍率（新增调试项）


#======== credits ========#
#目前该脚本正处于开发阶段，如果你有任何建议，可随时与我练习。感谢您的支持与喜爱！
#该脚本是我在@爱认真的泡泡 Bilibili  的专栏内容找到的，感谢他提供了这样一种方式，并允许我发布基于他代码的更改到github.
#脚本中部分内容由AI编写，AI给了我很大的帮助
#这是 @爱认真的泡泡  的b站专栏 https://www.bilibili.com/opus/697225740818579477
#据上述专栏描述，他也是基于此贴写的代码  https://www.lfs.net/forum/post/1862759

#Edited finally by NewMan   2025-11-13  https://space.bilibili.com/1771594975
