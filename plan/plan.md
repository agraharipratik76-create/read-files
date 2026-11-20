# Gate6 Campus Rush — Run the Existing Game

Campus Rush is a hackathon project: an open-world, GTA-style game set on a campus.
This plan gets the uploaded project running here as it is, so it can be opened and played in the browser.

## Who it's for
- The hackathon team, so they can show, test and share a working version of the game.
- Judges and players who open the preview link to try it.

## Core features and experience
- The game's existing features stay as they are: no new features, no redesign and no content changes.
- The goal is that the game loads, the world shows up, the controls respond and nothing crashes on startup.
- Changes to the code are limited to what is needed to make it run here, such as missing packages, wrong file paths, port and address settings, or a broken build step.
- If the project has a backend (scores, saves, multiplayer), it is connected to this environment's database so it keeps working.

## User flow
1. Open the preview link.
2. The game loads in the same way the team built it: menu or straight into the world.
3. Play with the project's existing controls.

## UI/UX feel
- No changes. The game keeps its original look, sound and controls.

## Implementation phases
- **Phase 1 (MVP, built now):** Unpack the project, work out how it is built, set it up here and fix anything that stops it from loading or playing. Check that it opens and plays in the browser on desktop. Afterwards, provide a short note listing every fix made and anything that still does not work.
- **Phase 2 (later, only if requested):** Fix gameplay bugs, improve performance and support mobile or touch controls.
- **Phase 3 (later, only if requested):** Add new features, such as new areas, missions, leaderboards or multiplayer improvements.

## Assumptions
- The zip contains the full source code for the game, not just a compiled build. If it only has a compiled build, that build is served as it is.
- Files the game needs, such as models, textures and sounds, are inside the zip. Anything missing is reported, not replaced.
- Desktop browser with keyboard and mouse is the target. Mobile support is not part of phase 1.
- Any outside services the game uses (for example an AI or online service that needs a key) are reported if they need credentials. The rest of the game is still made to run without them.
- Only the fixes needed to make the game run are made. The team's code, structure and design are otherwise left as they are.
