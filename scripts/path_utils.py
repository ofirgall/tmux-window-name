from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from libtmux.pane import Pane as TmuxPane


@dataclass
class Pane:
    info: TmuxPane
    program: str | None  # None when no program is running


@dataclass
class DisplayedPath:
    pane: Pane
    full: Path
    display: Path

    @staticmethod
    def from_pane(pane: Pane):
        path = Path(str(pane.info.pane_current_path))
        return DisplayedPath(pane, path, Path(path.name))


def get_uncommon_path(a: Path, b: Path) -> tuple[Path, Path]:
    """
    Get 2 uncommon path between paths.

    Args:
        a: first path
        b: second path

    Returns:
        Tuple of uncommon paths

    Examples:
        >>> get_uncommon_path(Path('a/dir1/c'), Path('b/dir2/c'))
        ('dir1/c', 'dir2/c')
    """
    # Go from -1 to -Maximum length to check each part from the end
    # E.g: 'a/dir1/c', 'b/dir1/c' will go [:-1], [:-2] and stop
    for x in range(-1, -max(len(a.parts), len(b.parts)) - 1, -1):
        try:
            if a.parts[x] != b.parts[x]:
                break
        except IndexError:
            # If not in bounds its the last common path
            break

    return Path(*a.parts[x:]), Path(*b.parts[x:])


def get_exclusive_paths(panes: list[Pane]) -> list[tuple[Pane, Path]]:
    """
    Get exclusive path for each pane (better explaining in the README).

    Args:
        panes: list of the panes

    Returns:
        List of tuples with the original pane and display path.
    """
    # Start all displays as the last dir (.name)
    exc_paths = [DisplayedPath.from_pane(pane) for pane in panes]

    for x in range(len(exc_paths)):
        intersected_paths = []
        same_paths_different_programs = []
        for y in range(len(exc_paths)):
            if x == y:
                continue

            # If different programs dont change display path
            if panes[x].program != panes[y].program:
                continue

            # If full path equals no need to find a display path
            if exc_paths[x].full == exc_paths[y].full:
                same_paths_different_programs.append(y)
                continue

            # If display not the same dont find new one
            if exc_paths[x].display != exc_paths[y].display:
                continue

            intersected_paths.append(y)

        for y in intersected_paths:
            exc_paths[x].display, exc_paths[y].display = get_uncommon_path(exc_paths[x].full, exc_paths[y].full)

            for same_path in same_paths_different_programs:
                exc_paths[same_path].display = exc_paths[x].display

    return [(p.pane, p.display) for p in exc_paths]
