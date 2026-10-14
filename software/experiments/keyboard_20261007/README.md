# Assistant-authored RIA keyboard experiments, October 7, 2026

This is the preserved software version built around a physical feedback controller and a learned six-channel residual. It is a reviewable historical experiment, not a promoted policy or hardware firmware. The Python implementation files here are byte-for-byte copies of the authored source; only packaging, documentation, manifest, and offline checks were added for this PR.

## Which version is which

- `train_residual_jump04_moving.py`: the executed moving-jump curriculum, resuming `ria/keyboard-residual-20261007-jump03-stationary` and saving `ria/keyboard-residual-20261007-jump04-moving`. The final policy had 1,110,016 cumulative steps. Its checkpoint at 1,064,960 steps is a different artifact.
- `evaluate_height_gain_schedule.py`: the executed runtime sweep with unchanged jump04 weights. The best tested setting is Kp exponent 1 and Kd exponent 2. The height ratio is clipped to 0.4–1 relative to 0.154 m.
- `validate_compiler_pose_keyboard.py`: the executed broader validator and complete best-tested controller/observation/action runtime. It uses the height schedule, correctly compiled initial poses, 24 randomized jumps, and a separate four-case recovery comparison for the original policy.
- `unrun/transfer_state49_runtime.py`: an authored next-step proposal adding four observation features and transfer initialization. It was not run, and no state49 policy or performance result is established. It is not the best-tested version.

The training and final validation scripts match the scripts embedded in their original saved process reports. `manifest.json` records source/result hashes. No physical controller implementation was invented or tuned while packaging this PR.

## Historical evidence

With the unchanged jump04 policy plus height-scheduled feedback:

- Fixed grid: 12/12 strict geometric-proxy successes, zero falls, mean qualified peak 0.0229028 m
- Randomized set: 23/24 strict successes, one falling case (3.67 s fallen), mean qualified peak 0.0218839 m
- The separate feedback-only driving prototype had zero falls over 19 cases / 140 simulated seconds. On its 14 standard cases, speed MAE at 2 s was 0.03707385 m/s and turn MAE at 1 s was 0.30731295 rad/s. This is an earlier driving experiment, not a full residual-policy validation
- The four recovery cases use the original `ria/resume-jump-20261005-2015` policy; 2/4 recovered. They do not demonstrate recovery by the residual controller

`results/ria-height-gain-results.json` contains all 48 sweep cases; select exponent pair (1, 2) for the reported fixed-grid result. The unmodified moving04 training evaluator predates the strict validator and can retain a valid label after a later fall; its 9/12 legacy count is only 8/12 after the full-case fall veto. Peaks after a fall are not safe-jump evidence. The reported best results are approximately 2 cm, not demonstrated 10 cm jumps.

## Runtime contract and reproducibility gaps

The tested interface has 45 observations and six residual actions. Physical actions are the clipped feedback baseline plus residual scales `[0.3, 0.3, 0.3, 0.3, 0.15, 0.15]`. Residual authority is gated to jump hold and 2.5 seconds after release. Controller dt is 0.01 s; physics timestep is 0.005 s. The validator uses scenario seed 90301, reset seed 90206, and two Torch threads. Previous actions mean residual actions, not direct motor actions.

Matching policy bytes and numeric observation normalization, an immutable robot snapshot, and exact BotBlocks/MuJoCo/Torch/dependency versions are not bundled or fully pinned. The scripts load mutable `ria/robot`; a later copy is not proof of the historical model. A runtime source-patch installs residual dispatch into `SimVecEnv.step_wait` and deliberately asserts if the expected implementation differs. A current library version may be incompatible. The residual policy is not interchangeable with the baseline 87-observation direct-action policy.

**These archived files execute work at module top level. Do not import them to inspect them.** Running the training script or unrun transfer proposal can train and/or write the named remote policy assets. Read and adapt a separate copy, choose fresh destinations, and establish the exact dependencies/assets first. The validation scripts execute simulations on import. This PR does not launch training, modify policy assets, or run the simulator.

Jump/landing labels are wheel-height and upright proxies, not contact-force measurements. The ground and flight proxies can overlap; a witnessed non-ground phase is still needed for a stronger landing definition. State49 review also identified missing finite-horizon terminal handling and observation flags, abrupt height-schedule termination, and insufficient recovery authority. These are unresolved design limitations, not fixes implemented in this PR.

## Verification now

The offline test suite checks source syntax/hashes, preserved result counts, the strict fall veto, and reported means without executing these scripts. Historical simulations were not rerun for publication. BotBlocks access currently needs reauthentication, and complete historical runtime/policy pins remain unavailable.
