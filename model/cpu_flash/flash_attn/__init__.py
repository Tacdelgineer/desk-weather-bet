"""CPU stand-in for flash-attn (CUDA-only), so the AIFS checkpoint loads and runs on a machine without an NVIDIA GPU.

Same math as flash_attn_func with a symmetric sliding window: query i attends to keys j with |i - j| <= window.
Computed in query chunks so memory stays small. Not a speed-up; just an exact fallback.
"""
__version__ = "2.8.3"

from .flash_attn_interface import flash_attn_func  # noqa: F401
