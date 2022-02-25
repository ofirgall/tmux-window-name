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

    @staticmethod
    def from_pane(pane: Pane):
        path = Path(pane.info['pane_current_path'])
        return DisplayedPath(pane, path, Path(path.name))

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
    exc_paths = [DisplayedPath.from_pane(pane) for pane in panes]

    # TODO: issue:
    # a/b - a/b
    # a/b - b (need to bo a/b too)
    # c/b - c/b
    for x in range(len(exc_paths)):
        for y in range(len(exc_paths)):
            if x == y:
                continue

            # If full path equals no need to find a display path
            if exc_paths[x].full == exc_paths[y].full:
                continue

            # If different programs dont change display path
            if panes[x].program != panes[y].program:
                continue

            # If display not the same dont find new one
            if exc_paths[x].display != exc_paths[y].display:
                continue

            exc_paths[x].display, exc_paths[y].display = get_uncommon_path(exc_paths[x].full, exc_paths[y].full)

    return [(p.pane, p.display) for p in exc_paths]

