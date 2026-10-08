def update(state, real_dt, actions):
    if state.wanted > 0:
        state.wanted_cool -= real_dt * state.time_scale
        if state.wanted_cool <= 0:
            state.wanted = max(0, state.wanted - 0.25)
            state.wanted_cool = 3.0
    state.stars_total = max(state.stars_total, int(state.wanted))
