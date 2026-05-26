"""Logging helpers for Dataset Quality Auditor."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a package logger."""
    return logging.getLogger(name)
