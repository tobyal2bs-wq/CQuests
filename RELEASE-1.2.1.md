# CQuests 1.2.1

Fixes the Paper 1.21.4 GitHub Actions smoke test. The plugin compiled and started in the failed run, but the test bot timed out waiting for `Welcome to Dawn SMP` while the minimal test configuration produced `Welcome to our server`.

The isolated CI fixture now explicitly uses `CQuests CI` as its server name and passes that value to the bot. Welcome and single-use reward checks use the configured name. Mineflayer is pinned to the locally validated 4.39.0 version for repeatable client tests.

This release changes the CI scripts and plugin version metadata. Gameplay classes and saved-data formats are unchanged from 1.2.0. Existing progress, NPCs, farming areas, purchases and configuration are retained.

Stop the server, replace the previous CQuests JAR with `CQuests-1.2.1.jar`, keep `plugins/CQuests/`, and start normally. Do not leave both plugin versions installed. Farm setup and integration requirements remain in `INSTALL-1.2.md`.
