# KNOWN BUGS

Primary blocker:
- v0.27 still flickers / sometimes map becomes blank.

Likely causes:
- Canvas redraw still clears too much.
- Hover redraw still calls full draw.
- after scheduling / initial draw / redraw on hover may produce blank.
- Canvas.delete("all") should be minimized or removed during interaction.
