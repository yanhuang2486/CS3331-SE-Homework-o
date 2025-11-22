"""
controllers.py
作者：yanhuang2486
本文件目的：为“复活”软件实现业务逻辑控制器
----------------
控制器层，实现对数据的读写和业务逻辑调用。

该模块封装了对磁盘 JSON 数据的加载/保存（通过 DataManager），以及对
用户、物品、物品类型、需求和申请等实体的增删改查操作。

全局/模块级说明：
- 数据目录（DataManager.data_dir）：默认为 `data`，用于保存所有 JSON 数据文件。

输入数据（来自 GUI 或其他上层模块）：
- 大多数方法以基础 Python 类型接收参数（例如 username/password/item_name 等），
    控制器负责将这些数据组织到实体对象并持久化。

输出数据（返回值或持久化结果）：
- 多数操作返回布尔值表示成功/失败；查询方法返回实体对象列表（List[Entity]）。

入口参数注释示例（见各方法 docstring）将标注每个参数的含义和返回值。
"""

import json
import os
import uuid
from typing import List, Dict, Any, Optional
from entities import User, Item, ItemType, Demand, Application

class DataManager:
    """数据管理器

    负责将内存中的实体列表序列化为 JSON 文件写入 data_dir，
    以及从 data_dir 中读取 JSON 并反序列化为实体对象列表。

    参数:
    - data_dir: 存储 JSON 文件的目录（默认 'data'）。
    属性/全局影响:
    - 在初始化时会确保 data_dir 目录存在（会创建目录）。
    """
    def __init__(self, data_dir: str = "data"):
        # 指向数据目录（相对路径或绝对路径），此目录存放 users.json/items.json 等文件
        self.data_dir = data_dir
        # 确保数据目录存在（若不存在则创建）
        os.makedirs(data_dir, exist_ok=True)
        
    def save_data(self, filename: str, data: List[Any]):
        """将实体列表保存为 JSON 文件。

        参数:
        - filename: 不含扩展名的文件名（例如 'users' -> 保存为 data/users.json）
        - data: 实体对象列表，要求每个对象实现 `to_dict()` 方法以便序列化。
        返回: None（成功写入文件或抛出异常）
        """
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            # 将实体对象列表转换为 dict 列表后写入 JSON，使用 ensure_ascii=False 保持中文
            json.dump([item.to_dict() for item in data], f, ensure_ascii=False, indent=2)
    
    def load_data(self, filename: str, entity_class):
        """从 JSON 文件中加载实体对象列表。

        参数:
        - filename: 不含扩展名的文件名（例如 'items'）
        - entity_class: 用于反序列化的实体类（该类必须实现 `from_dict` 类方法）

        返回:
        - 成功：实体对象列表（List[entity_class]）
        - 若文件不存在：返回空列表（[]）
        """
        filepath = os.path.join(self.data_dir, f"{filename}.json")
        if not os.path.exists(filepath):
            return []

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 将 JSON 中的字典转为实体对象
            return [entity_class.from_dict(item) for item in data]

class AuthController:
    """用户认证与用户信息管理控制器。

    主要职责：注册用户、登录/登出、修改当前用户信息。

    关键属性：
    - data_manager: DataManager 实例，用于加载/保存 users 列表
    - users: 当前内存中的 User 列表（从 data/users.json 加载）
    - current_user: 当前登录的 User 对象，未登录时为 None
    """
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        # 当前登录用户（User 对象），默认为 None 表示未登录
        self.current_user = None
        # 从磁盘加载用户列表（如果没有则返回空列表）
        self.users = self.data_manager.load_data("users", User)
        # 确保存在一个初始管理员账号
        self._initialize_admin()
    
    def _initialize_admin(self):
        """初始化管理员账号（如果 users 数据中没有 admin 则创建）。

        无输入参数，直接修改 `self.users` 并持久化到磁盘（如果创建了管理员）。
        """
        admin_exists = any(user.username == "admin" for user in self.users)
        if not admin_exists:
            admin_user = User(
                user_id=str(uuid.uuid4()),
                username="admin",
                password="123456",
                contact_info="系统管理员",
                role="管理员"
            )
            self.users.append(admin_user)
            # 保存 users 到 data/users.json
            self.data_manager.save_data("users", self.users)
    
    def register(self, username: str, password: str, contact_info: str) -> bool:
        """注册新用户。

        输入参数:
        - username: 用户名（字符串），需唯一
        - password: 密码（字符串）
        - contact_info: 联系方式（字符串）

        返回:
        - True: 注册成功（并已持久化到 data/users.json）
        - False: 用户名已存在，注册失败
        """
        if any(user.username == username for user in self.users):
            return False

        new_user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            password=password,
            contact_info=contact_info,
            role="普通用户"
        )
        self.users.append(new_user)
        # 将更新后的用户列表保存到磁盘
        self.data_manager.save_data("users", self.users)
        return True
    
    def login(self, username: str, password: str) -> bool:
        """登录验证。

        输入: username, password
        如果匹配成功，将 `self.current_user` 设置为对应 User 并返回 True，否则返回 False。
        """
        user = next((u for u in self.users if u.username == username and u.password == password), None)
        if user:
            self.current_user = user
            return True
        return False
    
    def logout(self):
        """登出：清除当前登录用户。"""
        self.current_user = None
    
    def modify_user_info(self, password: str = None, contact_info: str = None) -> bool:
        """修改当前登录用户的信息。

        输入参数（均为可选）：
        - password: 新密码（若提供则更新）
        - contact_info: 新联系方式（若提供则更新）

        返回:
        - True: 修改成功并已持久化
        - False: 当前没有登录用户（无法修改）
        """
        if not self.current_user:
            return False

        if password:
            self.current_user.password = password
        if contact_info:
            self.current_user.contact_info = contact_info

        # 保存 users.json
        self.data_manager.save_data("users", self.users)
        return True

