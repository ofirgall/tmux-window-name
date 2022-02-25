#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple

@dataclass
class Pane:
    info: Mapping[str, Any]
    program: Optional[str]

@dataclass
class DisplayedPath:
    pane: Pane
    full: Path
    display: Path

def get_uncommon_path(a: Path, b: Path) -> Tuple[Path, Path]:
    for x in range(-1, -max(len(a.parts), len(b.parts)) - 1, -1):
        try:
            if a.parts[x] != b.parts[x]:
                break
        except IndexError:
            break

    return Path(*a.parts[x:]), Path(*b.parts[x:])

def get_exclusive_paths(panes: List[Pane]) -> List[Tuple[Pane, Path]]:
    # Start all displays as the last dir (.name)
    exc_paths = [DisplayedPath(pane, Path(pane.info['pane_current_path']), Path(Path(pane.info['pane_current_path']).name)) for pane in panes]

    # TODO: issue:
    # a/b - a/b
    # a/b - b (need to bo a/b too)
    # c/b - c/b
    for x in range(len(exc_paths)):
        for y in range(len(exc_paths)):
            if x == y:
                continue
            # If same display find new display
            if exc_paths[x].display == exc_paths[y].display and \
                    panes[x].program == panes[y].program and \
                    exc_paths[x].full != exc_paths[y].full:
                exc_paths[x].display, exc_paths[y].display = get_uncommon_path(exc_paths[x].full, exc_paths[y].full)

    return [(p.pane, p.display) for p in exc_paths]

