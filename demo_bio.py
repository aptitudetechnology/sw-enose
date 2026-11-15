"""The biomimetic stages on SYNTHETIC odorants. Shows behaviours, not findings."""
import numpy as np
from sw_enose import BiomimeticNose, SparseMemory, synthetic_params, BIOLOGY

p = synthetic_params(n_receptors=40, odorants=("A", "B", "C"), seed=11)
nose = BiomimeticNose(p, seed=12)
print(nose.label, "\n")
for k, (what, status) in BIOLOGY.items():
    print(f"- {k}: {what}\n    {status}")

print("\nAdaptation (you stop noticing a constant smell):")
nose.reset()
for t in range(0, 30):
    g = nose.adapt(nose.glomeruli([3, 0, 0]))
    if t in (0, 5, 10, 20, 29):
        print(f"  step {t:2d}: total signal {g.sum():.2f}")

print("\nSame smell, weak and strong: the normalised pattern stays similar")
lo, hi = nose.normalise(nose.glomeruli([1, 0, 0])), nose.normalise(nose.glomeruli([10, 0, 0]))
print(f"  pattern similarity (cosine) {lo @ hi / np.linalg.norm(lo) / np.linalg.norm(hi):.2f}")

mem = SparseMemory()
smells = {"A": [2, 0, 0], "B": [0, 2, 0], "C": [0, 0, 2]}
for n, c in smells.items():
    mem.learn(n, [nose.sniff(c, adapt=False) for _ in range(10)])
ok = sum(mem.recognise(nose.sniff(c, adapt=False))[0] == n for n, c in smells.items() for _ in range(20))
print(f"\nRecognition from the sparse code: {ok}/60 (synthetic odorants; a check of the code, not a result about smell)")
