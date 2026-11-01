# CQuests 1.2.1

Fixes the Paper 1.21.4 GitHub Actions smoke test. The plugin compiled and started in the failed run, but the test bot timed out waiting for `Welcome to Dawn SMP` while the minimal test configuration produced `Welcome to our server`.

The isolated CI fixture now explicitly uses `CQuests CI` as its server name and passes that value to the bot. Welcome and single-use reward checks use the configured name. Mineflayer is pinned to the locally validated 4.39.0 version for repeatable client tests.

The smoke test also waits for asynchronous NPC placement before issuing reload or shutdown. Previously a slower fresh Folia world could have its placement job cancelled by the test itself, then fail the placement check.

The Nether test uses a solid base beneath its lava test block. This prevents residual flowing lava below the platform from contaminating the later safe-placement assertion. Production lava and void safety rules are unchanged.

This release changes the CI scripts and plugin version metadata. Gameplay classes and saved-data formats are unchanged from 1.2.0. Existing progress, NPCs, farming areas, purchases and configuration are retained.

Stop the server, replace the previous CQuests JAR with `CQuests-1.2.1.jar`, keep `plugins/CQuests/`, and start normally. Do not leave both plugin versions installed. Farm setup and integration requirements remain in `INSTALL-1.2.md`.
