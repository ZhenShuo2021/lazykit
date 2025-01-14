# CLI Kit

避免顯示 argparse metavar 的 Formatter，用於簡化參數提示和加長選項到說明的間距。舉例來說，使用 options 參數預設的提示是

```shell
options
  -o OPTION --options OPTION   Description...
```

會變成

```shell
options
  -o --options OPTION          Description...
```

::: lazykit.arg_kit
    options:
      separate_signature: true
      show_signature_annotations: true
      signature_crossrefs: true
