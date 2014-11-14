# -*- coding: utf-8 -*-


class BaseAnalyzer(object):
    """Base class for all domains analyzers"""

    def __init__(self, documenter):
        self.documenter = documenter

    def process(self, fileconent):
        raise NotImplementedError()
