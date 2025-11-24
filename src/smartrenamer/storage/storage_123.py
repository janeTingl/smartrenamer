"""
123 网盘存储适配器

提供 123 网盘的统一访问接口
"""

import os
import json
import time
import hashlib
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Iterator

from .base import StorageAdapter, StorageFile, StorageType

logger = logging.getLogger(__name__)


class Storage123Adapter(StorageAdapter):
    """
    123 网盘适配器
    
    提供 123 网盘的统一访问接口
    
    配置项：
        - access_token: 访问令牌
        - refresh_token: 刷新令牌
        - 缓存目录: 本地缓存目录（可选）
        - 代理: 代理设置（可选）
    """
    
    # API 端点
    API_BASE = "https://www.123pan.com/api"
    
    def __init__(self, 配置: Dict[str, Any]):
        """
        初始化 123 网盘适配器
        
        Args:
            配置: 配置字典
        """
        super().__init__(配置)
        
        # 从配置中获取认证信息
        self.access_token = 配置.get("access_token", "")
        self.refresh_token = 配置.get("refresh_token", "")
        
        # 缓存配置
        self.缓存目录 = Path(配置.get("缓存目录", Path.home() / ".smartrenamer" / "cache" / "123"))
        self.缓存目录.mkdir(parents=True, exist_ok=True)
        
        # HTTP 会话
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Platform": "web",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
        
        # 代理设置
        代理 = 配置.get("代理")
        if 代理:
            self.session.proxies.update(代理)
        
        # 文件缓存
        self._文件缓存: Dict[str, StorageFile] = {}
        self._缓存过期时间 = 300  # 5 分钟
        self._上次刷新时间: Dict[str, float] = {}
    
    def 连接(self) -> bool:
        """
        连接到 123 网盘（验证 token 有效性）
        
        Returns:
            bool: 是否连接成功
        """
        if not self.access_token:
            logger.error("123 网盘 access_token 未配置")
            return False
        
        try:
            # 获取用户信息以验证 token
            response = self.session.get(f"{self.API_BASE}/user/info")
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                user_info = data["data"]
                self.已连接 = True
                logger.info(f"123 网盘连接成功，用户: {user_info.get('nickname', 'unknown')}")
                return True
            else:
                # Token 可能过期，尝试刷新
                if self._刷新令牌():
                    return self.连接()
                logger.error(f"123 网盘认证失败: {data}")
                return False
        
        except Exception as e:
            logger.error(f"连接 123 网盘失败: {e}")
            return False
    
    def 断开连接(self) -> None:
        """断开连接"""
        self.session.close()
        self.已连接 = False
        logger.info("123 网盘已断开")
    
    def 列出文件(
        self,
        路径: str,
        递归: bool = False,
        过滤器: Optional[callable] = None
    ) -> List[StorageFile]:
        """
        列出目录中的文件
        
        Args:
            路径: 目录路径（123 网盘路径或目录 ID）
            递归: 是否递归列出子目录
            过滤器: 文件过滤函数
            
        Returns:
            List[StorageFile]: 文件列表
        """
        文件列表 = []
        
        # 检查缓存
        if not 递归 and 路径 in self._文件缓存:
            上次时间 = self._上次刷新时间.get(路径, 0)
            if time.time() - 上次时间 < self._缓存过期时间:
                logger.debug(f"使用缓存的文件列表: {路径}")
                cached_files = [f for f in self._文件缓存.values() if f.父目录ID == 路径]
                if 过滤器:
                    cached_files = [f for f in cached_files if 过滤器(f)]
                return cached_files
        
        try:
            # 获取目录 ID
            目录ID = self._解析路径(路径)
            
            # 调用 API 获取文件列表
            文件列表 = self._获取目录文件(目录ID, 过滤器)
            
            # 更新缓存
            for 文件 in 文件列表:
                self._文件缓存[文件.路径] = 文件
            self._上次刷新时间[路径] = time.time()
            
            # 递归处理子目录
            if 递归:
                子目录列表 = [f for f in 文件列表 if f.是否目录]
                for 子目录 in 子目录列表:
                    子文件列表 = self.列出文件(子目录.路径, 递归=True, 过滤器=过滤器)
                    文件列表.extend(子文件列表)
        
        except Exception as e:
            logger.error(f"列出 123 网盘文件失败: {e}")
        
        return 文件列表
    
    def 列出文件迭代(
        self,
        路径: str,
        递归: bool = False,
        过滤器: Optional[callable] = None,
        批次大小: int = 100
    ) -> Iterator[List[StorageFile]]:
        """
        流式列出目录中的文件（生成器）
        
        Args:
            路径: 目录路径
            递归: 是否递归列出子目录
            过滤器: 文件过滤函数
            批次大小: 每批返回的文件数
            
        Yields:
            List[StorageFile]: 批量文件列表
        """
        # 123 API 通常一次返回所有文件，这里简化实现
        文件列表 = self.列出文件(路径, 递归, 过滤器)
        
        # 分批输出
        for i in range(0, len(文件列表), 批次大小):
            yield 文件列表[i:i + 批次大小]
    
    def 获取文件信息(self, 路径: str) -> Optional[StorageFile]:
        """
        获取文件信息
        
        Args:
            路径: 文件路径或文件 ID
            
        Returns:
            Optional[StorageFile]: 文件信息，不存在则返回 None
        """
        # 先检查缓存
        if 路径 in self._文件缓存:
            return self._文件缓存[路径]
        
        try:
            # 解析路径获取文件 ID
            文件ID = self._解析路径(路径)
            
            # 调用 API 获取文件信息
            response = self.session.get(
                f"{self.API_BASE}/file/info",
                params={"fileId": 文件ID}
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                文件数据 = data["data"]
                存储文件 = self._转换为存储文件(文件数据)
                
                # 更新缓存
                if 存储文件:
                    self._文件缓存[路径] = 存储文件
                
                return 存储文件
        
        except Exception as e:
            logger.error(f"获取 123 网盘文件信息失败: {e}")
        
        return None
    
    def 读取文件(self, 路径: str, 本地路径: Optional[Path] = None) -> Optional[Path]:
        """
        读取文件内容（下载到本地）
        
        Args:
            路径: 文件路径或文件 ID
            本地路径: 保存到本地的路径（可选）
            
        Returns:
            Optional[Path]: 本地文件路径，失败则返回 None
        """
        try:
            # 获取文件信息
            文件信息 = self.获取文件信息(路径)
            if not 文件信息:
                logger.error(f"文件不存在: {路径}")
                return None
            
            # 确定本地保存路径
            if 本地路径 is None:
                本地路径 = self.缓存目录 / 文件信息.名称
            else:
                本地路径 = Path(本地路径)
            
            # 如果文件已存在且大小匹配，直接返回
            if 本地路径.exists() and 本地路径.stat().st_size == 文件信息.大小:
                logger.info(f"使用缓存的文件: {本地路径}")
                return 本地路径
            
            # 获取下载链接
            下载URL = self._获取下载链接(文件信息.文件ID)
            if not 下载URL:
                logger.error(f"无法获取下载链接: {路径}")
                return None
            
            # 下载文件
            logger.info(f"开始下载文件: {文件信息.名称}")
            本地路径.parent.mkdir(parents=True, exist_ok=True)
            
            # 注意：下载时不使用 session 的认证头
            response = requests.get(下载URL, stream=True)
            response.raise_for_status()
            
            with open(本地路径, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"文件下载成功: {本地路径}")
            return 本地路径
        
        except Exception as e:
            logger.error(f"读取 123 网盘文件失败: {e}")
            return None
    
    def 写入文件(self, 本地路径: Path, 目标路径: str) -> bool:
        """
        写入文件（上传到 123 网盘）
        
        Args:
            本地路径: 本地文件路径
            目标路径: 目标网盘路径或目录 ID
            
        Returns:
            bool: 是否写入成功
        """
        try:
            本地路径 = Path(本地路径)
            
            if not 本地路径.exists():
                logger.error(f"本地文件不存在: {本地路径}")
                return False
            
            # 获取目标目录 ID
            目录ID = self._解析路径(目标路径)
            
            # 上传文件
            logger.info(f"开始上传文件: {本地路径.name}")
            
            # 预上传（获取上传参数）
            上传信息 = self._预上传(本地路径, 目录ID)
            if not 上传信息:
                return False
            
            # 如果需要上传（秒传失败）
            if 上传信息.get("需要上传", True):
                # 分片上传
                if not self._分片上传(本地路径, 上传信息):
                    return False
            
            logger.info(f"文件上传成功: {本地路径.name}")
            
            # 清除缓存
            self._清除缓存(目标路径)
            
            return True
        
        except Exception as e:
            logger.error(f"写入 123 网盘文件失败: {e}")
            return False
    
    def 删除文件(self, 路径: str) -> bool:
        """
        删除文件
        
        Args:
            路径: 文件路径或文件 ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 解析文件 ID
            文件ID = self._解析路径(路径)
            
            # 调用删除 API
            response = self.session.post(
                f"{self.API_BASE}/file/trash",
                json={"fileIdList": [int(文件ID)]}
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                logger.info(f"删除文件成功: {路径}")
                
                # 清除缓存
                if 路径 in self._文件缓存:
                    del self._文件缓存[路径]
                
                return True
            else:
                logger.error(f"删除文件失败: {data}")
                return False
        
        except Exception as e:
            logger.error(f"删除 123 网盘文件失败: {e}")
            return False
    
    def 重命名文件(self, 源路径: str, 目标路径: str) -> bool:
        """
        重命名文件
        
        Args:
            源路径: 源文件路径或文件 ID
            目标路径: 目标文件名（仅文件名，不含路径）
            
        Returns:
            bool: 是否重命名成功
        """
        try:
            # 解析文件 ID
            文件ID = self._解析路径(源路径)
            
            # 从目标路径提取文件名
            目标文件名 = Path(目标路径).name
            
            # 调用重命名 API
            response = self.session.post(
                f"{self.API_BASE}/file/rename",
                json={
                    "fileId": int(文件ID),
                    "fileName": 目标文件名
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                logger.info(f"重命名文件成功: {源路径} -> {目标文件名}")
                
                # 清除缓存
                if 源路径 in self._文件缓存:
                    del self._文件缓存[源路径]
                
                return True
            else:
                logger.error(f"重命名文件失败: {data}")
                return False
        
        except Exception as e:
            logger.error(f"重命名 123 网盘文件失败: {e}")
            return False
    
    def 创建目录(self, 路径: str) -> bool:
        """
        创建目录
        
        Args:
            路径: 目录路径（父目录 ID + 目录名）
            
        Returns:
            bool: 是否创建成功
        """
        try:
            # 解析父目录 ID 和目录名
            父目录ID, 目录名 = self._解析创建路径(路径)
            
            # 调用创建目录 API
            response = self.session.post(
                f"{self.API_BASE}/file/create",
                json={
                    "parentFileId": int(父目录ID),
                    "fileName": 目录名,
                    "dirPath": ""
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                logger.info(f"创建目录成功: {路径}")
                
                # 清除缓存
                self._清除缓存(父目录ID)
                
                return True
            else:
                logger.error(f"创建目录失败: {data}")
                return False
        
        except Exception as e:
            logger.error(f"创建 123 网盘目录失败: {e}")
            return False
    
    def 文件存在(self, 路径: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            路径: 文件路径或文件 ID
            
        Returns:
            bool: 文件是否存在
        """
        return self.获取文件信息(路径) is not None
    
    def 获取存储空间信息(self) -> Dict[str, Any]:
        """
        获取存储空间信息
        
        Returns:
            Dict[str, Any]: 存储空间信息
        """
        try:
            response = self.session.get(f"{self.API_BASE}/user/info")
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                user_info = data["data"]
                总空间 = int(user_info.get("spaceInfo", {}).get("totalSize", 0))
                已用空间 = int(user_info.get("spaceInfo", {}).get("useSize", 0))
                
                return {
                    "总空间": 总空间,
                    "已用空间": 已用空间,
                    "剩余空间": 总空间 - 已用空间,
                    "使用率": (已用空间 / 总空间 * 100) if 总空间 > 0 else 0
                }
        
        except Exception as e:
            logger.error(f"获取 123 网盘存储空间信息失败: {e}")
        
        return {
            "总空间": 0,
            "已用空间": 0,
            "剩余空间": 0,
            "使用率": 0
        }
    
    def 获取类型(self) -> StorageType:
        """获取存储类型"""
        return StorageType.STORAGE_123
    
    # 内部辅助方法
    
    def _刷新令牌(self) -> bool:
        """
        刷新访问令牌
        
        Returns:
            bool: 是否刷新成功
        """
        if not self.refresh_token:
            return False
        
        try:
            response = self.session.post(
                f"{self.API_BASE}/user/refresh_token",
                json={"refreshToken": self.refresh_token}
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                token_info = data["data"]
                self.access_token = token_info.get("accessToken", "")
                self.refresh_token = token_info.get("refreshToken", "")
                
                # 更新请求头
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                logger.info("123 网盘令牌刷新成功")
                return True
        
        except Exception as e:
            logger.error(f"刷新令牌失败: {e}")
        
        return False
    
    def _解析路径(self, 路径: str) -> str:
        """
        解析路径，返回文件/目录 ID
        
        Args:
            路径: 文件路径或 ID
            
        Returns:
            str: 文件/目录 ID
        """
        # 如果是纯数字，认为是 ID
        if 路径.isdigit():
            return 路径
        
        # 否则需要通过路径查找（实现可能较复杂，这里简化处理）
        return "0"  # 默认返回根目录
    
    def _解析创建路径(self, 路径: str) -> tuple:
        """
        解析创建路径，返回父目录 ID 和目录名
        
        Args:
            路径: 目录路径
            
        Returns:
            tuple: (父目录 ID, 目录名)
        """
        # 简化实现：假设路径格式为 "父ID/目录名"
        parts = 路径.rsplit("/", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return "0", 路径
    
    def _获取目录文件(self, 目录ID: str, 过滤器: Optional[callable]) -> List[StorageFile]:
        """
        获取目录下的文件列表
        
        Args:
            目录ID: 目录 ID
            过滤器: 文件过滤函数
            
        Returns:
            List[StorageFile]: 文件列表
        """
        文件列表 = []
        
        try:
            # 分页获取文件列表
            page = 1
            page_size = 100
            
            while True:
                response = self.session.get(
                    f"{self.API_BASE}/file/list",
                    params={
                        "parentFileId": 目录ID,
                        "page": page,
                        "limit": page_size,
                        "orderBy": "file_name",
                        "orderDirection": "asc"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                if data.get("code") != 0:
                    break
                
                # 处理文件数据
                files_data = data.get("data", {}).get("infoList", [])
                if not files_data:
                    break
                
                for 文件数据 in files_data:
                    存储文件 = self._转换为存储文件(文件数据)
                    if 存储文件 and (过滤器 is None or 过滤器(存储文件)):
                        文件列表.append(存储文件)
                
                # 检查是否还有更多数据
                if len(files_data) < page_size:
                    break
                
                page += 1
        
        except Exception as e:
            logger.error(f"获取目录文件列表失败: {e}")
        
        return 文件列表
    
    def _转换为存储文件(self, 文件数据: Dict[str, Any]) -> Optional[StorageFile]:
        """
        将 123 API 返回的文件数据转换为 StorageFile 对象
        
        Args:
            文件数据: 123 API 返回的文件数据
            
        Returns:
            Optional[StorageFile]: 存储文件对象
        """
        try:
            文件ID = str(文件数据.get("fileId", ""))
            文件名 = 文件数据.get("fileName", "")
            文件大小 = int(文件数据.get("size", 0))
            是否目录 = 文件数据.get("type") == 0  # type=0 表示目录
            修改时间戳 = int(文件数据.get("updateAt", 0)) / 1000  # 毫秒转秒
            父目录ID = str(文件数据.get("parentFileId", "0"))
            
            return StorageFile(
                路径=文件ID,  # 使用文件 ID 作为路径
                名称=文件名,
                大小=文件大小,
                是否目录=是否目录,
                修改时间=datetime.fromtimestamp(修改时间戳),
                文件ID=文件ID,
                父目录ID=父目录ID,
                哈希值=文件数据.get("etag", ""),
                缩略图URL=None,
                下载URL=None,  # 下载链接需要单独获取
                扩展属性={
                    "原始数据": 文件数据
                }
            )
        
        except Exception as e:
            logger.error(f"转换存储文件失败: {e}")
            return None
    
    def _获取下载链接(self, 文件ID: str) -> Optional[str]:
        """
        获取文件的下载链接
        
        Args:
            文件ID: 文件 ID
            
        Returns:
            Optional[str]: 下载链接
        """
        try:
            response = self.session.get(
                f"{self.API_BASE}/file/download_info",
                params={"fileId": 文件ID}
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                return data["data"].get("DownloadURL")
        
        except Exception as e:
            logger.error(f"获取下载链接失败: {e}")
        
        return None
    
    def _预上传(self, 本地路径: Path, 目录ID: str) -> Optional[Dict[str, Any]]:
        """
        预上传，获取上传参数
        
        Args:
            本地路径: 本地文件路径
            目录ID: 目标目录 ID
            
        Returns:
            Optional[Dict[str, Any]]: 上传信息
        """
        try:
            # 计算文件信息
            文件大小 = 本地路径.stat().st_size
            文件名 = 本地路径.name
            
            # 计算文件哈希
            with open(本地路径, "rb") as f:
                文件内容 = f.read()
                etag = hashlib.md5(文件内容).hexdigest()
            
            # 预上传请求
            response = self.session.post(
                f"{self.API_BASE}/file/upload_request",
                json={
                    "parentFileId": int(目录ID),
                    "fileName": 文件名,
                    "size": 文件大小,
                    "etag": etag
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                upload_data = data.get("data", {})
                
                # 检查是否秒传成功
                if upload_data.get("reuse", False):
                    logger.info(f"秒传成功: {文件名}")
                    return {"需要上传": False}
                
                return {
                    "需要上传": True,
                    "上传URL": upload_data.get("preuploadID"),
                    "文件大小": 文件大小,
                    "分片大小": upload_data.get("sliceSize", 5 * 1024 * 1024),
                }
        
        except Exception as e:
            logger.error(f"预上传失败: {e}")
        
        return None
    
    def _分片上传(self, 本地路径: Path, 上传信息: Dict[str, Any]) -> bool:
        """
        分片上传文件
        
        Args:
            本地路径: 本地文件路径
            上传信息: 上传信息
            
        Returns:
            bool: 是否上传成功
        """
        try:
            文件大小 = 上传信息["文件大小"]
            分片大小 = 上传信息["分片大小"]
            预上传ID = 上传信息["上传URL"]
            
            # 计算分片数
            分片数 = (文件大小 + 分片大小 - 1) // 分片大小
            
            # 逐个上传分片
            with open(本地路径, "rb") as f:
                for i in range(分片数):
                    offset = i * 分片大小
                    chunk = f.read(分片大小)
                    
                    # 上传分片
                    response = self.session.post(
                        f"{self.API_BASE}/file/upload",
                        data={
                            "preuploadID": 预上传ID,
                            "sliceNo": i + 1,
                            "sliceSize": len(chunk)
                        },
                        files={"file": chunk}
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get("code") != 0:
                        logger.error(f"上传分片失败: {data}")
                        return False
                    
                    logger.debug(f"上传分片 {i+1}/{分片数}")
            
            logger.info(f"分片上传完成")
            return True
        
        except Exception as e:
            logger.error(f"分片上传失败: {e}")
            return False
    
    def _清除缓存(self, 路径: str) -> None:
        """
        清除指定路径的缓存
        
        Args:
            路径: 文件路径或目录 ID
        """
        if 路径 in self._文件缓存:
            del self._文件缓存[路径]
        if 路径 in self._上次刷新时间:
            del self._上次刷新时间[路径]
