from __future__ import annotations

from argparse import Action, RawTextHelpFormatter
from typing import Any


class ArgFormatter(RawTextHelpFormatter):
    """抑制 argparse metavar 輸入重複提示，加寬參數到描述文字的間隔

    Usage:
        ```python
        parser = argparse.ArgumentParser(
            prog='awesome-cli',
            description='My super cool cli tool',
            formatter_class=ArgFormatter,
        )
        parser.add_argument('-o', '--option', dest='option', type=str, help='custom option')
        parser.parse_args()
        ```

        Command line output:
        ```
        $ example.py -h
        usage: awesome-cli [-h] [-o OPTION]

        My super cool cli tool

        options:
          -h, --help           show this help message and exit
          -o, --option OPTION  custom option
        ```
    """

    def __init__(self, spacing: int = 36, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, max_help_position=spacing, **kwargs)

    def _format_action_invocation(self, action: Action) -> str:
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts: list[str] = []
            if action.nargs == 0:
                parts.extend(action.option_strings)

            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(f'{option_string}')
                parts[-1] += f' {args_string}'
            return ', '.join(parts)
