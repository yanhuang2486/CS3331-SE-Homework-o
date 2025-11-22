"""
作者：yanhuang2486
gui_ui.py
---------
GUI 界面模块，基于 tkinter/ttk 实现应用的所有窗口与对话框。

模块级说明（全局/输入/输出/入口参数）:
- 全局变量：`ThemeManager.PALETTE` 定义了应用的莫兰迪风格配色方案，供各窗口统一使用。
- 输入数据：由上层 `main.py` 传入的控制器实例（`AuthController`, `ItemController`, `TypeController`, `DemandController`, `ApplicationController`）
    以及用户在界面上输入的字符串（用户名、密码、物品信息等）。
- 输出数据：多数交互操作会通过控制器方法将实体持久化（例如 `item_controller.add_item(...)`），
    或返回布尔/列表结果用于界面反馈；界面本身不直接返回复杂数据结构。
- 入口参数说明：每个对话框类的构造函数均以 `parent`（父窗口）为首参数，并接收相应的控制器对象和回调函数，
    具体请参考各类 docstring（下方已标注）。

注：本文件仅负责视图和与用户交互的逻辑，业务/持久化由 controllers 层处理（依赖注入）。
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List
from controllers import AuthController, ItemController, TypeController, DemandController, ApplicationController, DataManager
from entities import User, Item, ItemType, Demand, Application


class FontManager:
    """字体工具类。

    提供统一的字体配置方法：`get_font` 和 `get_chinese_font`。
    入口参数：size（字号）、weight（字重）
    输出：用于 tkinter/ttk 的字体元组，例如 ("宋体", 12, "bold")。
    """
    @staticmethod
    def get_font(size=10, weight="normal"):
        return ("Helvetica", size, weight)
    
    @staticmethod
    def get_chinese_font(size=10, weight="normal"):
        return ("宋体", size, weight)

class ThemeManager:
    """主题管理器，应用简约的莫兰迪色系样式到 ttk 部件。

    全局/模块级变量：
    - `PALETTE`：字典，定义背景、面板、按钮、输入框等颜色值，界面中的控件样式从此处读取以保持一致性。

    方法：
    - `apply(root)`：将样式应用到传入的 `tk.Tk` 根窗口上。

    注意：此类只负责样式配置，不处理业务逻辑或数据。
    """
    PALETTE = {
        # muted, desaturated Morandi-like colors
        'bg': '#E7E6E4',          # light neutral background
        'panel': '#D0CBC7',       # panel / frame background
        'accent': '#A7A39A',      # muted accent (buttons hover)
        'muted': '#8F8B86',       # secondary text / borders
        'button_bg': '#CFC9C4',   # button base
        'button_fg': '#222222',   # button text
        'entry_bg': '#F4F3F2',    # entry background
        'text': '#333333',        # main text color
    }

    @staticmethod
    def apply(root: tk.Tk):
        style = ttk.Style(root)
        # prefer a theme that allows background changes
        try:
            style.theme_use('clam')
        except Exception:
            pass

        p = ThemeManager.PALETTE
        # root background
        try:
            root.configure(bg=p['bg'])
        except Exception:
            pass

        # Basic widget styles
        style.configure('TFrame', background=p['bg'])
        style.configure('TLabel', background=p['bg'], foreground=p['text'], font=FontManager.get_chinese_font())
        style.configure('TLabelFrame', background=p['bg'], foreground=p['text'], font=FontManager.get_chinese_font())
        style.configure('TLabelframe.Label', background=p['bg'], foreground=p['text'])

        style.configure('TButton', background=p['button_bg'], foreground=p['button_fg'], relief='flat', padding=6)
        style.map('TButton', background=[('active', p['accent']), ('!disabled', p['button_bg'])])

        style.configure('TEntry', fieldbackground=p['entry_bg'], background=p['entry_bg'], foreground=p['text'])
        style.configure('TCombobox', fieldbackground=p['entry_bg'], background=p['entry_bg'], foreground=p['text'])

        style.configure('TNotebook', background=p['bg'])
        style.configure('TNotebook.Tab', background=p['panel'], foreground=p['text'], padding=[8, 4])

        # Treeview
        style.configure('Treeview', background='white', fieldbackground='white', foreground=p['text'])
        style.configure('Treeview.Heading', background=p['panel'], foreground=p['text'])

        # Scrollbars
        style.configure('Vertical.TScrollbar', background=p['panel'], troughcolor=p['bg'])

        # Additional small tweaks
        root.option_add('*Font', FontManager.get_font())
        root.option_add('*Foreground', p['text'])
        root.option_add('*Background', p['bg'])

class LoginUI:
    def __init__(self, root, auth_controller: AuthController, on_login_success):
        """登录界面主类。

        构造参数:
        - root: tkinter 根窗口或父窗口（`tk.Tk` 或 `tk.Toplevel`）
        - auth_controller: `AuthController` 实例，用于执行登录/注册操作（输入数据由界面收集并传给 controller）
        - on_login_success: 登录成功后的回调函数（无参数），用于切换到主界面

        输出/副作用:
        - 在成功登录后调用 `on_login_success()`；失败时显示错误对话框。
        """
        self.root = root
        self.auth_controller = auth_controller
        self.on_login_success = on_login_success
        # apply theme once for this root
        try:
            ThemeManager.apply(self.root)
        except Exception:
            pass

        self.setup_ui()
    
    def setup_ui(self):
        """构建登录界面元素并进行布局。

        输入数据: 无（只构建控件）；用户通过界面输入用户名/密码并触发 `login()`。
        输出数据: 无直接返回值，界面交互会调用 `auth_controller.login` 并在成功时触发回调。
        """
        # create a container that fills the root, then center the actual frame inside it
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame = ttk.Frame(container, padding="20")
        self.frame.pack(anchor=tk.CENTER)
        
        # 标题
        title_label = ttk.Label(
            self.frame,
            text="“复活”物品流通平台",
            font=FontManager.get_chinese_font(16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 12))

        # 大框：用 Canvas 绘制一个无填充、灰绿色边框的矩形，内部放置一个 inner_frame 来包含输入与按钮
        # Canvas 背景与窗口背景一致以达到“无填充”效果
        canvas = tk.Canvas(self.frame, highlightthickness=0, bd=0, bg=ThemeManager.PALETTE.get('bg', '#E7E6E4'))
        canvas.grid(row=1, column=0, columnspan=2, pady=(0, 12))

        inner_frame = ttk.Frame(canvas, padding="8")

        # 在 canvas 上创建一个 window，用来放置 inner_frame。先在 canvas 上创建矩形（会在底层），再创建 window
        # 我mitigate sizing after widgets are laid out by drawing rectangle after populating inner_frame

        # 用户名（放在 inner_frame 内）
        ttk.Label(inner_frame, text="用户名:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0,6))
        self.username_entry = ttk.Entry(inner_frame, width=22, font=FontManager.get_font())
        self.username_entry.grid(row=0, column=1, pady=5)

        # 密码（放在 inner_frame 内）
        ttk.Label(inner_frame, text="密码:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0,6))
        self.password_entry = ttk.Entry(inner_frame, width=22, show="*", font=FontManager.get_font())
        self.password_entry.grid(row=1, column=1, pady=5)

        # 按钮框架（放在 inner_frame 内底部）
        button_frame = ttk.Frame(inner_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(12,0))

        ttk.Button(button_frame, text="登录", command=self.login).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="注册", command=self.show_register).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT, padx=6)

        # 将 inner_frame 放到 canvas 中的 window 中，并在其周围绘制边框矩形
        canvas_window = canvas.create_window(0, 0, anchor='nw', window=inner_frame)

        # draw border after widgets computed size
        inner_frame.update_idletasks()
        iw = inner_frame.winfo_reqwidth()
        ih = inner_frame.winfo_reqheight()
        pad = 10
        # resize canvas to fit inner_frame + padding
        canvas.config(width=iw + pad*2, height=ih + pad*2)
        # move window to padded position
        canvas.coords(canvas_window, pad, pad)
        # gray-green outline color
        gray_green = '#9AA89A'
        canvas.create_rectangle(2, 2, iw + pad*2 - 2, ih + pad*2 - 2, outline=gray_green, width=1)

        # 大框外的宣传语，居中显示
        slogan = ttk.Label(self.frame, text="让生活重启，让闲置复活", font=FontManager.get_chinese_font(12, "normal"))
        slogan.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky=tk.N)

        # 绑定回车键
        self.root.bind('<Return>', lambda event: self.login())
    
    def login(self):
        """执行登录动作。

        入口参数（来自界面）：从 `self.username_entry` 和 `self.password_entry` 获取输入。
        处理：调用 `self.auth_controller.login(username, password)`。
        输出/副作用：
        - 登录成功 -> 弹出提示并调用 `self.on_login_success()`；
        - 登录失败或输入校验失败 -> 弹出错误提示。
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        if self.auth_controller.login(username, password):
            messagebox.showinfo("成功", f"欢迎 {username}!")
            self.on_login_success()
        else:
            messagebox.showerror("错误", "用户名或密码错误")
    
    def show_register(self):
        RegisterDialog(self.root, self.auth_controller)

