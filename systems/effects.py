def update(state, real_dt, actions):
    """Взрывы, флоатеры, слоумо, баннер, тряска, буфер чит-кода."""
    dt = real_dt * state.time_scale

    state.banner_t = max(0, state.banner_t - dt)
    state.shake = max(0, state.shake - real_dt * 3)
    if state.cheat_timer > 0:
        state.cheat_timer = max(0.0, state.cheat_timer - real_dt)

    if state.slowmo_t > 0:
        state.slowmo_t -= real_dt
        state.time_scale = 0.3
    else:
        state.time_scale = 1.0

    if state.j_timer > 0:
        state.j_timer -= real_dt
        if state.j_timer <= 0:
            state.j_count = 0

    for ex in state.explosions[:]:
        ex["life"] -= dt
        if ex["life"] <= 0:
            state.explosions.remove(ex)

    for f in state.floaters[:]:
        f["life"] -= dt
        f["y"] += f["vy"] * dt
        f["vy"] *= 0.94
        if f["life"] <= 0:
            state.floaters.remove(f)

    # анимация NPC
    all_npcs = list(state.peds) + list(state.cops) + list(state.gangsters)
    if state.pimp is not None:
        all_npcs.append(state.pimp)
    if state.boss is not None and state.boss.on_foot:
        all_npcs.append(state.boss)
    for n in all_npcs:
        if not hasattr(n, 'anim_t'):
            import random
            n.anim_t = random.random() * 0.15
            n.anim_frame = random.randint(0, 3)
        n.anim_t += real_dt
        if n.anim_t >= 0.15:
            n.anim_t = 0.0
            n.anim_frame = (n.anim_frame + 1) % 4

    # движение педов
    for p in state.peds:
        p.timer -= dt
        p.witness_cd = max(0, p.witness_cd - dt)
        if p.timer <= 0:
            import random
            import math
            p.angle = random.random() * math.tau
            p.timer = random.uniform(0.8, 3.0)
        import math
        state.world.try_move(p, math.cos(p.angle) * p.speed * dt,
                             math.sin(p.angle) * p.speed * dt, p.radius)
