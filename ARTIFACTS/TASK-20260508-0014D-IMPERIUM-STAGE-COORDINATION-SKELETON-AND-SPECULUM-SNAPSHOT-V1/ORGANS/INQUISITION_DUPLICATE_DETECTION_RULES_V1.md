# INQUISITION DUPLICATE DETECTION RULES V1

Conflict triggers:
- same TASK/STAGE/RUN/CONTOUR with different sha256
- ACK exists without source signal
- stage completion without receipt
- provenance producer mismatch
- multiple contours claiming same single-owner stage output