class RegisterDialog:
    """用户注册对话框。

    构造参数:
    - parent: 父窗口
    - auth_controller: `AuthController` 实例，用于调用 `register(username, password, contact_info)`

    界面输入字段（入口参数）: 用户名、密码、联系方式。
    输出/副作用: 成功注册后会向 `auth_controller` 请求持久化并关闭对话框，否则显示错误信息。
    """
    def __init__(self, parent, auth_controller: AuthController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("用户注册")
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        
        self.auth_controller = auth_controller
        
        # center the inner frame
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        ttk.Label(frame, text="用户名:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(frame, width=20, font=FontManager.get_font())
        self.username_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="密码:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame, width=20, show="*", font=FontManager.get_font())
        self.password_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="联系方式:", font=FontManager.get_chinese_font()).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.contact_entry = ttk.Entry(frame, width=20, font=FontManager.get_font())
        self.contact_entry.grid(row=2, column=1, pady=5)
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="注册", command=self.register).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        contact_info = self.contact_entry.get().strip()
        
        if not username or not password or not contact_info:
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if self.auth_controller.register(username, password, contact_info):
            messagebox.showinfo("成功", "注册成功！请登录")
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "用户名已存在")

class MainUI:
    """主界面类，包含普通用户与管理员的入口。

    构造参数:
    - root: 根窗口
    - auth_controller: 认证控制器（用于获取当前用户信息）
    - item_controller, type_controller, demand_controller, application_controller: 对应的控制器实例
    - on_logout: 注销回调函数（用于返回登录界面）

    作用/输出: 负责呈现主菜单、打开各功能对话框（发布物品、搜索、类型管理等），不直接返回数据。
    """
    def __init__(self, root, auth_controller: AuthController, item_controller: ItemController, 
                 type_controller: TypeController, demand_controller: DemandController, 
                 application_controller: ApplicationController, on_logout):
        self.root = root
        self.auth_controller = auth_controller
        self.item_controller = item_controller
        self.type_controller = type_controller
        self.demand_controller = demand_controller
        self.application_controller = application_controller
        self.on_logout = on_logout
        
        # ensure theme applied for main window as well
        try:
            ThemeManager.apply(self.root)
        except Exception:
            pass

        self.setup_ui()
    
    def setup_ui(self):
        # 清除现有内容
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title(f"“复活”物品流通平台 \n 欢迎 {self.auth_controller.current_user.username}")
        
        # 创建主框架并居中显示：先创建填满根窗口的 container，再将内层 main_frame 居中
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame = ttk.Frame(container, padding="10")
        main_frame.pack(anchor=tk.CENTER)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=f"“复活”物品流通平台 \n欢迎 {self.auth_controller.current_user.username} ({self.auth_controller.current_user.role})", 
            font=FontManager.get_chinese_font(14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # 创建笔记本控件，区分普通用户功能和管理员功能
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 普通用户功能标签页
        self.user_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.user_frame, text="普通用户功能")
        
        # 管理员功能标签页
        if self.auth_controller.current_user.role == "管理员":
            self.admin_frame = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(self.admin_frame, text="管理员功能")
            self.setup_admin_tab()
        
        self.setup_user_tab()
        
        # 通用功能按钮
        common_frame = ttk.Frame(main_frame)
        common_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(
            common_frame, 
            text="个人信息管理", 
            command=self.show_user_info_management,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            common_frame, 
            text="退出登录", 
            command=self.logout,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_user_tab(self):
        # 普通用户功能按钮
        buttons = [
            ("发布物品", self.show_item_publish),
            ("闲置集市", self.show_item_search),
            ("我的发布", self.show_my_items),
            ("发布需求", self.show_demand_publish),
            ("赏金客栈", self.show_demands),
            ("申请成为管理员", self.apply_for_admin),
            ("申请修改物品类型", self.apply_for_type_modification),
        ]
        
        for i, (text, command) in enumerate(buttons):
            row = i // 3
            col = i % 3
            ttk.Button(
                self.user_frame, 
                text=text, 
                command=command,
                width=15
            ).grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
    
    def setup_admin_tab(self):
        # 管理员功能按钮
        buttons = [
            ("类型管理", self.show_type_management),
            ("申请审批", self.show_application_approval),
        ]
        
        for i, (text, command) in enumerate(buttons):
            row = i // 3
            col = i % 3
            ttk.Button(
                self.admin_frame, 
                text=text, 
                command=command,
                width=15
            ).grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
    
    def show_item_publish(self):
        """打开发布物品对话框。

        入口/输出: 无返回值；会实例化 `ItemPublishDialog`，该对话框在发布成功时调用 `item_controller.add_item(...)`。
        """
        ItemPublishDialog(self.root, self.item_controller, self.type_controller, self.auth_controller)
    
    def show_item_search(self):
        ItemSearchDialog(self.root, self.item_controller, self.type_controller)
    
    def show_my_items(self):
        MyItemsDialog(self.root, self.item_controller, self.auth_controller)
    
    def show_demand_publish(self):
        DemandPublishDialog(self.root, self.demand_controller, self.type_controller, self.auth_controller)
    
    def show_demands(self):
        DemandsDialog(self.root, self.demand_controller)
    
    def show_type_management(self):
        if self.auth_controller.current_user.role != "管理员":
            messagebox.showerror("错误", "您没有管理员权限")
            return
        TypeManagementDialog(self.root, self.type_controller, self.application_controller, self.auth_controller)
    
    def show_application_approval(self):
        if self.auth_controller.current_user.role != "管理员":
            messagebox.showerror("错误", "您没有管理员权限")
            return
        ApplicationApprovalDialog(self.root, self.application_controller, self.auth_controller, self.type_controller)
    
    def show_user_info_management(self):
        UserInfoDialog(self.root, self.auth_controller)
    
    def apply_for_admin(self):
        if self.auth_controller.current_user.role == "管理员":
            messagebox.showinfo("提示", "您已经是管理员")
            return
        
        if messagebox.askyesno("确认", "确认申请成为管理员？"):
            if self.application_controller.add_application(
                "成为管理员",
                f"用户 {self.auth_controller.current_user.username} 申请成为管理员",
                self.auth_controller.current_user.user_id
            ):
                messagebox.showinfo("成功", "申请已提交，等待管理员审批")
            else:
                messagebox.showerror("错误", "申请失败")
    
    def apply_for_type_modification(self):
        TypeApplicationDialog(self.root, self.application_controller, self.type_controller, self.auth_controller)
    
    def logout(self):
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.auth_controller.logout()
            self.on_logout()

class ItemPublishDialog:
    """发布物品对话框。

    构造参数:
    - parent: 父窗口
    - item_controller: `ItemController` 实例（用于持久化 add_item）
    - type_controller: `TypeController`（用于获取类型与属性定义，输入数据来源）
    - auth_controller: `AuthController`（用于获取当前用户 id 作为 owner_id）

    界面输入/出口:
    - 界面收集物品类型、属性字段、物品名称、描述、联系方式等输入；
    - 点击发布后，调用 `item_controller.add_item(...)` 将数据写入 `data/items.json`（输出/副作用）。
    """
    def __init__(self, parent, item_controller: ItemController, type_controller: TypeController, auth_controller: AuthController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("发布物品")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        self.item_controller = item_controller
        self.type_controller = type_controller
        self.auth_controller = auth_controller
        
        self.setup_ui()
    
    def setup_ui(self):
        # 创建可滚动区域：canvas + vertical scrollbar + 内部 frame
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg=ThemeManager.PALETTE.get('bg', '#E7E6E4'), highlightthickness=0)
        vscroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 内部放置实际控件的 frame
        frame = ttk.Frame(canvas, padding="20")
        canvas_window = canvas.create_window((0, 0), window=frame, anchor='nw')

        # 当内部 frame 尺寸改变时更新 scrollregion
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        frame.bind('<Configure>', _on_frame_configure)

        # 当 canvas 尺寸改变时，调整内嵌 window 的宽度以匹配（确保横向不会出现额外空隙）
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind('<Configure>', _on_canvas_configure)

        # 鼠标滚轮支持 (Windows 常用 MouseWheel)
        def _on_mousewheel(event):
            # event.delta 在 Windows 是 120 的倍数
            delta = int(-1 * (event.delta / 120))
            canvas.yview_scroll(delta, 'units')

        canvas.bind_all('<MouseWheel>', _on_mousewheel)
        
        # 物品类型
        ttk.Label(frame, text="物品类型:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar()
        types = self.type_controller.get_all_types()
        type_names = [t.type_name for t in types]
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=type_names, state="readonly", font=FontManager.get_font())
        self.type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        if type_names:
            self.type_combo.set(type_names[0])

        # 属性输入区域（会根据类型变化动态生成），放在描述输入上方，跨两列
        self.attrs_frame = ttk.Frame(frame)
        self.attrs_frame.grid(row=2, column=0, columnspan=2, pady=(6, 6), sticky=(tk.W, tk.E))
        self.attribute_entries = {}
        # 绑定类型选择变更来更新属性输入栏
        self.type_combo.bind('<<ComboboxSelected>>', lambda e: self._build_attribute_fields())
        # 初始化属性栏
        self._build_attribute_fields()
        
        # 物品名称
        ttk.Label(frame, text="物品名称:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(frame, width=30, font=FontManager.get_font())
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # 物品描述（属性显示在此输入上方）
        ttk.Label(frame, text="物品描述:", font=FontManager.get_chinese_font()).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_text = scrolledtext.ScrolledText(frame, width=40, height=8, font=FontManager.get_font())
        self.desc_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # 联系方式
        ttk.Label(frame, text="联系方式:", font=FontManager.get_chinese_font()).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.contact_entry = ttk.Entry(frame, width=30, font=FontManager.get_font())
        self.contact_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="发布", command=self.publish_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def publish_item(self):
        """收集表单字段并提交发布请求。

        入口参数（从界面读取）:
        - item_type: 物品类型（字符串）
        - item_name: 物品名称
        - item_desc: 物品描述
        - contact_info: 联系方式
        - attribute_entries: 动态生成的属性字段（字典）

        处理: 将属性拼接为字符串前缀并与描述合并，调用 `item_controller.add_item`。
        输出/副作用: 成功 -> 提示并关闭对话框；失败 -> 错误提示。
        """
        item_type = self.type_var.get()
        item_name = self.name_entry.get().strip()
        item_desc = self.desc_text.get("1.0", tk.END).strip()
        contact_info = self.contact_entry.get().strip()
        
        if not all([item_type, item_name, item_desc, contact_info]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        # 收集属性值并把属性作为描述一部分存储，格式: 属性: key1=value1; key2=value2\n<原描述>
        attrs = []
        for k, entry in self.attribute_entries.items():
            val = entry.get().strip()
            if val:
                attrs.append(f"{k}={val}")

        full_description = item_desc
        if attrs:
            attr_str = "; ".join(attrs)
            full_description = f"属性: {attr_str}\n{item_desc}"

        if self.item_controller.add_item(
            item_name=item_name,
            description=full_description,
            item_type=item_type,
            contact_info=contact_info,
            owner_id=self.auth_controller.current_user.user_id
        ):
            messagebox.showinfo("成功", "物品发布成功！")
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "发布失败")

    def _build_attribute_fields(self):
        """根据当前选择的物品类型动态生成属性输入栏。

        入口参数: 从 `self.type_var` 获取所选类型名称；type_controller 提供类型定义对象。
        输出: 在 `self.attrs_frame` 中创建 Label + Entry 控件，并将 Entry 存入 `self.attribute_entries` 以便后续读取。
        """
        # 清理现有属性输入
        for child in self.attrs_frame.winfo_children():
            child.destroy()
        self.attribute_entries.clear()

        sel_type = self.type_var.get()
        types = self.type_controller.get_all_types()
        type_obj = next((t for t in types if t.type_name == sel_type), None)
        if not type_obj or not getattr(type_obj, 'attributes', None):
            return

        # 为每个属性创建 label + entry
        for i, attr in enumerate(type_obj.attributes):
            ttk.Label(self.attrs_frame, text=f"{attr}:", font=FontManager.get_chinese_font()).grid(row=i, column=0, sticky=tk.W, pady=4)
            e = ttk.Entry(self.attrs_frame, width=18, font=FontManager.get_font())
            e.grid(row=i, column=1, pady=4)
            self.attribute_entries[attr] = e

class ItemSearchDialog:
    """闲置集市（物品搜索）对话框。

    构造参数:
    - parent: 父窗口
    - item_controller: `ItemController`（用于执行 `search_items`）
    - type_controller: `TypeController`（用于类型下拉数据）

    输入/输出:
    - 界面输入：类型筛选、关键词；
    - 输出：在 Treeview 中显示查询结果；双击行可打开详情窗口（显示描述、属性、联系方式等）。
    """
    def __init__(self, parent, item_controller: ItemController, type_controller: TypeController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("闲置集市")
        self.dialog.geometry("600x500")
        
        self.item_controller = item_controller
        self.type_controller = type_controller
        # map of item_id -> Item for quick lookup when showing details
        self._items_map = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        main_frame = ttk.Frame(container, padding="10")
        main_frame.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
        # 搜索条件框架
        search_frame = ttk.LabelFrame(main_frame, text="搜索条件", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 类型选择
        ttk.Label(search_frame, text="物品类型:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value="所有类型")
        types = ["所有类型"] + [t.type_name for t in self.type_controller.get_all_types()]
        self.type_combo = ttk.Combobox(search_frame, textvariable=self.type_var, values=types, state="readonly", font=FontManager.get_font())
        self.type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        
        # 关键词
        ttk.Label(search_frame, text="关键词:", font=FontManager.get_chinese_font()).grid(row=0, column=2, sticky=tk.W, pady=5)
        self.keyword_entry = ttk.Entry(search_frame, width=20, font=FontManager.get_font())
        self.keyword_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # 搜索按钮
        ttk.Button(search_frame, text="搜索", command=self.search_items).grid(row=0, column=4, padx=5)
        
        # 结果框架
        result_container = ttk.Frame(main_frame)
        result_container.pack(fill=tk.BOTH, expand=True)
        result_frame = ttk.LabelFrame(result_container, text="搜索结果", padding="10")
        result_frame.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
        # 结果列表（增加“属性”列用于展示按类型填写的属性）
        columns = ("名称", "类型", "属性", "描述", "联系方式", "发布时间")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            # 给属性和描述列更大的宽度
            if col == "描述":
                self.tree.column(col, width=220)
            elif col == "属性":
                self.tree.column(col, width=160)
            else:
                self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始显示所有物品
        self.search_items()
        # 绑定双击事件查看详情
        self.tree.bind("<Double-1>", lambda event: self.show_item_details())
    
    def search_items(self):
        """执行搜索并将结果填入结果列表。

        入口参数（从界面读取）: self.type_var（可能为 '所有类型'）、self.keyword_entry（关键词字符串）
        处理: 调用 `item_controller.search_items(item_type, keyword)` 获取 Item 列表；
        输出: 在 Treeview 中插入每条记录，并将 item 存入 `self._items_map` 以便后续查看详情。
        """
        # 清空现有结果
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        item_type = self.type_var.get()
        keyword = self.keyword_entry.get().strip()
        
        if item_type == "所有类型":
            item_type = None
        
        items = self.item_controller.search_items(item_type, keyword if keyword else None)
        
        def _extract_attrs_and_desc(description: str):
            # 如果描述以 '属性:' 开头，则第一行包含属性对，用 '；' 分隔
            if description.startswith("属性:"):
                parts = description.split('\n', 1)
                first = parts[0][len("属性:"):].strip()
                rest = parts[1].strip() if len(parts) > 1 else ""
                return first, rest
            return "", description

        # 清理 items map
        self._items_map.clear()
        for item in items:
            attrs, real_desc = _extract_attrs_and_desc(item.description or "")
            short_desc = real_desc[:50] + "..." if len(real_desc) > 50 else real_desc
            # store item in map and tag the tree item with item_id
            self._items_map[item.item_id] = item
            self.tree.insert("", tk.END, values=(
                item.item_name,
                item.item_type,
                attrs,
                short_desc,
                item.contact_info,
                item.create_time
            ), tags=(item.item_id,))

    def show_item_details(self):
        """在新的对话框中展示选中物品的详细信息。

        输入: 从 Treeview 的选中行读取 item_id，并从 `self._items_map` 获取对应 `Item` 对象。
        输出: 打开一个只读详情窗口，显示名称、类型、属性、完整描述、联系方式、发布时间等。
        """
        selection = self.tree.selection()
        if not selection:
            return

        item_id = self.tree.item(selection[0], "tags")[0]
        item = self._items_map.get(item_id)
        if not item:
            return

        detail = tk.Toplevel(self.dialog)
        detail.title("物品详情")
        detail.geometry("520x360")

        container = ttk.Frame(detail, padding="12")
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="物品名称:", font=FontManager.get_chinese_font(12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Label(container, text=item.item_name, font=FontManager.get_font(12)).grid(row=0, column=1, sticky=tk.W, pady=4)

        ttk.Label(container, text="类型:", font=FontManager.get_chinese_font(12, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Label(container, text=item.item_type, font=FontManager.get_font(12)).grid(row=1, column=1, sticky=tk.W, pady=4)

        # 提取属性和描述
        attrs, real_desc = ("", item.description)
        if item.description and item.description.startswith("属性:"):
            parts = item.description.split('\n', 1)
            attrs = parts[0][len("属性:"):].strip()
            real_desc = parts[1].strip() if len(parts) > 1 else ""

        ttk.Label(container, text="属性:", font=FontManager.get_chinese_font(12, "bold")).grid(row=2, column=0, sticky=tk.NW, pady=4)
        attrs_text = scrolledtext.ScrolledText(container, width=48, height=3, font=FontManager.get_font(10))
        attrs_text.insert("1.0", attrs)
        attrs_text.config(state=tk.DISABLED)
        attrs_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=4)

        ttk.Label(container, text="描述:", font=FontManager.get_chinese_font(12, "bold")).grid(row=3, column=0, sticky=tk.NW, pady=4)
        desc_text = scrolledtext.ScrolledText(container, width=48, height=8, font=FontManager.get_font(10))
        desc_text.insert("1.0", real_desc)
        desc_text.config(state=tk.DISABLED)
        desc_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=4)

        ttk.Label(container, text="联系方式:", font=FontManager.get_chinese_font(12, "bold")).grid(row=4, column=0, sticky=tk.W, pady=4)
        ttk.Label(container, text=item.contact_info, font=FontManager.get_font()).grid(row=4, column=1, sticky=tk.W, pady=4)

        ttk.Label(container, text="发布时间:", font=FontManager.get_chinese_font(12, "bold")).grid(row=5, column=0, sticky=tk.W, pady=4)
        ttk.Label(container, text=item.create_time, font=FontManager.get_font()).grid(row=5, column=1, sticky=tk.W, pady=4)

        ttk.Button(container, text="关闭", command=detail.destroy).grid(row=6, column=1, sticky=tk.E, pady=8)

class MyItemsDialog:
    """显示当前用户发布的物品窗口（包含修改/删除操作）。

    构造参数:
    - parent: 父窗口
    - item_controller: `ItemController`（用于查询与删除/修改）
    - auth_controller: `AuthController`（用于获取当前用户 id）

    操作/副作用: 修改/删除会通过 `item_controller` 更新数据并持久化。
    """
    def __init__(self, parent, item_controller: ItemController, auth_controller: AuthController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("我的发布")
        self.dialog.geometry("700x400")
        
        self.item_controller = item_controller
        self.auth_controller = auth_controller
        
        self.setup_ui()
        self.load_items()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        main_frame = ttk.Frame(container, padding="10")
        main_frame.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
        # 物品列表
        columns = ("名称", "类型", "描述", "状态", "发布时间")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("描述", width=200)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 主列：tree + scrollbar, 侧边操作栏为纵向放置的 sidebar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # pack scrollbar to the left of the sidebar so it stays next to the tree
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # 侧边工具栏（纵向）
        sidebar = ttk.Frame(main_frame)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))

        ttk.Button(sidebar, text="修改", command=self.modify_item).pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Button(sidebar, text="删除", command=self.delete_item).pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Button(sidebar, text="刷新", command=self.load_items).pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Button(sidebar, text="关闭", command=self.dialog.destroy).pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", lambda event: self.modify_item())
    
    def load_items(self):
        """从控制器加载当前用户的物品并填充列表。

        输入: 使用 `auth_controller.current_user.user_id` 作为查询条件；
        输出: 在 Treeview 中显示用户的物品条目（包括状态与发布时间）。
        """
        # 清空现有结果
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        items = self.item_controller.get_user_items(self.auth_controller.current_user.user_id)
        
        for item in items:
            self.tree.insert("", tk.END, values=(
                item.item_name,
                item.item_type,
                item.description[:50] + "..." if len(item.description) > 50 else item.description,
                item.status,
                item.create_time
            ), tags=(item.item_id,))
    
    def get_selected_item_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个物品")
            return None
        return self.tree.item(selection[0], "tags")[0]
    
    def modify_item(self):
        """触发修改物品对话框（双击或点击修改按钮）。

        入口: 选中的物品 id；输出: 弹出 `ModifyItemDialog`，在保存成功后回调刷新函数 `self.load_items`。
        """
        item_id = self.get_selected_item_id()
        if item_id:
            ModifyItemDialog(self.dialog, self.item_controller, self.auth_controller, item_id, self.load_items)
    
    def delete_item(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        
        if messagebox.askyesno("确认删除", "确定要删除这个物品吗？"):
            if self.item_controller.delete_item(item_id, self.auth_controller.current_user.user_id):
                messagebox.showinfo("成功", "物品删除成功")
                self.load_items()
            else:
                messagebox.showerror("错误", "删除失败")

class ModifyItemDialog:
    """修改物品对话框。

    构造参数:
    - parent: 父窗口
    - item_controller: `ItemController`（用于保存修改）
    - auth_controller: `AuthController`（用于权限校验）
    - item_id: 要修改的物品 id（入口参数）
    - on_success: 修改成功后的回调（可选）

    方法 `save_changes` 将调用 `item_controller.modify_item(...)` 并在成功后触发回调。
    """
    def __init__(self, parent, item_controller: ItemController, auth_controller: AuthController, item_id: str, on_success=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("修改物品")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        self.item_controller = item_controller
        self.auth_controller = auth_controller
        self.item_id = item_id
        self.on_success = on_success
        
        self.item = next((i for i in self.item_controller.get_user_items(self.auth_controller.current_user.user_id) 
                         if i.item_id == item_id), None)
        
        if not self.item:
            messagebox.showerror("错误", "物品不存在或无权修改")
            self.dialog.destroy()
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        # 物品名称
        ttk.Label(frame, text="物品名称:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(frame, width=30, font=FontManager.get_font())
        self.name_entry.insert(0, self.item.item_name)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 物品描述
        ttk.Label(frame, text="物品描述:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_text = scrolledtext.ScrolledText(frame, width=40, height=8, font=FontManager.get_font())
        self.desc_text.insert("1.0", self.item.description)
        self.desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 联系方式
        ttk.Label(frame, text="联系方式:", font=FontManager.get_chinese_font()).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.contact_entry = ttk.Entry(frame, width=30, font=FontManager.get_font())
        self.contact_entry.insert(0, self.item.contact_info)
        self.contact_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 状态
        ttk.Label(frame, text="状态:", font=FontManager.get_chinese_font()).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value=self.item.status)
        status_combo = ttk.Combobox(frame, textvariable=self.status_var, 
                                   values=["已发布", "已交易", "已下架"], state="readonly", font=FontManager.get_font())
        status_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_changes(self):
        """读取表单并提交物品修改。

        输入: 表单字段（name、description、contact_info、status）；
        输出/副作用: 成功 -> 持久化修改并触发回调/关闭对话框；失败 -> 错误提示。
        """
        item_name = self.name_entry.get().strip()
        item_desc = self.desc_text.get("1.0", tk.END).strip()
        contact_info = self.contact_entry.get().strip()
        status = self.status_var.get()
        
        if not all([item_name, item_desc, contact_info]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if self.item_controller.modify_item(
            self.item_id,
            self.auth_controller.current_user.user_id,
            item_name=item_name,
            description=item_desc,
            contact_info=contact_info,
            status=status
        ):
            messagebox.showinfo("成功", "物品信息修改成功")
            if self.on_success:
                self.on_success()
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "修改失败")

class DemandPublishDialog:
    """发布需求对话框。

    构造参数:
    - parent
    - demand_controller: `DemandController`（用于 add_demand）
    - type_controller: `TypeController`（用于类型选择）
    - auth_controller: `AuthController`（获取当前用户 id）

    输入/输出: 将用户输入的需求描述与联系方式组合并通过 `demand_controller.add_demand` 持久化。
    """
    def __init__(self, parent, demand_controller: DemandController, type_controller: TypeController, auth_controller: AuthController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("发布需求")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        
        self.demand_controller = demand_controller
        self.type_controller = type_controller
        self.auth_controller = auth_controller
        
        self.setup_ui()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        # 需求类型
        ttk.Label(frame, text="需求类型:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar()
        types = self.type_controller.get_all_types()
        type_names = [t.type_name for t in types]
        self.type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=type_names, state="readonly", font=FontManager.get_font())
        self.type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        if type_names:
            self.type_combo.set(type_names[0])
        
        # 需求描述
        ttk.Label(frame, text="需求描述:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_text = scrolledtext.ScrolledText(frame, width=40, height=6, font=FontManager.get_font())
        self.desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 联系方式 - 新增
        ttk.Label(frame, text="联系方式:", font=FontManager.get_chinese_font()).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.contact_entry = ttk.Entry(frame, width=30, font=FontManager.get_font())
        self.contact_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="发布", command=self.publish_demand).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def publish_demand(self):
        """提交需求：收集类型、描述、联系方式并调用 `demand_controller.add_demand`。"""
        demand_type = self.type_var.get()
        description = self.desc_text.get("1.0", tk.END).strip()
        contact_info = self.contact_entry.get().strip()
        
        if not all([demand_type, description, contact_info]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        # 在需求描述中包含联系方式
        full_description = f"{description}\n联系方式: {contact_info}"
        
        if self.demand_controller.add_demand(
            demand_type=demand_type,
            description=full_description,
            publisher_id=self.auth_controller.current_user.user_id
        ):
            messagebox.showinfo("成功", "需求发布成功！")
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "发布失败")

class DemandsDialog:
    """展示所有需求的界面（赏金客栈）。

    构造参数: parent, demand_controller
    输出: 在 Treeview 中列出所有需求；双击可查看详情。
    """
    def __init__(self, parent, demand_controller: DemandController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("赏金客栈")
        self.dialog.geometry("700x400")
        
        self.demand_controller = demand_controller
        
        self.setup_ui()
        self.load_demands()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        main_frame = ttk.Frame(container, padding="10")
        main_frame.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
        # 需求列表
        columns = ("类型", "描述", "发布时间")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.column("描述", width=400)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 主列：tree + scrollbar，侧边操作栏纵向排列
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # place scrollbar next to tree, before sidebar
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        sidebar = ttk.Frame(main_frame)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))

        ttk.Button(sidebar, text="刷新", command=self.load_demands).pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Button(sidebar, text="关闭", command=self.dialog.destroy).pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # 绑定双击事件查看详情
        self.tree.bind("<Double-1>", self.show_demand_details)
    
    def load_demands(self):
        """从 `demand_controller` 加载所有需求并显示在列表中。"""
        # 清空现有结果
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        demands = self.demand_controller.get_all_demands()
        
        for demand in demands:
            # 截断描述以适合显示
            short_desc = demand.description[:80] + "..." if len(demand.description) > 80 else demand.description
            self.tree.insert("", tk.END, values=(
                demand.demand_type,
                short_desc,
                demand.create_time
            ), tags=(demand.demand_id,))
    
    def show_demand_details(self, event):
        """在对话框中弹出选中需求的详细信息窗口。"""
        selection = self.tree.selection()
        if not selection:
            return
        
        demand_id = self.tree.item(selection[0], "tags")[0]
        demands = self.demand_controller.get_all_demands()
        demand = next((d for d in demands if d.demand_id == demand_id), None)
        
        if demand:
            detail_dialog = tk.Toplevel(self.dialog)
            detail_dialog.title("需求详情")
            detail_dialog.geometry("500x300")
            
            container = ttk.Frame(detail_dialog)
            container.pack(fill=tk.BOTH, expand=True)
            frame = ttk.Frame(container, padding="20")
            frame.pack(anchor=tk.CENTER)
            
            ttk.Label(frame, text="需求类型:", font=FontManager.get_chinese_font(12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
            ttk.Label(frame, text=demand.demand_type, font=FontManager.get_font(12)).grid(row=0, column=1, sticky=tk.W, pady=5)
            
            ttk.Label(frame, text="需求描述:", font=FontManager.get_chinese_font(12, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
            desc_text = scrolledtext.ScrolledText(frame, width=50, height=10, font=FontManager.get_font(10))
            desc_text.insert("1.0", demand.description)
            desc_text.config(state=tk.DISABLED)
            desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
            
            ttk.Label(frame, text="发布时间:", font=FontManager.get_chinese_font(12, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
            ttk.Label(frame, text=demand.create_time, font=FontManager.get_font(12)).grid(row=2, column=1, sticky=tk.W, pady=5)
            
            ttk.Button(frame, text="关闭", command=detail_dialog.destroy).grid(row=3, column=1, sticky=tk.E, pady=10)

class UserInfoDialog:
    """用户个人信息管理对话框。

    构造参数: parent, auth_controller
    功能: 修改用户联系方式和密码（如提供），通过 `auth_controller.modify_user_info` 持久化变更。
    """
    def __init__(self, parent, auth_controller: AuthController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("个人信息管理")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        self.auth_controller = auth_controller
        
        self.setup_ui()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        user = self.auth_controller.current_user
        
        # 用户名（不可修改）
        ttk.Label(frame, text="用户名:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=user.username, font=FontManager.get_font()).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 角色
        ttk.Label(frame, text="角色:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=user.role, font=FontManager.get_font()).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 新密码
        ttk.Label(frame, text="新密码:", font=FontManager.get_chinese_font()).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame, width=20, show="*", font=FontManager.get_font())
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 联系方式
        ttk.Label(frame, text="联系方式:", font=FontManager.get_chinese_font()).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.contact_entry = ttk.Entry(frame, width=20, font=FontManager.get_font())
        self.contact_entry.insert(0, user.contact_info)
        self.contact_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_changes(self):
        """保存用户信息变更：读取密码与联系方式并调用 `auth_controller.modify_user_info`。"""
        password = self.password_entry.get().strip()
        contact_info = self.contact_entry.get().strip()
        
        if not contact_info:
            messagebox.showerror("错误", "联系方式不能为空")
            return
        
        if self.auth_controller.modify_user_info(
            password=password if password else None,
            contact_info=contact_info
        ):
            messagebox.showinfo("成功", "个人信息修改成功")
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "修改失败")

class TypeApplicationDialog:
    """申请修改物品类型的对话框。

    入口参数: parent, application_controller, type_controller, auth_controller
    用户输入申请内容并提交，最终调用 `application_controller.add_application` 创建申请记录（输出/副作用）。
    """
    def __init__(self, parent, application_controller: ApplicationController, type_controller: TypeController, auth_controller: AuthController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("申请修改物品类型")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        self.application_controller = application_controller
        self.type_controller = type_controller
        self.auth_controller = auth_controller
        
        self.setup_ui()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        # 申请类型
        ttk.Label(frame, text="申请类型:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.app_type_var = tk.StringVar(value="添加新类型")
        app_type_combo = ttk.Combobox(frame, textvariable=self.app_type_var, 
                                     values=["添加新类型", "修改现有类型"], state="readonly", font=FontManager.get_font())
        app_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        app_type_combo.bind("<<ComboboxSelected>>", self.on_app_type_changed)
        
        # 类型选择（仅修改时显示）
        self.type_frame = ttk.Frame(frame)
        self.type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.type_frame, text="选择类型:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W)
        self.type_var = tk.StringVar()
        types = self.type_controller.get_all_types()
        type_names = [t.type_name for t in types]
        self.type_combo = ttk.Combobox(self.type_frame, textvariable=self.type_var, values=type_names, state="readonly", font=FontManager.get_font())
        self.type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        if type_names:
            self.type_combo.set(type_names[0])
        
        self.type_frame.grid_remove()  # 初始隐藏
        
        # 申请内容
        ttk.Label(frame, text="申请内容:", font=FontManager.get_chinese_font()).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.content_text = scrolledtext.ScrolledText(frame, width=40, height=8, font=FontManager.get_font())
        self.content_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="提交申请", command=self.submit_application).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def on_app_type_changed(self, event=None):
        if self.app_type_var.get() == "修改现有类型":
            self.type_frame.grid()
        else:
            self.type_frame.grid_remove()
    
    def submit_application(self):
        """提交类型修改/新增申请，将整理后的内容传递给 `application_controller.add_application`。"""
        app_type = self.app_type_var.get()
        content = self.content_text.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showerror("错误", "请填写申请内容")
            return
        
        if app_type == "修改现有类型":
            selected_type = self.type_var.get()
            if not selected_type:
                messagebox.showerror("错误", "请选择要修改的类型")
                return
            content = f"修改类型 '{selected_type}': {content}"
        else:
            content = f"添加新类型: {content}"
        
        if self.application_controller.add_application(
            "修改物品类型",
            content,
            self.auth_controller.current_user.user_id
        ):
            messagebox.showinfo("成功", "申请已提交，等待管理员审批")
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "申请失败")

class TypeManagementDialog:
    """类型管理对话框（管理员专用）。

    功能: 列表显示所有类型，支持添加/修改/删除。删除时会检查是否有物品在使用该类型（防止误删）。
    入口参数: parent, type_controller, application_controller, auth_controller
    """
    def __init__(self, parent, type_controller: TypeController, application_controller: ApplicationController, auth_controller: AuthController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("类型管理")
        self.dialog.geometry("600x500")
        
        self.type_controller = type_controller
        self.application_controller = application_controller
        self.auth_controller = auth_controller
        
        self.setup_ui()
        self.load_types()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        main_frame = ttk.Frame(container, padding="10")
        main_frame.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
        # 类型列表
        columns = ("类型名称", "属性")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="添加类型", command=self.add_type).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="修改类型", command=self.modify_type).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除类型", command=self.delete_type).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.load_types).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_types(self):
        """加载并显示所有物品类型（从 type_controller 获取）。"""
        # 清空现有结果
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        types = self.type_controller.get_all_types()
        
        for item_type in types:
            self.tree.insert("", tk.END, values=(
                item_type.type_name,
                ", ".join(item_type.attributes)
            ), tags=(item_type.type_id,))
    
    def get_selected_type_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个类型")
            return None
        return self.tree.item(selection[0], "tags")[0]
    
    def add_type(self):
        AddTypeDialog(self.dialog, self.type_controller, self.load_types)
    
    def modify_type(self):
        type_id = self.get_selected_type_id()
        if type_id:
            ModifyTypeDialog(self.dialog, self.type_controller, type_id, self.load_types)
    
    def delete_type(self):
        """删除所选类型（管理员操作）。

        入口: 选择的类型 id；处理: 检查是否有物品正在使用该类型，若无则从类型列表中移除并保存。
        输出/副作用: 修改 `item_types.json` 并刷新列表。
        """
        type_id = self.get_selected_type_id()
        if not type_id:
            return
        
        if messagebox.askyesno("确认删除", "确定要删除这个类型吗？"):
            types = self.type_controller.get_all_types()
            type_to_delete = next((t for t in types if t.type_id == type_id), None)
            
            if type_to_delete:
                # 检查是否有物品使用此类型
                from controllers import ItemController
                item_controller = ItemController(self.type_controller.data_manager)
                items_using_type = [item for item in item_controller.items if item.item_type == type_to_delete.type_name]
                
                if items_using_type:
                    messagebox.showerror("错误", f"无法删除该类型，有 {len(items_using_type)} 个物品正在使用此类型")
                    return
                
                # 删除类型
                types.remove(type_to_delete)
                self.type_controller.data_manager.save_data("item_types", types)
                messagebox.showinfo("成功", "类型删除成功")
                self.load_types()
            else:
                messagebox.showerror("错误", "类型不存在")

class AddTypeDialog:
    """添加类型对话框。

    用户在文本框中按行输入属性名，点击添加会调用 `type_controller.add_item_type(type_name, attributes)`。
    """
    def __init__(self, parent, type_controller: TypeController, on_success=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("添加类型")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        self.type_controller = type_controller
        self.on_success = on_success
        
        self.setup_ui()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        # 类型名称
        ttk.Label(frame, text="类型名称:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(frame, width=30, font=FontManager.get_font())
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 属性列表
        ttk.Label(frame, text="属性列表:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.attributes_text = scrolledtext.ScrolledText(frame, width=30, height=8, font=FontManager.get_font())
        self.attributes_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="(每行一个属性)", font=FontManager.get_chinese_font(9)).grid(row=2, column=1, sticky=tk.W, pady=0)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="添加", command=self.add_type).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_type(self):
        """收集类型名称与属性列表并提交给 `type_controller.add_item_type`。"""
        type_name = self.name_entry.get().strip()
        attributes_text = self.attributes_text.get("1.0", tk.END).strip()
        
        if not type_name:
            messagebox.showerror("错误", "请输入类型名称")
            return
        
        attributes = [attr.strip() for attr in attributes_text.split('\n') if attr.strip()]
        
        if self.type_controller.add_item_type(type_name, attributes):
            messagebox.showinfo("成功", "类型添加成功")
            if self.on_success:
                self.on_success()
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "类型名称已存在")

class ModifyTypeDialog:
    """修改类型对话框。

    入口参数: type_id（要修改的类型 id），界面会加载当前名称与属性供编辑。
    保存时调用 `type_controller.modify_item_type(type_id, type_name, attributes)`。
    """
    def __init__(self, parent, type_controller: TypeController, type_id: str, on_success=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("修改类型")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        self.type_controller = type_controller
        self.type_id = type_id
        self.on_success = on_success
        
        self.type_obj = next((t for t in self.type_controller.get_all_types() if t.type_id == type_id), None)
        
        if not self.type_obj:
            messagebox.showerror("错误", "类型不存在")
            self.dialog.destroy()
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        # 类型名称
        ttk.Label(frame, text="类型名称:", font=FontManager.get_chinese_font()).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(frame, width=30, font=FontManager.get_font())
        self.name_entry.insert(0, self.type_obj.type_name)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 属性列表
        ttk.Label(frame, text="属性列表:", font=FontManager.get_chinese_font()).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.attributes_text = scrolledtext.ScrolledText(frame, width=30, height=8, font=FontManager.get_font())
        self.attributes_text.insert("1.0", "\n".join(self.type_obj.attributes))
        self.attributes_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="(每行一个属性)", font=FontManager.get_chinese_font(9)).grid(row=2, column=1, sticky=tk.W, pady=0)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_changes(self):
        """保存类型修改并调用控制器持久化。"""
        type_name = self.name_entry.get().strip()
        attributes_text = self.attributes_text.get("1.0", tk.END).strip()
        
        if not type_name:
            messagebox.showerror("错误", "请输入类型名称")
            return
        
        attributes = [attr.strip() for attr in attributes_text.split('\n') if attr.strip()]
        
        if self.type_controller.modify_item_type(self.type_id, type_name, attributes):
            messagebox.showinfo("成功", "类型修改成功")
            if self.on_success:
                self.on_success()
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "修改失败")

class ApplicationApprovalDialog:
    """管理员审批申请的对话框。

    入口参数: parent, application_controller, auth_controller, type_controller
    功能: 列出所有申请并支持批准/拒绝。批准可能触发其他控制器的变更（例如将用户升级为管理员）。
    """
    def __init__(self, parent, application_controller: ApplicationController, auth_controller: AuthController, type_controller: TypeController):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("申请审批")
        self.dialog.geometry("700x500")
        
        self.application_controller = application_controller
        self.auth_controller = auth_controller
        self.type_controller = type_controller
        
        self.setup_ui()
        self.load_applications()
    
    def setup_ui(self):
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        main_frame = ttk.Frame(container, padding="10")
        main_frame.pack(anchor=tk.CENTER, fill=tk.BOTH)
        
        # 申请列表
        columns = ("申请类型", "申请内容", "申请人", "申请时间", "状态")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("申请内容", width=200)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="批准", command=self.approve_application).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="拒绝", command=self.reject_application).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看详情", command=self.show_application_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.load_applications).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_applications(self):
        # 清空现有结果
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        applications = self.application_controller.applications
        
        for app in applications:
            # 获取申请人用户名
            from controllers import AuthController
            auth_controller = AuthController(self.application_controller.data_manager)
            applicant = next((u for u in auth_controller.users if u.user_id == app.applicant_id), None)
            applicant_name = applicant.username if applicant else "未知用户"
            
            self.tree.insert("", tk.END, values=(
                app.app_type,
                app.content[:50] + "..." if len(app.content) > 50 else app.content,
                applicant_name,
                app.create_time,
                app.app_status
            ), tags=(app.application_id,))
    
    def get_selected_application_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个申请")
            return None
        return self.tree.item(selection[0], "tags")[0]
    
    def approve_application(self):
        """批准选中的申请。

        过程: 根据申请类型执行相应的操作（例如将申请人设为管理员），然后调用
        `application_controller.process_application(app_id, "通过")` 更新申请状态并持久化。
        """
        app_id = self.get_selected_application_id()
        if not app_id:
            return
        
        application = next((app for app in self.application_controller.applications if app.application_id == app_id), None)
        if not application:
            messagebox.showerror("错误", "申请不存在")
            return
        
        if application.app_status != "待处理":
            messagebox.showwarning("警告", "该申请已被处理")
            return
        
        # 处理不同类型的申请
        if application.app_type == "成为管理员":
            # 更新用户角色
            from controllers import AuthController
            auth_controller = AuthController(self.application_controller.data_manager)
            user = next((u for u in auth_controller.users if u.user_id == application.applicant_id), None)
            if user:
                user.role = "管理员"
                auth_controller.data_manager.save_data("users", auth_controller.users)
        
        elif application.app_type == "修改物品类型":
            # 这里可以添加处理类型修改申请的逻辑
            # 由于类型修改申请内容较复杂，可能需要更复杂的解析和处理
            pass
        
        if self.application_controller.process_application(app_id, "通过"):
            messagebox.showinfo("成功", "申请已批准")
            self.load_applications()
        else:
            messagebox.showerror("错误", "操作失败")
    
    def reject_application(self):
        app_id = self.get_selected_application_id()
        if not app_id:
            return
        
        application = next((app for app in self.application_controller.applications if app.application_id == app_id), None)
        if not application:
            messagebox.showerror("错误", "申请不存在")
            return
        
        if application.app_status != "待处理":
            messagebox.showwarning("警告", "该申请已被处理")
            return
        
        if self.application_controller.process_application(app_id, "拒绝"):
            messagebox.showinfo("成功", "申请已拒绝")
            self.load_applications()
        else:
            messagebox.showerror("错误", "操作失败")
    
    def show_application_details(self):
        app_id = self.get_selected_application_id()
        if not app_id:
            return
        
        application = next((app for app in self.application_controller.applications if app.application_id == app_id), None)
        if not application:
            messagebox.showerror("错误", "申请不存在")
            return
        
        detail_dialog = tk.Toplevel(self.dialog)
        detail_dialog.title("申请详情")
        detail_dialog.geometry("500x400")
        
        container = ttk.Frame(detail_dialog)
        container.pack(fill=tk.BOTH, expand=True)
        frame = ttk.Frame(container, padding="20")
        frame.pack(anchor=tk.CENTER)
        
        # 获取申请人信息
        from controllers import AuthController
        auth_controller = AuthController(self.application_controller.data_manager)
        applicant = next((u for u in auth_controller.users if u.user_id == application.applicant_id), None)
        
        ttk.Label(frame, text="申请类型:", font=FontManager.get_chinese_font(12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=application.app_type, font=FontManager.get_font(12)).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="申请人:", font=FontManager.get_chinese_font(12, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=applicant.username if applicant else "未知用户", font=FontManager.get_font(12)).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="申请内容:", font=FontManager.get_chinese_font(12, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        content_text = scrolledtext.ScrolledText(frame, width=50, height=15, font=FontManager.get_font(10))
        content_text.insert("1.0", application.content)
        content_text.config(state=tk.DISABLED)
        content_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(frame, text="申请状态:", font=FontManager.get_chinese_font(12, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=application.app_status, font=FontManager.get_font(12)).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="申请时间:", font=FontManager.get_chinese_font(12, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=application.create_time, font=FontManager.get_font(12)).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(frame, text="关闭", command=detail_dialog.destroy).grid(row=5, column=1, sticky=tk.E, pady=10)