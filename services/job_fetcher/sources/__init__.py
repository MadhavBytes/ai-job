"""Job source adapters"""
from .base import JobSourceAdapter
from .foorilla import FoorillaJobSource

__all__ = ["JobSourceAdapter", "FoorillaJobSource"]
