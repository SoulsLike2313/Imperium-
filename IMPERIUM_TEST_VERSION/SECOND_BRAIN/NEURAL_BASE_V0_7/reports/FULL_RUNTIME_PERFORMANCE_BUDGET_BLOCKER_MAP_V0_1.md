# FULL RUNTIME PERFORMANCE BUDGET BLOCKER MAP V0.1

- average_fps_status: `BLOCKED` value=`33.085` target=`55.0` blocker=`50.0`
- fps_1pct_low_status: `BLOCKED` value=`11.976` target=`45.0` blocker=`35.0`
- long_task_status: `PASS`
- dom_nodes_status: `PASS`
- svg_elements_status: `PASS`
- asset_request_status: `REQUIRED_ASSETS_LOADED`
- api_status: `API_CHECKS_PASS`
- console_status: `PASS`
- verdict: `PERFORMANCE_BLOCKERS_CONFIRMED_AFTER_VALID_ROUTE_FIX`

## Possible Blocker Categories
- A_heavy_visual_effects: UNKNOWN | No effect-level profiler evidence in current receipt.
- B_excessive_dom_svg: NOT_SUPPORTED_BY_CURRENT_DATA | DOM and SVG metrics are PASS versus budget.
- C_animation_frame_pressure: LIKELY | Both average_fps and fps_1pct_low are BLOCKED with valid route/assets/API context.
- D_asset_weight: UNKNOWN | Asset request success is PASS; payload-weight breakdown not present in current receipt.
- E_js_main_thread_work: UNKNOWN | Long task count is PASS but does not exclude medium-cost JS frame work.
- F_layout_reflow_pressure: UNKNOWN | No explicit layout/reflow traces available in compact receipt.
- G_measurement_environment_limitation: POSSIBLE_SECONDARY | Environment may influence absolute FPS, but route/assets/API truth is valid and blocker remains real for this baseline.
