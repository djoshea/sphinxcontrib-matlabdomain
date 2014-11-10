# -*- coding: utf-8 -*-
from .base import BaseAnalyzer


class JSAnalyzer(BaseAnalyzer):
    """JavaScript anaylzer.

    Will grab documentations from comments block started '/*\"\"\"'
    and ended by '*/'

    """

    # sphinx domain for .. default-domain:: directive
    domain = 'js'

    comment_starts_with = '/*"""'
    comment_ends_with = '*/'

    def process(self, content):
        in_comment_block = False
        comment_block_indent_len = 0

        for lineno, srcline in enumerate(content.split('\n')):

            # remove indent
            line = srcline.lstrip()

            # check block begins
            if line.startswith(self.comment_starts_with):
                in_comment_block = True
                comment_block_indent_len = len(srcline) - len(line)
                continue  # goto next line

            # skip if line is not a docs
            if not in_comment_block:
                continue

            # check blocks ends
            if line.startswith(self.comment_ends_with):
                in_comment_block = False
                yield '', lineno  # empty line in docs
                continue  # goto next line

            # calculate indent
            indent_len = len(srcline) - len(line) - comment_block_indent_len
            if srcline and indent_len:
                indent_char = srcline[0]
                line = indent_char * indent_len + line

            yield line, lineno
