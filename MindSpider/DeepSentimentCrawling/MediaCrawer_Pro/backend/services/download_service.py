#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载服务
"""
from typing import Optional
from pathlib import Path
import httpx
import aiofiles
from loguru import logger

from core.config import settings


class DownloadService:
    """下载服务"""
    
    def __init__(self):
        self.download_dir = settings.DOWNLOAD_DIR
        self.max_size = settings.MAX_DOWNLOAD_SIZE
        self.chunk_size = settings.DOWNLOAD_CHUNK_SIZE
    
    async def download(
        self,
        url: str,
        save_path: Optional[str] = None,
        filename: Optional[str] = None
    ) -> dict:
        """
        下载文件
        
        Args:
            url: 下载链接
            save_path: 保存路径（可选）
            filename: 文件名（可选）
        
        Returns:
            {
                "success": true,
                "file_path": "/path/to/file",
                "file_size": 1024,
                "message": "下载成功"
            }
        """
        try:
            # 确定保存路径
            if save_path:
                save_dir = Path(save_path)
            else:
                save_dir = self.download_dir
            
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 确定文件名
            if not filename:
                filename = url.split("/")[-1].split("?")[0]
                if not filename:
                    filename = "download_file"
            
            file_path = save_dir / filename
            
            # 下载文件
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    
                    # 检查文件大小
                    content_length = response.headers.get("content-length")
                    if content_length and int(content_length) > self.max_size:
                        return {
                            "success": False,
                            "message": f"文件过大: {int(content_length) / 1024 / 1024:.2f} MB"
                        }
                    
                    # 分块下载
                    total_size = 0
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=self.chunk_size):
                            await f.write(chunk)
                            total_size += len(chunk)
                            
                            # 检查大小限制
                            if total_size > self.max_size:
                                await f.close()
                                file_path.unlink()  # 删除文件
                                return {
                                    "success": False,
                                    "message": "下载超出大小限制"
                                }
            
            logger.success(f"✅ 下载成功: {filename} ({total_size / 1024 / 1024:.2f} MB)")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "file_size": total_size,
                "message": "下载成功"
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 下载失败: HTTP {e.response.status_code}")
            return {
                "success": False,
                "message": f"下载失败: HTTP {e.response.status_code}"
            }
        except Exception as e:
            logger.exception(f"❌ 下载失败: {url}")
            return {
                "success": False,
                "message": f"下载失败: {str(e)}"
            }
    
    async def batch_download(self, urls: list, save_path: Optional[str] = None) -> dict:
        """
        批量下载
        
        Args:
            urls: URL 列表
            save_path: 保存路径
        
        Returns:
            {
                "total": 10,
                "success": 8,
                "failed": 2,
                "results": [...]
            }
        """
        results = []
        success_count = 0
        failed_count = 0
        
        for url in urls:
            result = await self.download(url, save_path)
            results.append(result)
            
            if result["success"]:
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"✅ 批量下载完成: 成功 {success_count}/{len(urls)}, 失败 {failed_count}")
        
        return {
            "total": len(urls),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }




