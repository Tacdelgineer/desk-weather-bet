import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "model" / "cpu_flash"))


def test_cpu_flash_matches_dense_masked_attention():
    from flash_attn import flash_attn_func
    torch.manual_seed(0)
    n, w = 3000, 300
    q, k, v = (torch.randn(1, n, 4, 16) for _ in range(3))
    out = flash_attn_func(q, k, v, window_size=(w, w))
    i = torch.arange(n)
    m = (i[None] - i[:, None]).abs() <= w
    ref = torch.nn.functional.scaled_dot_product_attention(*(t.transpose(1, 2) for t in (q, k, v)), attn_mask=m)
    assert (out - ref.transpose(1, 2)).abs().max().item() < 1e-4


@pytest.mark.skipif(not torch.cuda.is_available(), reason="no GPU")
def test_stand_in_on_gpu_matches_dense_masked_attention():
    from flash_attn import flash_attn_func
    torch.manual_seed(0)
    n, w = 3000, 300
    q, k, v = (torch.randn(1, n, 4, 16, device="cuda") for _ in range(3))
    out = flash_attn_func(q, k, v, window_size=(w, w))
    i = torch.arange(n, device="cuda")
    m = (i[None] - i[:, None]).abs() <= w
    ref = torch.nn.functional.scaled_dot_product_attention(*(t.transpose(1, 2) for t in (q, k, v)), attn_mask=m)
    assert (out - ref.transpose(1, 2)).abs().max().item() < 1e-4
