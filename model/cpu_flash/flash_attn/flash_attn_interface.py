import math
import os

import torch

CHUNK = int(os.environ.get("CPU_FLASH_CHUNK", "2048"))


def flash_attn_func(q, k, v, dropout_p=0.0, softmax_scale=None, causal=False, window_size=(-1, -1),
                    softcap=0.0, alibi_slopes=None, deterministic=False, return_attn_probs=False):
    """q, k, v: (batch, seq, heads, dim) -> (batch, seq, heads, dim)."""
    if causal or alibi_slopes is not None or return_attn_probs:
        raise NotImplementedError("cpu flash_attn stand-in: causal/alibi/return_attn_probs not supported")
    b, n, h, d = q.shape
    scale = softmax_scale if softmax_scale is not None else 1.0 / math.sqrt(d)
    left, right = window_size
    left = n if left is None or left < 0 else left
    right = n if right is None or right < 0 else right
    qt, kt, vt = (t.transpose(1, 2) for t in (q, k, v))  # (b, h, n, d)
    out = torch.empty_like(qt)
    idx = torch.arange(n, device=q.device)
    for s in range(0, n, CHUNK):
        e = min(n, s + CHUNK)
        ks, ke = max(0, s - left), min(n, e + right)
        scores = torch.matmul(qt[:, :, s:e], kt[:, :, ks:ke].transpose(-1, -2)) * scale
        if softcap:
            scores = softcap * torch.tanh(scores / softcap)
        rel = idx[ks:ke].unsqueeze(0) - idx[s:e].unsqueeze(1)  # j - i
        mask = (rel >= -left) & (rel <= right)
        scores = scores.masked_fill(~mask, float("-inf"))
        out[:, :, s:e] = torch.matmul(torch.softmax(scores, dim=-1), vt[:, :, ks:ke])
    return out.transpose(1, 2)
