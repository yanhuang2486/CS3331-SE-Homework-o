'''
作者：yanhuang2486
本文件目的：为“复活”软件定义实体类
'''
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any

class User:
    def __init__(self, user_id: str, username: str, password: str, contact_info: str, role: str = "普通用户"):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.contact_info = contact_info
        self.role = role
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password": self.password,
            "contact_info": self.contact_info,
            "role": self.role
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            password=data["password"],
            contact_info=data["contact_info"],
            role=data.get("role", "普通用户")
        )

class Item:
    def __init__(self, item_id: str, item_name: str, description: str, item_type: str, 
                 contact_info: str, owner_id: str, image: str = "", status: str = "已发布"):
        self.item_id = item_id
        self.item_name = item_name
        self.description = description
        self.item_type = item_type
        self.image = image
        self.contact_info = contact_info
        self.status = status
        self.owner_id = owner_id
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "description": self.description,
            "item_type": self.item_type,
            "image": self.image,
            "contact_info": self.contact_info,
            "status": self.status,
            "owner_id": self.owner_id,
            "create_time": self.create_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        item = cls(
            item_id=data["item_id"],
            item_name=data["item_name"],
            description=data["description"],
            item_type=data["item_type"],
            contact_info=data["contact_info"],
            owner_id=data["owner_id"],
            image=data.get("image", ""),
            status=data.get("status", "已发布")
        )
        item.create_time = data.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return item

class ItemType:
    def __init__(self, type_id: str, type_name: str, attributes: List[str]):
        self.type_id = type_id
        self.type_name = type_name
        self.attributes = attributes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_id": self.type_id,
            "type_name": self.type_name,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemType':
        return cls(
            type_id=data["type_id"],
            type_name=data["type_name"],
            attributes=data["attributes"]
        )

class Demand:
    def __init__(self, demand_id: str, demand_type: str, description: str, publisher_id: str):
        self.demand_id = demand_id
        self.demand_type = demand_type
        self.description = description
        self.publisher_id = publisher_id
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "demand_id": self.demand_id,
            "demand_type": self.demand_type,
            "description": self.description,
            "publisher_id": self.publisher_id,
            "create_time": self.create_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Demand':
        demand = cls(
            demand_id=data["demand_id"],
            demand_type=data["demand_type"],
            description=data["description"],
            publisher_id=data["publisher_id"]
        )
        demand.create_time = data.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return demand

class Application:
    def __init__(self, application_id: str, app_type: str, content: str, applicant_id: str, app_status: str = "待处理"):
        self.application_id = application_id
        self.app_type = app_type
        self.content = content
        self.app_status = app_status
        self.applicant_id = applicant_id
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "application_id": self.application_id,
            "app_type": self.app_type,
            "content": self.content,
            "app_status": self.app_status,
            "applicant_id": self.applicant_id,
            "create_time": self.create_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Application':
        application = cls(
            application_id=data["application_id"],
            app_type=data["app_type"],
            content=data["content"],
            applicant_id=data["applicant_id"],
            app_status=data.get("app_status", "待处理")
        )
        application.create_time = data.get("create_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return application