"""Worked example on SYNTHETIC odorants. Nothing here is chemistry or a finding."""
import numpy as np
from sw_enose import ReceptorArray, Pipeline, synthetic_params

p = synthetic_params(n_receptors=24, odorants=("A", "B", "C", "D"), seed=1)
arr = ReceptorArray(p, noise=0.03, seed=2)
pipe = Pipeline().fit_baseline(arr.stream([[0, 0, 0, 0]] * 20))

mixes = {"A": [2, 0, 0, 0], "B": [0, 2, 0, 0], "C": [0, 0, 2, 0], "A+B": [1, 1, 0, 0]}
train = {n: [arr.stream([c] * 10, [0.2] * 10) for _ in range(5)] for n, c in mixes.items()}
pipe.fit(train)

right = total = 0
for n, c in mixes.items():
    for _ in range(20):
        guess, _ = pipe.predict(arr.stream([c] * 10, [0.3] * 10))
        right += guess == n
        total += 1
print(f"{arr.label}")
print(f"synthetic test: {right}/{total} correct. This is a check of the machinery, not a result about smell.")
