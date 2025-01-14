# LazyKit

在每個 repo 複製一樣的東西很麻煩，但是這些東西又沒有用到值得發成獨立套件所以放在 Github，即使不當套件來用也可以當作一個 cheatsheet 來查看。

請注意基本上所有函式都沒寫測試，等哪天認真用到才會寫。

## What's Inside

- CLI Kit: argparse 的預配置 formatter
- Log Kit: 開箱即用，可以輸出顏色、紀錄執行時間、寫入日誌檔案的 logger
- Decode Kit: 支援各種常見編碼的編解碼函式
- Path Kit: 路徑模組，補充一些 [python-fsutil](https://github.com/fabiocaccamo/python-fsutil) 裡面沒有的函式，例如自動重新命名、解析絕對路徑、檢查是否為系統檔案等
- Time Kit: 一些包裝好的 datetime 函式，主要用於在 unix timestamp 和 datetime 模組間轉換
- String Kit: 關於字串處理的模組，例如修改 URL、生成隨機字串、漂亮印出 json 等
- Tool Kit: 沒有分類、雜七雜八的都在這裡，例如找到 chrome 執行路徑、retry 裝飾器、檢查套件是否安裝等等

## 安裝

```sh
pip install git+https://github.com/ZhenShuo2021/lazykit
```

## 使用

### CLI Kit

```py
import lazykit

# CLI Kit: argparse 套用 formatter
parser = argparse.ArgumentParser(
    prog='awesome-cli',
    description='My super cool cli tool',
    formatter_class=lazykit.ArgFormatter,
)
parser.add_argument('-o', '--option', dest='option', type=str, help='custom option')
parser.parse_args()
```

### Log Kit

套用漂亮 logger

```py
import lazykit

# 1. 基礎使用:
lazykit.setup_logging()

# 2. 客製化 formatter 和 handler:

my_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
my_handler = logging.StreamHandler()
my_handler.setFormatter(my_formatter)
setup_logging(handlers=[my_handler], formatter=my_formatter)

# 3. 支援抑制指定模組的 logger，例如 httpx 很吵:
be_quiet={'httpx': logging.WARNING, 'httpcore': logging.WARNING}
setup_logging(suppress_libs=be_quiet)
```

### Decode Kit

編解碼工具包

```py
import lazykit

# 使用 Codec 類別的 encode 方法，分別輸入資料、資料編碼方法、字元集（預設 utf-8）
lazykit.Codec.encode(data_to_be_processed, "unicode")
# 使用 decode 方法
lazykit.Codec.decode(data_to_be_processed, "unicode")

# 新增你自己的編碼器
def encode_ascii(data, encoding): ...
def decode_ascii(data, encoding): ...
lazykit.Codec.register("ascii", encode_ascii, decode_ascii)
lazykit.Codec.encode(ascii_data)
```

### Path Kit

路徑懶人包

```py
import lazykit

lazykit.mkdir(folder_path)
lazykit.mv_dir(src, dst, 檔案重複時自動增加數字的分位符)
lazykit.mv_file(src, dst, 分位符)
lazykit.is_system_file(file_path)
lazykit.gen_unique_path(file_path, 分位符)
```

### Time Kit

timestamp 簡易函式

```py
import lazykit

timestamp_now = lazykit.timestamp_now()
datetime_now = lazykit.timestamp_to_datetime(timestamp_now)
```
