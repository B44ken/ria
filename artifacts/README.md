# Baseline checkpoint evidence, October 5, 2026

These three files were preserved from the assistant-authored `ria-training-safety.patch`:

- `evaluate_checkpoints.py`: the historical two-seed baseline evaluator
- `checkpoint-metadata.json`: the examined `ria/jump` and `ria/pi4` checkpoint metadata/hashes
- `evaluation-results.json`: the resulting four simulation episodes

These are not the later residual-controller results. The historical evaluator found 1/2 completed episodes for `jump` and 2/2 for `pi4`. The former had 13/14 observed releases above its 5 cm geometric-clearance threshold and stable-landing window; the latter had 0/16. The `jump` policy fell in the second episode, so a counted landing is not proof of full-episode success. The evaluator uses wheel-height/contact heuristics, not contact forces.

This PR did not rerun these simulations. Matching `jump.zip`/`pi4.zip`, the authenticated service, and compatible dependencies are not bundled. Do not load untrusted pickle-based policy files. The executable source and reported results are preserved; no new success or hardware-readiness claim is made.
