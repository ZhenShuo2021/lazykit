import time
from datetime import datetime, timedelta, timezone


def datetime_now() -> datetime:
    """返回當前的 UTC 日期時間"""
    return datetime.now(timezone.utc)


def timestamp_now(ms: bool = True) -> int:
    """返回當前的時間戳

    Arguments:
        ms (bool): 是否返回毫秒。預設為True

    Returns:
        int: 當前的時間戳，單位為毫秒或秒
    """
    return int(time.time() * 1000) if ms else int(time.time())


def timestamp_to_datetime(timestamp: int, ms: bool = True) -> datetime:
    """將時間戳轉換為 datetime 物件

    Arguments:
        timestamp (int): Unix 時間戳（以秒或毫秒為單位）
        ms (bool): 如果為 True，表示時間戳是以毫秒為單位。預設為True

    Returns:
        datetime: 轉換後的 datetime 物件
    """
    timestamp = timestamp // 1000 if ms else timestamp
    return datetime.fromtimestamp(timestamp)


def datetime_to_timestamp(dt: datetime, ms: bool = True) -> int:
    """將 datetime 轉換為時間戳

    Arguments:
        dt (datetime): 輸入的 datetime
        ms (bool): 是否返回毫秒。預設為True

    Returns:
        int: 對應的時間戳，單位為毫秒或秒
    """
    timestamp = int(dt.timestamp())
    return timestamp * 1000 if ms else timestamp


def get_datetime(
    timestamp: int,
    td: int = 8,
    ms: bool = True,
) -> datetime:
    """將時間戳轉換為本地化的 datetime

    Arguments:
        timestamp (int): 輸入的時間戳。如果為 -1，則使用當前時間戳
        td (int): 時區偏移的時間差（以小時為單位）。預設為8（UTC+8）
        ms (bool): 輸入的時間戳是否以毫秒為單位。預設為True

    Returns:
        datetime: 本地化的 datetime，帶有指定的時區偏移
    """
    if timestamp == -1:
        timestamp = timestamp_now(ms)

    timestamp = timestamp // 1000 if ms else timestamp
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.astimezone(timezone(timedelta(hours=td)))
