from __future__ import annotations

import os
import platform
import shutil
from mimetypes import guess_extension
from pathlib import Path
from typing import TYPE_CHECKING, TypeAlias

from pathvalidate import sanitize_filename

if TYPE_CHECKING:
    from requests import Response

strPath: TypeAlias = str | Path


def mkdir(folder_path: strPath) -> None:
    """建立目錄，若已存在則跳過

    Args:
        folder_path: 目錄路徑

    Returns:
        None
    """
    if os.path.isfile(folder_path):
        raise OSError(f'{folder_path} already exists')
    Path(folder_path).mkdir(parents=True, exist_ok=True)


def mv_dir(source: strPath, destination: strPath, delimiter: str = '_') -> Path:
    """安全移動目錄，若同名則自動重命名

    Args:
        source: 來源目錄路徑
        destination: 目標目錄路徑
        delimiter: 當名稱衝突時的分隔符，預設為 '_'

    Returns:
        Path: 移動後的目標目錄路徑
    """
    try:
        src_path = Path(source).resolve()
        dst_path = Path(destination).resolve()

        if not src_path.exists():
            raise FileNotFoundError(f'Source directory does not exist: {src_path}')
        if not src_path.is_dir():
            raise NotADirectoryError(f'Source path is not a directory: {src_path}')
        if src_path == dst_path:
            return dst_path

        if str(dst_path).startswith(str(src_path)):
            raise ValueError('Cannot move a directory into its own subdirectory')

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if dst_path.exists():
            dst_path = Path(gen_unique_path(dst_path, delimiter))
        shutil.move(str(src_path), str(dst_path))
        return dst_path

    except PermissionError as e:
        raise PermissionError(f'Permission denied: {e}')
    except OSError as e:
        raise OSError(f'Failed to move directory: {e}')
    except Exception as e:
        raise RuntimeError(f'Unexpected error during directory move: {e}')


def mv_file(source: strPath, destination: strPath, delimiter: str = '_') -> Path:
    """安全移動檔案，若同名則自動重命名

    Args:
        source: 來源檔案路徑
        destination: 目標檔案路徑
        delimiter: 當名稱衝突時的分隔符，預設為 '_'

    Returns:
        Path: 移動後的目標檔案路徑
    """
    try:
        src_path = Path(source).resolve()
        dst_path = Path(destination).resolve()

        if not src_path.exists():
            raise FileNotFoundError(f'Source file does not exist: {src_path}')
        if not src_path.is_file():
            raise OSError(f'Source path is not a file: {src_path}')

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if dst_path.exists():
            dst_path = Path(gen_unique_path(dst_path, delimiter))
        shutil.move(str(src_path), str(dst_path))
        return dst_path

    except PermissionError as e:
        raise PermissionError(f'Permission denied: {e}')
    except OSError as e:
        raise OSError(f'Failed to move file: {e}')
    except Exception as e:
        raise RuntimeError(f'Unexpected error during file move: {e}')


def is_system_file(file_path: strPath) -> bool:
    """判斷檔案是否為系統檔案

    Args:
        file_path: 檔案路徑

    Returns:
        bool: 是否為系統檔案
    """
    ignored_files = {
        '.DS_Store',
        'Thumbs.db',
        '.Spotlight-V100',
        '.Trashes',
        'desktop.ini',
    }
    return os.path.basename(file_path) in ignored_files


def count_file(folder_path: str, exclude_system: bool = True) -> int:
    """計算目錄中檔案數量，可排除系統檔案

    Args:
        folder_path: 目錄路徑
        exclude_system: 是否排除系統檔案，預設為 True

    Returns:
        int: 目錄中檔案數量
    """
    if exclude_system:
        filter_func = lambda entry: entry.is_file() and not is_system_file(entry.path)
    else:
        filter_func = lambda entry: entry.is_file()
    return sum(1 for entry in os.scandir(folder_path) if filter_func(entry))


def resolve_abs_path(relative_path: str) -> Path:
    """解析相對路徑為絕對路徑

    解析相對路徑並擴展 `~` 為使用者主目錄

    Args:
        relative_path: 相對路徑

    Returns:
        Path: 絕對路徑

    Example:
        resolve_abs_path('~') -> /home/user
        resolve_abs_path('data/file.txt') -> /home/user/data/file.txt
        resolve_abs_path('/data/file.txt') -> /data/file.txt
        resolve_abs_path('~/data/file.txt') -> /home/user/data/file.txt
    """
    return Path(relative_path).expanduser().resolve()


def gen_unique_path(path: strPath, delimiter: str = '_') -> Path:
    """生成唯一路徑，使用二分法找可用名稱

    Args:
        path: 路徑
        delimiter: 當名稱衝突時的分隔符，預設為 '_'

    Returns:
        Path: 唯一路徑
    """
    try:
        path = Path(path)
        if not path.parent.exists():
            raise ValueError(f'Parent directory not exists: {path.parent}')

        stem, suffix = path.stem, path.suffix
        parent = path.parent

        if not path.exists():
            return path

        # 二分搜索找到第一個可用的數字
        start, end = 1, 1
        while Path(parent / f'{stem}{delimiter}{end}{suffix}').exists():
            end *= 2

        while start < end:
            mid = (start + end) // 2
            test_path = Path(parent / f'{stem}{delimiter}{mid}{suffix}')

            if test_path.exists():
                start = mid + 1
            else:
                end = mid

        return parent / f'{stem}{delimiter}{start}{suffix}'

    except OSError as e:
        raise OSError(f'File system error: {e}')
    except Exception as e:
        raise ValueError(f'Invalid path or arguments: {e}')


def get_system_config_dir() -> Path:
    """取得系統設定目錄

    Returns:
        Path: 系統設定目錄路徑
    """
    if platform.system() == 'Windows':
        base = os.getenv('APPDATA', '')
    else:
        base = os.path.expanduser('~/.config')
    return Path(base)


def get_file_dest(root: strPath, category: str, filename: str, ext: str = '') -> Path:
    """組合路徑並清理非法字元

    Args:
        root: 下載根目錄
        category: 類別資料夾名稱
        filename: 檔案名稱
        ext: 檔案副檔名，預設為空

    Returns:
        Path: 完整的檔案路徑
    """
    folder = Path(root) / category
    return sanitize_filename(folder / f'{filename}{ext}')


def get_ext(response: Response, default_ext: str = 'jpg') -> str:
    """從回應中取得檔案副檔名，若無法判斷則回傳預設值

    Args:
        response: HTTP 回應物件
        default_ext: 預設副檔名，預設為 'jpg'

    Returns:
        str: 檔案副檔名
    """
    content_type = response.headers.get('Content-Type', '').split(';')[0].strip()
    extension = guess_extension(content_type)
    return extension.lstrip('.') if extension else default_ext
