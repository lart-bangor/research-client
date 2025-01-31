"""Utilities to work with Python Eel and Bootstrap."""

import html
import logging
import traceback
from typing import Any, Callable, Optional
from urllib.parse import quote as urlquote

import eel

# Set up module loggers
pylogger = logging.getLogger(__name__ + ".py")
jslogger = logging.getLogger(__name__ + ".js")


def setloglevel(level: int):
    """Set the log level for the booteel module in both Python and JavaScript."""
    global pylogger, jslogger
    pylogger.setLevel(level)
    jslogger.setLevel(level)


_modal_callbacks: dict[str, Callable[[str, str], bool]] = {}


def modal(
    title: str,
    body: str,
    options: Optional[dict[str, str]] = None,
    primary: str = "ok",
    dismissable: bool = True,
    callback: Optional[Callable[[str, str], bool]] = None,
    icon: Optional[str] = None,
) -> str:
    """Display a client-side modal via bootstrap."""
    if options is None:
        options = {"ok": "OK"}
    modal_id = eel._booteel_modal(  # type: ignore
        title, body, options, primary, dismissable, None, icon
    )()
    if callback is not None:
        _modal_callbacks[modal_id] = callback  # type: ignore
    return modal_id  # type: ignore


def displayexception(exc: Exception):
    """Display an exception as a dismissable client-side bootstrap modal."""
    type_ = type(exc).__name__
    description = html.escape(str(exc)).replace("\n", "<br />\n")
    details = html.escape(traceback.format_exc()).replace("\n", "<br />\n")
    title = f"Error: {type_}"
    body = (
        f'<p>An error of type <span class="error-type">{type_}</span> occurred:</p>\n'
        f'<p class="error-description">{description}</p>\n'
        '<details class="error-details">\n'
        "   <summary>Details</summary>"
        f"  <code>\n{details}\n</code>\n"
        "</details>\n"
    )
    modal(title, body, icon="bug-fill text-danger")


def buildquery(params: dict[str, str]) -> str:
    """Build a URL query string based on a set of key-value pairs of parameters."""
    return "&".join(
        [f"{key}={urlquote(str(value), safe='')}" for key, value in params.items()]
    )


def setlocation(location: str):
    """Direct the user to a new address."""
    eel._booteel_setlocation(location)()  # type: ignore


@eel.expose  # type: ignore
def _booteel_logger_getlevel():  # type: ignore
    """Grant access to the module's loglevel to booteel.js."""
    return jslogger.level


@eel.expose  # type: ignore
def _booteel_log(level: int, message: str, args: list[Any]):  # type: ignore
    """Expose logging interface to booteel.js."""
    global jslogger
    if args:
        message += " " + ", ".join([repr(_) for _ in args])
    jslogger.log(level, message)


@eel.expose  # type: ignore
def _booteel_handlemodal(modal_id: str, choice: str):  # type: ignore
    if modal_id in _modal_callbacks:
        return _modal_callbacks[modal_id](modal_id, choice)
    else:
        return True
