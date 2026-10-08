import random

from config import W, H


def update(state, real_dt, actions):
    if state.game_over or state.show_help or state.confirm_exit:
        return
    dt = real_dt * state.time_scale

    if not state.time_disabled:
        state.time_of_day = (state.time_of_day + dt / 180.0) % 1.0

    state.weather_t -= dt
    if state.weather_t <= 0:
        if state.weather_disabled:
            state.weather = "clear"
            state.weather_t = 5.0
        else:
            r = random.random()
            if r < 0.55:
                state.weather = "clear"
                state.weather_t = random.uniform(20, 50)
            elif r < 0.85:
                state.weather = "rain"
                state.weather_t = random.uniform(15, 35)
            else:
                state.weather = "storm"
                state.weather_t = random.uniform(10, 25)

    if state.weather in ("rain", "storm"):
        n = 6 if state.weather == "rain" else 12
        for _ in range(n):
            state.rain.append([random.randint(0, W), random.randint(-40, 0),
                               random.uniform(500, 800)])

    for r in state.rain[:]:
        r[1] += r[2] * dt
        if r[1] > H:
            state.rain.remove(r)

    if state.weather == "storm" and random.random() < 0.004:
        state.flash = 1.0
    if state.flash > 0:
        state.flash -= real_dt * 4
