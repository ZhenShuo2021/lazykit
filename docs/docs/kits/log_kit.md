# Log Kit

`LoggingUtility` 中使用預設的 `setup_logging` 為開箱即用的 logger，顯示時間並且以顏色區分 log level。`LogFormatter` 預設格式為

```shell
[HH:MM:SS][LEVEL] Message
```

`setup_logging` 以外的方法都是子方法，全部湊在一起就變成 `setup_logging`。

::: lazykit.log_kit
    options:
      separate_signature: true
      show_signature_annotations: true
      signature_crossrefs: true
