from __future__ import annotations

import json
import os
import random
import string
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from .constant import DEFAULT_CODEC, DEFAULT_UA
from .decode_kit import decode_dict

try:
    # from: fabiocaccamo/python-fsutil
    import requests

    requests_installed = True
except ImportError:
    requests_installed = False


def _require_requests_installed() -> None:
    if not requests_installed:
        raise ModuleNotFoundError(
            "'requests' module is not installed, "
            "it can be installed by running: 'pip install requests'"
        )


def random_string(length: int = 16, digits: bool = True) -> str:
    """生成隨機字串

    Arguments:
        length: 字串的長度，預設為16
        digits: 是否包含數字，預設為True

    Returns:
        隨機字串
    """
    pop = string.ascii_letters + string.digits if digits else string.ascii_letters
    return ''.join(random.choices(pop, k=length))


def print_json(dictionary: dict[Any, Any], indent: int = 4) -> None:
    """以格式化的 JSON 字串印出解碼後的字典

    Arguments:
        dictionary: 輸入的字典，將會被解碼並印出
        indent: 格式化 JSON 時的縮排空格數（預設為4）

    Returns:
        None
    """
    print(json.dumps(decode_dict(dictionary), indent=indent))  # noqa: T201


def read_file_from_url(url: str, **kwargs: Any) -> str:
    """從 URL 取得內容並以字串形式回傳

    Arguments:
        url: 要取得內容的 URL
        kwargs: 傳遞給 requests.get() 的額外關鍵字參數

    Returns:
        str: 從 URL 取得的內容，作為字串回傳
    """
    _require_requests_installed()
    if headers := kwargs.get('headers'):
        kwargs.pop('headers')
    else:
        headers = {'user-agent': DEFAULT_UA}
    response = requests.get(url, headers=headers, **kwargs)  # nosec
    response.raise_for_status()
    return response.text


def read_file_lines(source: str, encoding: str = DEFAULT_CODEC) -> list[str]:
    """從檔案或 URL 讀取每一行並回傳為字串的列表

    Arguments:
        source: 要讀取的檔案路徑或 URL
        encoding: 用來讀取檔案的字元編碼（預設為 DEFAULT_CODEC）

    Returns:
        list[str]: 來自檔案或 URL 的每一行字串，已移除尾端換行符號

    若來源為 URL，則會使用 HTTP 請求取得內容
    若來源為檔案路徑，則會直接讀取檔案
    若來源既不是有效的檔案路徑，也不是 URL，則會回傳空列表
    """
    try:
        if source.startswith(('http://', 'https://')):
            text = read_file_from_url(source)
            return [line.rstrip('\n') for line in text.splitlines()]
        else:
            if os.path.isfile(source):
                with open(source, encoding=encoding) as file:
                    return [line.rstrip('\n') for line in file]
            else:
                return []
    except (UnicodeDecodeError, ValueError, OSError) as e:
        raise Exception(f'Error when reading file: {e}')


def write_file_lines(file_path: str, content: list[str]) -> None:
    """將字串列表寫入檔案，每個字串佔一行

    Arguments:
        file_path: 檔案的路徑，內容將被寫入此檔案
        content: 要寫入檔案的字串列表

    Returns:
        None
    """
    with open(file_path, 'w', encoding=DEFAULT_CODEC) as f:
        f.write('\n'.join(content))
        f.write('\n')


def add_page_num(url: str, page: int, page_tag: str = 'page') -> str:
    """在 URL 中加入或更新頁碼

    Arguments:
        url: 原始 URL
        page: 要加入或更新的頁碼
        page_tag: 頁面查詢參數的名稱

    Returns:
        str: 更新後的 URL，包含指定的頁碼
    """
    parsed_url = urlparse(url)  # 解析 URL
    query_params = parse_qs(parsed_url.query)  # 解析查詢參數
    query_params[page_tag] = [str(page)]  # 修改頁碼

    new_query = urlencode(query_params, doseq=True)  # 組合成字串
    new_url = parsed_url._replace(query=new_query)  # 替換頁碼

    # Example
    # url = "https://example.com/search?q=test&sort=asc", page = 3
    # parsed_url: ParseResult(scheme='https', netloc='example.com', path='/search', params='', query='q=test&sort=asc', fragment='')
    # query_params: {'q': ['test'], 'sort': ['asc'], 'page': ['3']}
    # new_query: 'q=test&sort=asc&page=3'
    # new_url: ParseResult(scheme='https', netloc='example.com', path='/search', params='', query='q=test&sort=asc&page=3', fragment='')
    # urlunparse: 'https://example.com/search?q=test&sort=asc&page=3'
    return urlunparse(new_url)


def remove_page_num(url: str, page_tag: str = 'page') -> str:
    """從 URL 中移除頁碼參數"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if page_tag in query_params:
        query_params.pop(page_tag)

    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))


def remove_query_params(url: str) -> str:
    """移除指定 URL 的查詢參數"""
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(query=''))


def update_query_param(url: str, param: str, value: str) -> str:
    """更新 URL 中特定查詢參數的值

    Examples:
        Update the 'hl' query parameter:

        ```python
        updated_url = update_query_param('https://example.com?hl=en', 'hl', 'fr')
        print(updated_url)
        # Output: https://example.com?hl=fr
        ```

        Update the 'user' query parameter:

        ```python
        updated_url = update_query_param('https://example.com?user=123', 'user', '456')
        print(updated_url)
        # Output: https://example.com?user=456
        ```
    """
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query[param] = [value]
    updated_query = urlencode(query, doseq=True)
    return urlunparse(parsed_url._replace(query=updated_query))
