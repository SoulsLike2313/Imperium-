# Manual Open Instructions

## Fast preview (no server)

1. Open file:
   `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_VISUAL_FOUNDRY\LAB\index.html`
2. Verify:
   - top truth strip is visible
   - work zone is left
   - command rail is right
   - tool registry and events are centered
3. Click language switch (`EN`/`RU`) in top-right.
4. Click `RAW OFF` to open secondary technical panel and confirm it appears inside command rail only.

## Screenshot regeneration

1. `cd E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_VISUAL_FOUNDRY\PLAYWRIGHT`
2. `npm install`
3. `npx playwright install chromium`
4. `npm run screenshots`

Outputs are written into:

- `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_VISUAL_FOUNDRY\SCREENSHOTS`

