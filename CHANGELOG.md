# Change Log
All major changes to `argdoc` will be documented here. This document
is written in [Markdown](https://help.github.com/articles/markdown-basics/).
Version numbers follow the conventions described in
[PEP440](https://www.python.org/dev/peps/pep-0440/) and
[Semantic versioning](http://semver.org/).


## Unreleased

### Added
- Quickstart, advanced usage, FAQ, glossary documentation, et c
- Export RST of processed docstrings
- argdoc-process-docstring event

### Fixed
- Can now handle option+argument+description lines that have
  multiple arguments.


## [0.0.2] - 2015-06-09

### Added
- Now handles formatting of argparsers that have subcommands
- added sphinx config variable `argdoc_main_func`
- made `setup.py`
- added this changelog

### Changed
- Lowered visual hierarchy of section headers for subcommands
  in processed rst output


# [0.0.1]

### Changed
- Converted method from conf.py to a proper Sphinx extension