class ItemController:
    """物品管理控制器

    负责物品的增删改查、搜索等操作。数据持久化存于 data/items.json。
    """
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        # 所有物品的内存列表，从 data/items.json 加载（若文件不存在则为空列表）
        self.items = self.data_manager.load_data("items", Item)
    
    def add_item(self, item_name: str, description: str, item_type: str, 
                 contact_info: str, owner_id: str, image: str = "") -> bool:
        """添加新物品。

        参数:
        - item_name: 物品名称
        - description: 物品描述（可以包含属性前缀）
        - item_type: 物品类型名称（如 '书籍'）
        - contact_info: 联系方式
        - owner_id: 发布者的 user_id
        - image: 可选图片路径或标识（目前未使用）

        返回: True（成功并已持久化）
        """
        new_item = Item(
            item_id=str(uuid.uuid4()),
            item_name=item_name,
            description=description,
            item_type=item_type,
            contact_info=contact_info,
            owner_id=owner_id,
            image=image
        )
        self.items.append(new_item)
        # 保存 items.json
        self.data_manager.save_data("items", self.items)
        return True
    
    def delete_item(self, item_id: str, user_id: str) -> bool:
        """删除物品（仅允许物品所有者删除）。

        参数:
        - item_id: 要删除的物品 id
        - user_id: 当前操作用户 id（必须与物品 owner_id 匹配）

        返回: True 表示删除成功并已保存；False 表示未找到或无权限删除。
        """
        item = next((i for i in self.items if i.item_id == item_id and i.owner_id == user_id), None)
        if item:
            self.items.remove(item)
            self.data_manager.save_data("items", self.items)
            return True
        return False
    
    def modify_item(self, item_id: str, user_id: str, **kwargs) -> bool:
        """修改物品信息（仅允许所有者修改）。

        参数:
        - item_id: 物品 id
        - user_id: 操作者 id（必须与 item.owner_id 匹配）
        - kwargs: 要更新的字段键值对（例如 item_name, description, contact_info, status 等）

        返回: True 表示修改成功并已持久化，False 表示物品不存在或无权限。
        """
        item = next((i for i in self.items if i.item_id == item_id and i.owner_id == user_id), None)
        if not item:
            return False

        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)

        self.data_manager.save_data("items", self.items)
        return True
    
    def get_all_items(self) -> List[Item]:
        """返回所有状态为'已发布'的物品列表（用于在闲置集市中展示）。"""
        return [item for item in self.items if item.status == "已发布"]
    
    def search_items(self, item_type: str = None, keyword: str = None) -> List[Item]:
        """搜索物品。

        输入参数:
        - item_type: 可选，按类型过滤（若为 None 或 '所有类型' 则不过滤）
        - keyword: 可选，按物品名称或描述进行包含匹配

        返回: 符合条件且状态为 '已发布' 的物品列表
        """
        results = self.items

        if item_type and item_type != "所有类型":
            results = [item for item in results if item.item_type == item_type]

        if keyword:
            # 简单的包含匹配（区分大小写），可以根据需要扩展为不区分大小写或正则匹配
            results = [item for item in results 
                      if keyword in item.item_name or keyword in item.description]

        return [item for item in results if item.status == "已发布"]
    
    def get_user_items(self, user_id: str) -> List[Item]:
        """获取指定用户发布的所有物品（包含不同状态）。

        参数: user_id
        返回: 该用户所有物品的列表
        """
        return [item for item in self.items if item.owner_id == user_id]

