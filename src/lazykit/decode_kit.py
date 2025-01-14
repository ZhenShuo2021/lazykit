from __future__ import annotations

import base64
import json
from collections.abc import Callable
from typing import Any
from urllib.parse import quote, unquote

from .constant import DEFAULT_CODEC


def encode_to_base64(text: str, char_sets: str = DEFAULT_CODEC) -> str:
    """文字轉Base64"""
    return base64.b64encode(text.encode(char_sets)).decode(char_sets)


def decode_from_base64(base64_text: str, char_sets: str = DEFAULT_CODEC) -> str:
    """Base64解碼"""
    return base64.b64decode(base64_text.encode(char_sets)).decode(char_sets)


def encode_to_hex(text: str, char_sets: str = DEFAULT_CODEC) -> str:
    """文字轉十六進位"""
    return text.encode(char_sets).hex()


def decode_from_hex(hex_text: str, char_sets: str = DEFAULT_CODEC) -> str:
    """十六進位解碼"""
    return bytes.fromhex(hex_text).decode(char_sets)


def encode_to_percent(text: str) -> str:
    """文字轉百分比編碼"""
    return quote(text)


def decode_from_percent(text: str) -> str:
    """百分比解碼"""
    return unquote(text)


def encode_to_unicode_escape(text: str, char_sets: str = DEFAULT_CODEC) -> str:
    """文字轉Unicode"""
    return text.encode('unicode_escape').decode(char_sets)


def decode_from_unicode_escape(escape_text: str, char_sets: str = DEFAULT_CODEC) -> str:
    """Unicode解碼"""
    return escape_text.encode(char_sets).decode('unicode_escape')


def encode_dict(data: dict[str, Any], char_sets: str = DEFAULT_CODEC) -> dict[str, Any]:
    """字典值轉Unicode"""
    try:
        return json.loads(json.dumps(data).encode('unicode-escape').decode(char_sets))
    except (TypeError, UnicodeEncodeError, json.JSONDecodeError) as e:
        raise ValueError(f'JSON encode error: {e}')


def decode_dict(data: dict[str, Any], char_sets: str = DEFAULT_CODEC) -> dict[str, Any]:
    """字典值Unicode解碼"""
    try:
        return json.loads(json.dumps(data).encode(char_sets).decode('unicode-escape'))
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f'JSON decode error: {e}')


class Codec:
    """
    字符編碼/解碼系統，支持自定義編碼器與解碼器。

    Supported Encoding Methods:
        - base64
        - percent
        - hex
        - unicode
        - dict

    Class Variables:
        - ENCODERS (dict): 預設編碼器的名稱和對應函數
        - DECODERS (dict): 預設解碼器的名稱和對應函數
        - CODEC (str): 預設字符編碼格式，預設為 'utf-8'

    Class Methods:
        - encode(data, codec, char_sets=CODEC): 將資料編碼為指定格式
        - decode(data, codec, char_sets=CODEC): 將資料解碼為原始格式
        - register(name, encoder, decoder): 註冊新的編碼器與解碼器

    Usage:
        ```python
        # 使用Base64進行編碼與解碼
        text = 'Hello, World!'
        encoded = Codec.encode(text, 'base64')
        print(encoded)  # 編碼後的Base64字串
        decoded = Codec.decode(encoded, 'base64')
        print(decoded)  # 還原後的原始字串


        # 註冊自定義編碼器與解碼器
        def custom_encode(data: str) -> str:
            return data[::-1]  # 字符串反轉


        def custom_decode(data: str) -> str:
            return data[::-1]  # 字符串反轉


        Codec.register('reverse', custom_encode, custom_decode)

        # 使用自定義的反轉編碼器
        custom_encoded = Codec.encode('Hello', 'reverse')
        print(custom_encoded)  # "olleH"
        custom_decoded = Codec.decode(custom_encoded, 'reverse')
        print(custom_decoded)  # "Hello"
        ```
    """

    ENCODERS = {
        'base64': encode_to_base64,
        'percent': encode_to_percent,
        'hex': encode_to_hex,
        'unicode': encode_to_unicode_escape,
        'dict': encode_dict,
    }

    DECODERS = {
        'base64': decode_from_base64,
        'percent': decode_from_percent,
        'hex': decode_from_hex,
        'unicode': decode_from_unicode_escape,
        'dict': decode_dict,
    }

    CODEC = 'utf-8'

    @classmethod
    def encode(cls, data: str | dict, codec: str, char_sets: str = CODEC) -> str | dict:
        """資料編碼"""
        encoder = cls.ENCODERS.get(codec.lower())
        if not encoder:
            raise CodecError(f'Unsupported codec: {codec}. Available: {list(cls.ENCODERS.keys())}')

        if codec == 'dict' and not isinstance(data, dict):
            raise CodecError('Dict char_sets only supports dictionary input.')

        try:
            return (
                encoder(data, char_sets)
                if 'char_sets' in encoder.__code__.co_varnames
                else encoder(data)
            )
        except Exception as e:
            raise CodecError(f'編碼失敗: {e!s}')

    @classmethod
    def decode(cls, data: str | dict, codec: str, char_sets: str = CODEC) -> str | dict:
        """資料解碼"""
        decoder = cls.DECODERS.get(codec.lower())
        if not decoder:
            raise CodecError(f'Unsupported codec: {codec}. Available: {list(cls.DECODERS.keys())}')

        if codec == 'dict' and not isinstance(data, dict):
            raise CodecError('Dict decoding only supports dictionary input.')

        try:
            return (
                decoder(data, char_sets)
                if 'char_sets' in decoder.__code__.co_varnames
                else decoder(data)
            )
        except Exception as e:
            raise CodecError(f'Decoding failed: {e!s}')

    @classmethod
    def register(cls, name: str, encoder: Callable, decoder: Callable) -> None:
        """註冊編碼/解碼"""
        cls.ENCODERS[name.lower()] = encoder
        cls.DECODERS[name.lower()] = decoder


class CodecError(Exception):
    """編碼錯誤的例外類別"""

    pass
