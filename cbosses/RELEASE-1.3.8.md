# CBosses 1.3.8

Repair the existing vanilla block-display bosses and retire the three rejected designs.

- Remove Ironhide Behemoth (`ironhide_behemoth`), Void Walker (`void_walker`) and Grimfang (`fenrir`) from bundled rosters and existing server configuration on startup.
- Fill visible shoulder, neck, elbow, knee and ankle gaps with matching sockets that stay attached to the hinge.
- Anchor models from their actual rotated rest geometry. The same floor correction follows skin and hit zones.
- Rebuild Mallard, Puffneck and Angry Goose as proportioned birds with one pair of side eyes, attached bills, necks and wings. Keep their existing IDs and mini classification.
- Give each creature individual opening, damage reaction and death clips. Plant, bird, beast, caster and fighter performances use different motion patterns; preserve the egg hatch, zombie climb and finale shatter.
- Remove translation channels that pull attached bones away from their parent. Retain normal attack mappings, health tiers, commands and rewards.
- Allow explicitly switched-off emissive parts to go dark during death.
- Synchronize common visual models across both plugins; retain CQuests' supported ability mappings and weak-spot multipliers.

The eight new creature concepts in `docs/ideas/drafts.json` are review-only. They are not in plugin resources and cannot spawn. Approval and category selection happen in the separate offline Boss Ideas page; no idea becomes a chapter or seasonal boss automatically.

Install: stop the server, replace the older JAR, keep existing plugin data folders, then start. Custom JSON model overrides still take precedence: back them up and remove only outdated overrides for models you want to use from this release. No resource pack is required.

Validation: regression checks cover real rest-floor placement, two-eye bird geometry, unique performances, attached animation channels and exact client display transforms. GitHub's real-server matrix exercises the remaining roster. Browser previews approximate block shapes and effects; a production Minecraft client visual session and TPS benchmark were not performed.
