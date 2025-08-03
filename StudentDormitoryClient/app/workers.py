# StudentDormitoryClient/app/workers.py

from PyQt6.QtCore import QObject, pyqtSignal
from .api_client import ApiClient

class ApiWorker(QObject):
    """
    一个通用的、运行在独立QThread中的工作器。
    它现在是一个独立的、可被任何模块导入的公共组件。
    """
    finished = pyqtSignal(bool, object)
    error = pyqtSignal(str)

    def __init__(self, api_client: ApiClient, target_func_name: str, *args, **kwargs):
        super().__init__()
        self.api_client = api_client
        self.target_func_name = target_func_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            target_func = getattr(self.api_client, self.target_func_name)
            result = target_func(*self.args, **self.kwargs)

            # 统一处理返回结果，判断是否成功
            if self.target_func_name.startswith('delete_'):
                is_success = result
                data = "操作成功" if is_success else "API返回失败"
            elif isinstance(result, dict) and 'error' in result:
                is_success = False
                data = result['error']
            elif result is not None:
                is_success = True
                data = result
            else:
                is_success = False
                data = "API未返回有效数据"

            self.finished.emit(is_success, data)
        except Exception as e:
            self.error.emit(f"执行'{self.target_func_name}'时发生致命错误: {e}")