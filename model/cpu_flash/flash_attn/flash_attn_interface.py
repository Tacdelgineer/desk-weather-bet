import math
import os

import torch
import torch.nn.functional as F

CHUNK = int(os.environ.get("CPU_FLASH_CHUNK", "256"))


def flash_attn_func(q, k, v, dropout_p=0.0, softmax_scale=None, causal=False, window_size=(-1, -1),
                    softcap=0.0, alibi_slopes=None, deterministic=False, return_attn_probs=False):
    """q, k, v: (batch, seq, heads, dim) -> (batch, seq, heads, dim).

    Query i attends to keys j with -left <= j - i <= right (flash-attn's window semantics). Done in query chunks
    with PyTorch's fused CPU attention, so only a (chunk x (chunk + left + right)) mask is ever built.
    """
    if causal or alibi_slopes is not None or return_attn_probs or softcap:
        raise NotImplementedError("cpu flash_attn stand-in: causal/alibi/softcap/return_attn_probs not supported")
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
        rel = idx[ks:ke].unsqueeze(0) - idx[s:e].unsqueeze(1)  # j - i
        mask = (rel >= -left) & (rel <= right)
        out[:, :, s:e] = F.scaled_dot_product_attention(qt[:, :, s:e], kt[:, :, ks:ke], vt[:, :, ks:ke],
                                                        attn_mask=mask, scale=scale)
    return out.transpose(1, 2)
