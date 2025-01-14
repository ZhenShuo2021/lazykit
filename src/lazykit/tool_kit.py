from __future__ import annotations

import ctypes
import importlib.util
import os
import time
from collections.abc import Callable
from functools import wraps
from subprocess import run
from typing import Any

import pkg_resources

DEFAULT_RETRY_CONFIG = {'max_retries': 3, 'delay': 1.0}


def _check_module_installed(
    module: str, version: str | None = None, raise_error: bool = True
) -> str | None:
    """
    檢查單一模組是否安裝，並選擇性地驗證其版本

    Arguments:
        module (str): 要檢查的模組名稱
        version (str | None): 可選的版本號，若提供，則檢查安裝的版本
        raise_error (bool): 若模組未安裝或版本不匹配，是否引發錯誤
                             若為 False，則返回問題的描述

    Returns:
        str | None: 若有問題，返回錯誤訊息，若沒有問題則返回 None（當 raise_error 為 False 時）

    Raises:
        ImportError: 如果模組未安裝或版本不匹配
    """
    module_spec = importlib.util.find_spec(module)

    if module_spec is None:
        message = (
            f"Module '{module}' is not installed. Please install it using 'pip install {module}'."
        )
        if raise_error:
            raise ImportError(message)
        return message

    if version:
        try:
            installed_version = pkg_resources.get_distribution(module).version
            if installed_version != version:
                message = (
                    f"Module '{module}' is installed but version {installed_version} "
                    f'does not match the required version {version}.'
                )
                if raise_error:
                    raise ImportError(message)
                return message
        except pkg_resources.DistributionNotFound:
            message = f"Module '{module}' is installed, but no version information was found."
            if raise_error:
                raise ImportError(message)
            return message

    return None


def check_module_installed(
    modules: str | list[str], version: str | list[str] | None = None, raise_error: bool = True
) -> list[str] | None:
    """
    檢查指定的模組是否安裝，並選擇性地驗證其版本

    Arguments:
        modules (str | list[str]): 要檢查的模組名稱，單一模組名稱或模組名稱列表
        version (str | list[str] | None): 可選的版本號，若提供，則檢查每個模組的版本是否匹配
                                          若為單一字串，則對所有模組使用相同版本，若長度不匹配則略過後續版本比較
        raise_error (bool): 若模組未安裝或版本不匹配，是否引發錯誤
                             預設為 True。若為 False，則返回報告

    Returns:
        list[str] | None: 若有問題，返回問題列表，若 `raise_error` 為 False 則返回 None

    Raises:
        ImportError: 如果任何模組未安裝或不符合版本要求
        VersionConflict: 如果模組安裝，但版本不匹配
    """
    if isinstance(modules, str):
        modules = [modules]

    if isinstance(version, str):
        version = [version] * len(modules)  # 如果版本是單一字串，對所有模組使用相同版本

    issues = []

    for idx, module in enumerate(modules):
        mod_version = version[idx] if version and idx < len(version) else None
        issue = _check_module_installed(module, mod_version, raise_error=False)
        if issue:
            issues.append(issue)

    if issues:
        if raise_error:
            raise ImportError('\n'.join(issues))
        return issues

    return None


def setup_retry(max_retries: int = 3, delay: int | float = 1):
    """允許使用者修改全局預設重試配置"""
    DEFAULT_RETRY_CONFIG['max_retries'] = max_retries
    DEFAULT_RETRY_CONFIG['delay'] = delay


def retry(
    max_retries: int | None = None,
    delay: int | float | None = None,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    max_duration: int | float | None = None,
    alert_threshold: int | None = None,
    log_func: Callable[[str], None] = print,
):
    """
    通用自動重試工具裝飾器，支援返回值緩存與全局預設配置

    參數:
    - max_retries: 最大重試次數，若未提供則使用全局預設值
    - delay: 初始延遲時間（秒），若未提供則使用全局預設值
    - backoff: 指數退避係數，默認為 2.0（每次重試延遲時間翻倍）
    - exceptions: 捕捉並重試的異常類型，默認為 (Exception,)
    - max_duration: 重試總時間上限（秒），超過時間則終止重試，默認為 None
    - alert_threshold: 重試警戒線（次數），超過後觸發警告，默認為 None
    - log_func: 日誌函數，用於記錄重試信息，默認為 print
    """

    max_retries = max_retries or DEFAULT_RETRY_CONFIG['max_retries']
    delay = delay or DEFAULT_RETRY_CONFIG['delay']

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            current_delay = delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise
                    if alert_threshold and attempt >= alert_threshold:
                        log_func(f'警告：重試已超過警戒線（{alert_threshold} 次）')
                    if max_duration and (time.time() - start_time) >= max_duration:
                        log_func('重試超過最大持續時間，終止重試')
                        raise
                    log_func(f'重試第 {attempt} 次，異常: {e}')
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator


def get_chrome_version_unix(chrome_path: str) -> str | None:
    """獲取 Chrome 的版本（Unix 系統）"""
    result = run([chrome_path, '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip().split()[-1]


def get_chrome_version_windows() -> str | None:
    """獲取 Chrome 的版本（Windows 系統）"""
    import winreg

    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:  # type: ignore
        chrome_path, _ = winreg.QueryValueEx(key, '')  # type: ignore

    if os.path.exists(chrome_path):
        chrome_path = chrome_path.replace('\\', '\\\\')
        cmd = f'wmic datafile where name="{chrome_path}" get Version /value'
        file_info = os.popen(cmd).read()  # nosec
        version = [line.split('=')[1] for line in file_info.splitlines() if 'Version=' in line]
        return version[0]


def get_chrome_version(system: str, chrome_path: str) -> str | None:
    """根據操作系統獲取 Chrome 的版本

    Arguments:
        system (str): 操作系統，Windows、Darwin 或 Linux
        chrome_path (str): Chrome 執行檔的路徑

    Returns:
        str | None: 返回 Chrome 版本，若無法獲取則返回 None
    """
    try:
        if system == 'Windows':
            return get_chrome_version_windows()
        elif system in ['Darwin', 'Linux']:
            return get_chrome_version_unix(chrome_path)
        else:
            raise ValueError(f'Unsupported platform: {system}')
    except Exception as e:
        raise Exception(f'Get chrome version error: {e}')


def cleanup(sensitive_data: list[bytes]) -> None:
    """立即清除敏感資料

    Arguments:
        sensitive_data (list[bytes]): 敏感資料的位元組列表
    """
    for data in sensitive_data:
        length = len(data)
        buffer = ctypes.create_string_buffer(length)
        ctypes.memmove(ctypes.addressof(buffer), data, length)
        ctypes.memset(ctypes.addressof(buffer), 0, length)
        del buffer


if __name__ == '__main__':
    setup_retry(max_retries=5, delay=0.5)

    @retry()
    def risky_operation():
        print('執行操作...')
        if time.time() % 2 == 1:
            return '成功'
        raise ValueError('失敗')

    try:
        result = risky_operation()
        print(f'操作成功，結果：{result}')
    except ValueError as e:
        print(f'操作最終失敗：{e}')