class TypeController:
    """物品类型管理控制器

    负责维护可用的物品类型及其属性列表（例如书籍包含作者/出版社/ISBN）。
    类型数据保存在 data/item_types.json 中。
    """
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        # 在内存中的 ItemType 列表
        self.item_types = self.data_manager.load_data("item_types", ItemType)
        self._initialize_default_types()
    
    def _initialize_default_types(self):
        """初始化默认类型（仅在数据文件为空时执行），包括常见类别及其属性。

        这会向 item_types.json 中写入默认类型，便于第一次运行时 GUI 有可选项。
        """
        if not self.item_types:
            default_types = [
                ItemType("1", "书籍", ["作者", "出版社", "ISBN", "新旧程度"]),
                ItemType("2", "宿舍用品", ["品牌", "新旧程度", "尺寸"]),
                ItemType("3", "电子产品", ["品牌", "型号", "新旧程度"]),
                ItemType("4", "服装", ["品牌", "尺码", "新旧程度"]),
                ItemType("5", "体育用品", ["品牌", "新旧程度"]),
                ItemType("6", "其他", ["备注"])
            ]
            self.item_types.extend(default_types)
            self.data_manager.save_data("item_types", self.item_types)
    
    def add_item_type(self, type_name: str, attributes: List[str]) -> bool:
        """添加新的物品类型。

        参数:
        - type_name: 新类型名称（需唯一）
        - attributes: 属性名列表（例如 ['品牌', '型号']）

        返回: True 表示添加成功并保存，False 表示类型名称已存在
        """
        if any(t.type_name == type_name for t in self.item_types):
            return False

        new_type = ItemType(
            type_id=str(uuid.uuid4()),
            type_name=type_name,
            attributes=attributes
        )
        self.item_types.append(new_type)
        self.data_manager.save_data("item_types", self.item_types)
        return True
    
    def modify_item_type(self, type_id: str, type_name: str = None, attributes: List[str] = None) -> bool:
        """修改物品类型的名称或属性列表。

        参数:
        - type_id: 要修改的类型 id
        - type_name: 可选，新类型名称
        - attributes: 可选，新属性列表

        返回: True/False 表示是否修改成功并已保存
        """
        item_type = next((t for t in self.item_types if t.type_id == type_id), None)
        if not item_type:
            return False

        if type_name:
            item_type.type_name = type_name
        if attributes:
            item_type.attributes = attributes

        self.data_manager.save_data("item_types", self.item_types)
        return True
    
    def get_all_types(self) -> List[ItemType]:
        """返回当前所有注册的物品类型列表（用于界面展示类型选项）。"""
        return self.item_types

class DemandController:
    """需求发布/查询控制器

    负责需求（寻找物品等）的发布与查询，数据保存在 data/demands.json。
    """
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.demands = self.data_manager.load_data("demands", Demand)
    
    def add_demand(self, demand_type: str, description: str, publisher_id: str) -> bool:
        """添加一条新的需求记录。

        参数:
        - demand_type: 需求类型
        - description: 需求描述
        - publisher_id: 发布者 user_id

        返回: True（成功并持久化）
        """
        new_demand = Demand(
            demand_id=str(uuid.uuid4()),
            demand_type=demand_type,
            description=description,
            publisher_id=publisher_id
        )
        self.demands.append(new_demand)
        self.data_manager.save_data("demands", self.demands)
        return True
    
    def get_all_demands(self) -> List[Demand]:
        """返回所有需求列表（按创建顺序）。"""
        return self.demands
    
    def get_user_demands(self, user_id: str) -> List[Demand]:
        """返回指定用户发布的需求列表。"""
        return [demand for demand in self.demands if demand.publisher_id == user_id]

class ApplicationController:
    """管理用户提交的各种申请（如申请成为管理员、类型修改申请等）。

    数据保存在 data/applications.json。
    """
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.applications = self.data_manager.load_data("applications", Application)
    
    def add_application(self, app_type: str, content: str, applicant_id: str) -> bool:
        """提交一个新的申请记录。

        参数:
        - app_type: 申请类型（例如 '成为管理员'）
        - content: 申请内容
        - applicant_id: 申请人 user_id

        返回: True（成功并保存）
        """
        new_application = Application(
            application_id=str(uuid.uuid4()),
            app_type=app_type,
            content=content,
            applicant_id=applicant_id
        )
        self.applications.append(new_application)
        self.data_manager.save_data("applications", self.applications)
        return True
    
    def get_pending_applications(self) -> List[Application]:
        """返回所有处于'待处理'状态的申请，供管理员审批页面使用。"""
        return [app for app in self.applications if app.app_status == "待处理"]
    
    def process_application(self, application_id: str, status: str) -> bool:
        """处理（更新）指定申请的状态。

        参数:
        - application_id: 目标申请 id
        - status: 新状态（例如 '通过' 或 '拒绝'）

        返回: True 表示成功更新并持久化，False 表示未找到对应申请。
        """
        application = next((app for app in self.applications if app.application_id == application_id), None)
        if not application:
            return False

        application.app_status = status
        self.data_manager.save_data("applications", self.applications)
        return True