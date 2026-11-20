"""Opt-in diagnostics for dev runs; a no-op in the arena.

Enabled only when JF_LOG_DIR is set (dev/eval.sh sets it; the official sandbox
does not). Each episode appends to <JF_LOG_DIR>/bot_<JF_EPISODE>.log.
"""
import os

_DIR = os.environ.get("JF_LOG_DIR")
_fh = None


def enabled():
    return _DIR is not None


def log(msg):
    global _fh
    if _DIR is None:
        return
    try:
        if _fh is None:
            os.makedirs(_DIR, exist_ok=True)
            episode = os.environ.get("JF_EPISODE", str(os.getpid()))
            _fh = open(os.path.join(_DIR, f"bot_{episode}.log"), "a", buffering=1)
        _fh.write(msg + "\n")
    except OSError:
        pass


# ---- dev-only screen dumps (JF_LOG_DIR set): JF_SCREEN is a regex of log messages after which the screen is written
import re as _re
_SCREEN = _re.compile(os.environ["JF_SCREEN"]) if (_DIR is not None and os.environ.get("JF_SCREEN")) else None


def screen_wanted(msg):
    return _SCREEN is not None and _SCREEN.search(msg) is not None


def _lines(obs):
    return [bytes(line).decode(errors="replace").replace("\0", " ").rstrip() for line in obs["tty_chars"]]


def screen(obs):
    if obs is None:
        return
    try:
        log("SCREEN\n" + "\n".join(_lines(obs)))
    except Exception:
        pass


def last_screen(obs, step):
    """the latest screens of the episode, rewritten every few steps (what the game looked like when it ended)"""
    if _DIR is None or obs is None:
        return
    try:
        episode = os.environ.get("JF_EPISODE", str(os.getpid()))
        path = os.path.join(_DIR, f"last_{episode}.txt")
        prev = ""
        if os.path.exists(path):
            prev = open(path).read().split("=====PREV=====")[0]
        with open(path, "w") as fh:
            fh.write(f"step {step}\n" + "\n".join(_lines(obs)) + "\n=====PREV=====\n" + prev)
    except Exception:
        pass
