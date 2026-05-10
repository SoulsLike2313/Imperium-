# LIGHTWEIGHT_INTER_CONTOUR_COMMUNICATION_LAW_V1

Status: candidate law.

## Core rule

Contours must exchange required artifacts through controlled lightweight communication, not Owner manual courier mode.

## Required transfer contract

Each request must include:
- exact file pattern or exact file name
- source contour and source path
- target contour and target destination path
- route id from route matrix
- manifest/hash expectation
- purpose and step id
- requester contour and timestamp

## Allowed

- targeted SSH/SCP pull/push for exact artifacts
- bounded lookup in declared artifact sinks
- explicit request artifact when direct route unavailable

## Forbidden

- broad uncontrolled directory copy
- endless filesystem search without route-based narrowing
- guessing path/identity without matrix evidence
- asking Owner to manually courier files as default behavior

## Stop rule

If direct route is unavailable, emit formal inter-contour file request and stop with request verdict.
