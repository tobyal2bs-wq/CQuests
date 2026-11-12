# Boss rebuild notes

One place for what you asked, what was done, and what is still open. Jump with the bookmarks.

**Bookmarks:** [Your rules](#rules) · [What you asked](#asked) · [Done](#done) · [Still open](#open) · [Preview designs](#previews) · [How the models are built](#how) · [Where things are](#where)

---

<a id="rules"></a>
## Your standing rules

- Models should look like the modded-mob reference pictures: real details, **no random blocky textures**.
- Up to **500 blocks** per model.
- **Keep Gorehorn and Thunderback** as they are.
- Names must sound human, not generated.
- No memory leaks in the plugin.
- Every update is pushed to the repo.
- New designs are shown as **previews first**, not added to the plugin until you pick them.
- `mcp.js` is not used.

<a id="asked"></a>
## What you asked, newest first

| When | You said | Status |
|---|---|---|
| 12 Nov | Delete Sunny and the Headless Horseman, make better ones | ==Done== (Sizzle, Stitches) |
| 12 Nov | Eyes disappear and faces glitch when heads turn | ==Fixed== (see Done) |
| 12 Nov | Texture is bad on nearly all of them | **Partly done**, see Still open |
| 12 Nov | Design more bosses, preview only, do not add | ==Done==, 3 previews |
| 12 Nov | Keep notes in files with bookmarks | ==This file== |
| 12 Nov | Use Blockbench | **Open**, see Still open |
| 12 Nov | Remove the little ghost boss (Hoo) | ==Done== |
| 12 Nov | Floating torsos and viewer glitches | ==Fixed== |
| 12 Nov | Work on the animations | ==Done==, own walks and signature moves |
| 11 Nov | The two with hoodies: delete and make new | ==Done== (Grimsby, Mister Bones) |
| 11 Nov | Rounded style looked even worse | ==Dropped==, switched to clean box mob style |

<a id="done"></a>
## Done

### Faces and eyes
- **Cause:** eyes, pupils, mouths and buckles were plates 0.06 px off the surface. On a real graphics card that is close enough to flicker or vanish when the head turns.
- **Fix:** every painted feature is now a raised solid piece, sunk 0.2 px into the face and standing 0.3 px out. A pupil on an eye white stands a further 0.25 px out.
- The viewer camera also got better depth precision.

### Floating parts
- Every neck, waist, shoulder, elbow and knee has a joint ball. 37 detached parts went to 0.
- Granny's hat and Old Jangles' key now sit on their owners.

### Flicker
- About 235 surfaces drawn in the same plane were separated.

### Replaced bosses
- **Sizzle** (was Sunny): an angry kettle barbecue with coals in its mouth.
- **Stitches** (was the Headless Horseman): a dog sewn together from three others.
- **Grimsby** (was the Gatekeeper): a stone gargoyle.
- **Mister Bones**: a skeleton gravedigger.
- **Hoo** removed.

### Animations
- Own walk for every walker.
- Signature moves: Ugor beats his chest, Mister Bones digs, Granny casts with her staff, Bjorn calls lightning, Old Jangles winds his key, the gnome brothers cheer.

<a id="open"></a>
## Still open

- **Textures.** Small parts now use smooth blocks so the texture is not squeezed into noise. The hard limit: without a resource pack each face shows one whole vanilla block texture, so the models cannot have painted skins like the reference mods. **A resource pack would lift that limit.** Your call.
- **Blockbench.** I cannot run Blockbench here. I can export any boss as a `.bbmodel` file for you to open and edit there, and read your edits back in.
- **I could not reproduce the vanishing eyes in my own renderer.** The fix targets the most likely cause. If it still happens, tell me which boss and whether it is in the viewer or in game.

<a id="previews"></a>
## Preview designs (not in the plugin)

Picture: `new-designs.png` in this folder.

| Design | Idea | Season it would fit |
|---|---|---|
| Old Patch | Scarecrow with a sack head, straw hat, pitchfork and a crow | Halloween |
| Sir Crumb | Gingerbread knight with a candy cane sword and peppermint shield | Winter |
| Coco | Walking palm tree with coconut fists and sunglasses | Summer |

Say which to add, change or drop.

<a id="how"></a>
## How the models are built

- Source: `cbosses/tools/models/v20_mob.py` (shipped bosses) and `v21_preview.py` (previews, only loaded with `PREVIEW=1`).
- Each model runs four passes after it is built: `calm` (smooth blocks on small parts), `joints` (joint balls), `emboss` (raised face details), `unfight` (no shared planes).
- Checks run before every push: parts apart while animating, feet on the floor, shared planes, block counts.

<a id="where"></a>
## Where things are

- Viewer: https://claude.ai/artifact/Efp58Ms8xsaULaPykFvvRx
- Repo branch: `claude/project-thread-4jho1k` in tobyal2bs-wq/CQuests
- Pictures: this folder (`new-designs.png`, `signature-moves.png`)
