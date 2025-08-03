# StudentDormitoryClient/app/api_client.py

import requests


class ApiClient:
    """
    一个专门用于和后端API通信的客户端类。
    它封装了所有HTTP请求的细节，如URL构建、错误处理和超时设置。
    """

    def __init__(self, base_url="http://127.0.0.1:5000/api"):
        """
        初始化API客户端。

        Args:
            base_url (str): 后端API的根地址。
        """
        self.base_url = base_url
        # 使用 requests.Session() 可以复用TCP连接，并保持cookies，效率更高
        self.session = requests.Session()
        # 为所有请求设置一个默认的超时时间（秒）
        self.timeout = 5
        self.current_user = None  # 【核心新增】用于存储当前登录用户的信息

    def login(self, username, password, role):
        """
        调用后端的登录接口。

        Returns:
            dict or None: 如果登录成功，返回包含用户信息的字典；
                          如果失败（网络错误、认证失败等），返回 None。
        """
        try:
            url = f"{self.base_url}/auth/login"
            payload = {'username': username, 'password': password, 'role': role}
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            # 【核心新增】登录成功后，保存用户信息
            if result and 'user' in result:
                self.current_user = result['user']
            return result
        except requests.exceptions.HTTPError as err:
            print(f"登录失败 (HTTP Error): {err.response.status_code} - {err.response.text}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"登录时发生网络错误: {err}")
            return None

    def get_my_profile(self):
        """获取当前登录用户的详细个人资料"""
        if not self.current_user:
            return {"error": "用户未登录"}

        try:
            url = f"{self.base_url}/me/profile"
            # 【核心】在请求头中代入当前用户的认证信息（模拟方式）
            headers = {
                'X-Username': self.current_user['username'],
                'X-Role': self.current_user['role']
            }
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def update_my_profile(self, data: dict):
        """更新当前用户的个人资料（例如电话）"""
        if not self.current_user: return {"error": "用户未登录"}
        try:
            url = f"{self.base_url}/me/profile"
            headers = {'X-Username': self.current_user['username'], 'X-Role': self.current_user['role']}
            response = self.session.put(url, headers=headers, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def change_my_password(self, old_password: str, new_password: str):
        """修改当前用户的密码"""
        if not self.current_user: return {"error": "用户未登录"}
        try:
            url = f"{self.base_url}/me/password"
            headers = {'X-Username': self.current_user['username']}
            payload = {"old_password": old_password, "new_password": new_password}
            response = self.session.put(url, headers=headers, json=payload, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def get_students(self): # 这个方法现在不需要了，因为被 get_unallocated_students 替代
        pass

    def add_student(self, data: dict):
        """添加新学生"""
        try:
            url = f"{self.base_url}/students/"
            response = self.session.post(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def update_student(self, student_id: int, data: dict):
        """修改学生信息"""
        try:
            url = f"{self.base_url}/students/{student_id}"
            response = self.session.put(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def delete_student(self, student_id: int):
        """删除学生"""
        try:
            url = f"{self.base_url}/students/{student_id}"
            response = self.session.delete(url, timeout=self.timeout)
            return response.status_code == 204
        except requests.exceptions.RequestException as err:
            return False

    def get_teachers(self):
        """
        调用后端接口获取所有教师列表。
        """
        try:
            url = f"{self.base_url}/teachers/"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"获取教师列表时发生网络错误: {err}")
            # 返回一个带error键的字典，以符合ApiWorker的预期
            return {"error": str(err)}

    def add_teacher(self, data: dict):
        """调用后端接口添加新教师 (包含登录账户信息)"""
        try:
            url = f"{self.base_url}/teachers/"
            response = self.session.post(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def update_teacher(self, teacher_id: int, data: dict):
        """调用后端接口修改教师信息"""
        try:
            url = f"{self.base_url}/teachers/{teacher_id}"
            response = self.session.put(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def delete_teacher(self, teacher_id: int):
        """调用后端接口删除教师"""
        try:
            url = f"{self.base_url}/teachers/{teacher_id}"
            response = self.session.delete(url, timeout=self.timeout)
            return response.status_code == 204
        except requests.exceptions.RequestException as err:
            print(f"删除教师时发生网络错误: {err}")
            return False

    def get_counselors(self):
        """获取所有辅导员列表"""
        try:
            url = f"{self.base_url}/counselors/"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def add_counselor(self, data: dict):
        """添加新辅导员"""
        try:
            url = f"{self.base_url}/counselors/"
            response = self.session.post(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def update_counselor(self, counselor_id: int, data: dict):
        """修改辅导员信息"""
        try:
            url = f"{self.base_url}/counselors/{counselor_id}"
            response = self.session.put(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def delete_counselor(self, counselor_id: int):
        """删除辅导员"""
        try:
            url = f"{self.base_url}/counselors/{counselor_id}"
            response = self.session.delete(url, timeout=self.timeout)
            return response.status_code == 204
        except requests.exceptions.RequestException as err:
            return False

    def get_dorm_managers(self):
        """获取所有宿管列表"""
        try:
            url = f"{self.base_url}/dorm_managers/"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def add_dorm_manager(self, data: dict):
        """添加新宿管"""
        try:
            url = f"{self.base_url}/dorm_managers/"
            response = self.session.post(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def update_dorm_manager(self, manager_id: int, data: dict):
        """修改宿管信息"""
        try:
            url = f"{self.base_url}/dorm_managers/{manager_id}"
            response = self.session.put(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def delete_dorm_manager(self, manager_id: int):
        """删除宿管"""
        try:
            url = f"{self.base_url}/dorm_managers/{manager_id}"
            response = self.session.delete(url, timeout=self.timeout)
            return response.status_code == 204
        except requests.exceptions.RequestException as err:
            return False

    def get_buildings(self):
        """获取所有宿舍楼列表"""
        try:
            url = f"{self.base_url}/buildings/"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def add_building(self, data: dict):
        """添加新宿舍楼"""
        try:
            url = f"{self.base_url}/buildings/"
            response = self.session.post(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def update_building(self, building_id: int, data: dict):
        """修改宿舍楼信息"""
        try:
            url = f"{self.base_url}/buildings/{building_id}"
            response = self.session.put(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def delete_building(self, building_id: int):
        """删除宿舍楼"""
        try:
            url = f"{self.base_url}/buildings/{building_id}"
            response = self.session.delete(url, timeout=self.timeout)
            return response.status_code == 204
        except requests.exceptions.RequestException as err:
            return False
    def get_rooms(self, building_name: str = None):
        """获取宿舍房间列表，可以按楼栋名筛选"""
        try:
            url = f"{self.base_url}/rooms/"
            params = {}
            if building_name:
                params['building'] = building_name
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    # ... 未来添加 add_room, update_room, delete_room ...

    def get_unallocated_students(self):
        """获取所有未分配宿舍的学生列表"""
        try:
            url = f"{self.base_url}/students/"
            # 【核心】使用 params 参数来筛选 allocated=false 的学生
            response = self.session.get(url, params={'allocated': 'false'}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def allocate_dorm(self, student_id: int, room_id: int):
        """执行宿舍分配"""
        try:
            url = f"{self.base_url}/allocations/"
            payload = {"student_id": student_id, "room_id": room_id}
            response = self.session.post(url, json=payload, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def get_all_students(self):
        """获取所有学生列表（不过滤）"""
        try:
            url = f"{self.base_url}/students/"
            # 不传递任何参数，后端默认返回所有学生
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def get_students_by_building(self, building_name: str):
        """根据楼栋名称获取学生列表"""
        try:
            url = f"{self.base_url}/students/"
            params = {'building': building_name}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def get_students_by_department(self, department_name: str):
        """根据院系名称获取学生列表"""
        try:
            url = f"{self.base_url}/students/"
            params = {'department': department_name}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def add_room(self, data: dict):
        """添加新宿舍房间"""
        try:
            url = f"{self.base_url}/rooms/"
            response = self.session.post(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def update_room(self, room_id: int, data: dict):
        """修改宿舍房间信息"""
        try:
            url = f"{self.base_url}/rooms/{room_id}"
            response = self.session.put(url, json=data, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

    def delete_room(self, room_id: int):
        """删除宿舍房间"""
        try:
            url = f"{self.base_url}/rooms/{room_id}"
            response = self.session.delete(url, timeout=self.timeout)
            return response.status_code == 204
        except requests.exceptions.RequestException as err:
            return False

    def get_my_roommates(self):
        """获取当前登录学生的室友列表"""
        if not self.current_user or self.current_user.get('role') != 'student':
            return {"error": "当前用户不是学生或未登录"}
        try:
            url = f"{self.base_url}/roommates/"
            headers = {'X-Username': self.current_user['username']}
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            return {"error": str(err)}

