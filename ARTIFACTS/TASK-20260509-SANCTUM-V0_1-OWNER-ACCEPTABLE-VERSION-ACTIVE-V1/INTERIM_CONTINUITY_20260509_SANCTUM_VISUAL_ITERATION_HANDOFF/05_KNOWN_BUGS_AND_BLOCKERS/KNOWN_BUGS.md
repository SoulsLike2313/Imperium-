# KNOWN BUGS

Primary blocker:
- Sanctum v0.27 still flickers / sometimes blank map appears.

Likely technical cause (working hypothesis):
- Tkinter Canvas redraw still clears too much or redraw timing remains unstable.
- Hover redraw / after scheduling / initial draw may still produce blank state.
