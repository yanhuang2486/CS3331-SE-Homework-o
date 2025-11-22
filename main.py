import tkinter as tk
from tkinter import ttk
from controllers import DataManager, AuthController, ItemController, TypeController, DemandController, ApplicationController
from gui_ui import LoginUI, MainUI, FontManager

class ResurrectionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("“复活”物品流通平台")
        self.root.geometry("800x600")
        
        # 设置字体
        self.setup_fonts()
        
        # 初始化数据管理和控制器
        self.data_manager = DataManager("data")
        self.auth_controller = AuthController(self.data_manager)
        self.item_controller = ItemController(self.data_manager)
        self.type_controller = TypeController(self.data_manager)
        self.demand_controller = DemandController(self.data_manager)
        self.application_controller = ApplicationController(self.data_manager)
        
        # 显示登录界面
        self.show_login()
    
    def setup_fonts(self):
        # 设置默认字体
        default_font = FontManager.get_font()
        self.root.option_add("*Font", default_font)
        
        # 设置特定组件的字体
        style = ttk.Style()
        style.configure("TLabel", font=FontManager.get_chinese_font())
        style.configure("TButton", font=FontManager.get_chinese_font())
        style.configure("TEntry", font=FontManager.get_font())
        style.configure("TCombobox", font=FontManager.get_font())
    
    def show_login(self):
        # 清除现有内容
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.login_ui = LoginUI(self.root, self.auth_controller, self.on_login_success)
    
    def on_login_success(self):
        # 登录成功后显示主界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.main_ui = MainUI(
            self.root, 
            self.auth_controller, 
            self.item_controller, 
            self.type_controller, 
            self.demand_controller, 
            self.application_controller,
            self.on_logout
        )
    
    def on_logout(self):
        # 退出登录后返回登录界面
        self.show_login()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ResurrectionApp()
    app.run()