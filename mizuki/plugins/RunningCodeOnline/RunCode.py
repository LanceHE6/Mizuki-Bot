# -*- coding = utf-8 -*-
# @File:RunCode.py
# @Author:Hycer_Lance
# @Time:2023/8/17 9:18
# @Software:PyCharm

import httpx
import re


class RunCode:
    _code_type = codeType = {
        'py': ['python', 'py'],
        'cpp': ['cpp', 'cpp'],
        'java': ['java', 'java'],
        'php': ['php', 'php'],
        'js': ['javascript', 'js'],
        'c': ['c', 'c'],
        'c#': ['csharp', 'cs'],
        'go': ['go', 'go'],
        'asm': ['assembly', 'asm'],
        'ats': ['ats', 'dats'],
        'bash': ['bash', 'sh'],
        'clisp': ['clisp', 'lsp'],
        'clojure': ['clojure', 'clj'],
        'cobol': ['cobol', 'cob'],
        'coffeescript': ['coffeescript', 'coffee'],
        'crystal': ['crystal', 'cr'],
        'D': ['D', 'd'],
        'elixir': ['elixir', 'ex'],
        'elm': ['elm', 'elm'],
        'erlang': ['erlang', 'erl'],
        'fsharp': ['fsharp', 'fs'],
        'groovy': ['groovy', 'groovy'],
        'guile': ['guile', 'scm'],
        'hare': ['hare', 'ha'],
        'haskell': ['haskell', 'hs'],
        'idris': ['idris', 'idr'],
        'julia': ['julia', 'jl'],
        'kotlin': ['kotlin', 'kt'],
        'lua': ['lua', 'lua'],
        'mercury': ['mercury', 'm'],
        'nim': ['nim', 'nim'],
        'nix': ['nix', 'nix'],
        'ocaml': ['ocaml', 'ml'],
        'pascal': ['pascal', 'pp'],
        'perl': ['perl', 'pl'],
        'raku': ['raku', 'raku'],
        'ruby': ['ruby', 'rb'],
        'rust': ['rust', 'rs'],
        'sac': ['sac', 'sac'],
        'scala': ['scala', 'scala'],
        'swift': ['swift', 'swift'],
        'typescript': ['typescript', 'ts'],
        'zig': ['zig', 'zig'],
        'plaintext': ['plaintext', 'txt']
    }

    _headers = {"Authorization": "Token c15c97da-f2f2-4d3f-97bf-1fd8528eb868",
                "content-type": "application/"}

    def __init__(self, user_input: str):
        lang, code_str = RunCode.segment_parameters(user_input)
        self._language = self._code_type[lang][0]
        self._code_suffix = self._code_type[lang][1]
        self._data = {
            "files": [
                {
                    "name": f"main.{self._code_suffix}",
                    "content": code_str
                }
            ],
            "stdin": "",
            "command": ""
        }

    @staticmethod
    def segment_parameters(text: str):

        try:
            a = re.match(
                r'(py|php|java|cpp|js|c#|c|go|asm|ats|bash|clisp|clojure|cobol|coffeescript|crystal|d|elixir|elm'
                r'|erlang|fsharp|groovy|guide|hare|haskell|idris|julia|kotlin|lua|mercury|nim|nix|ocaml|pascal|perl'
                r'|raku|ruby|rust|sac|scala|swift|typescript|zig|plaintext)((?:.|\n)+)',
                text)
            lang, code = a.group(1), a.group(2)
            return lang, code
        except re.error:
            return "TypeError", \
                "语言不支持，目前仅支持py/php/java/cpp/js/c#/c/go/asm/ats/bash/clisp/clojure/cobol/coffeescript/crystal/d" \
                "/elixir/elm/erlang/fsharp/groovy/guide/hare/haskell/idris/julia/kotlin/lua/mercury/nim/nix/ocaml" \
                "/pascal/perl/raku/ruby/rust/sac/scala/swift/typescript/zig/plaintext"

    async def run(self):
        async with httpx.AsyncClient() as client:
            res = await client.post(url=f'https://glot.io/run/{self._language}?version=latest',
                                    headers=self._headers,
                                    json=self._data)
        if res.status_code == 200:
            res = res.json()
            return res['stdout'] + ('\n---\n' + res['stderr'] if res['stderr'] else '')
        else:
            return '响应异常' + res.text
