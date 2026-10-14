# RIA training and driving

These baseline command-line changes were authored on October 5, 2026 and recovered from `ria-training-safety.patch`, against repository commit `d464531be4ef482af6590d86973cac4ab3ce7ac9`. The implementation and offline tests are preserved from that patch. This documentation was refreshed when publishing the work.

## Preview a bounded continuation

From the repository root:

```sh
python3 software/train.py --resume ria/jump --save ria/new-experiment \
  --lr 0.0001 --steps 24576 --n-steps 128 --n-epochs 3
```

This only prints a plan. It does not import BotBlocks or start training. Source and destination must differ, the learning rate must be finite and positive, and the transition budget is explicit. PPO rounds the requested budget up to full `n * n_steps` rollouts. The example requests 24,576 transitions and reports 27,648 with the default 36 environments.

To execute a reviewed plan in a compatible authenticated BotBlocks Python runtime, add `--launch --confirmed-idle --confirmed-new-save`. The last two flags acknowledge that the operator checked for conflicting training and checked that the destination is unused. They are not automatic server checks; periodic saves write the chosen destination. Verify algorithm, observation normalization, ordered subsystems, robot revision, and control timing before resuming a policy.

The baseline reward and command ranges are preserved. Episode reset now uses the supplied RNG and exposes the first sampled command in the initial observation. This baseline curriculum samples only -0.04 to 0.012 m/s and -0.004 to 0.004 rad/s. It does not establish the later full-range keyboard goal or hardware performance.

## Drive an explicit baseline policy

```sh
cd software
python3 drive.py --policy ria/jump
```

The baseline driver requires an explicit compatible direct-action policy. W/S and A/D retain their original ±0.125 commands; space controls jump hold/release. Do not give this driver one of the residual policies below: they require the custom observation/action adapter and physical controller.

The historical BotBlocks CLI did not forward Python script arguments. Use a supported Python entry point with the required runtime/module paths, or an explicit reviewed wrapper. Current CLI compatibility has not been rechecked.

## Later authored residual-controller version

The [October 7 residual experiments](experiments/keyboard_20261007/README.md) contain the later assistant-authored feedback controller, training script, height-gain schedule, and actual evaluation sources/results. They are separate from this baseline CLI. They are simulation experiments, not a replacement hardware firmware or a validated release.

The October 5 checkpoint comparison is preserved in `artifacts/evaluate_checkpoints.py`, `artifacts/checkpoint-metadata.json`, and `artifacts/evaluation-results.json`. Those are historical results for the baseline `jump` and `pi4` policies, not results for the October 7 residual controller. The evaluator needs separately obtained matching policy files and a compatible simulator. Checkpoint bytes are not included.

## Offline checks

```sh
python3 -m pytest software/tests -q
python3 -m compileall -q software artifacts/evaluate_checkpoints.py
```

Tests use mocks or inspect preserved evidence and never contact BotBlocks, execute archived experiments, or run physics. A pass establishes these code/evidence checks only.
