import random
from config import W, H


def update(state, real_dt):
    """Обновляет cam_x, cam_y, zoom_level. Возвращает словарь для рендера."""
    player = state.player

    if player.in_car and abs(player.in_car.speed) > 180:
        state.zoom_target = 1.0
    else:
        state.zoom_target = 0.0

    state.zoom_level += (state.zoom_target - state.zoom_level) * min(1.0, real_dt * 2.0)
    if state.zoom_level < 0.005: state.zoom_level = 0.0
    if state.zoom_level > 0.995: state.zoom_level = 1.0

    zs = state.zoom_surf
    B_w, B_h = zs.get_size()
    view_w = int(W + (B_w - W) * state.zoom_level)
    view_h = int(H + (B_h - H) * state.zoom_level)
    off_x = (B_w - view_w) // 2
    off_y = (B_h - view_h) // 2

    if state.inside is not None:
        state.cam_x = state.cam_y = 0
        state.rain.clear()
        state.flash = 0.0
    else:
        target = player.in_car if player.in_car else player
        world_cam_x = max(0, min(state.world_w - view_w, target.x - view_w / 2))
        world_cam_y = max(0, min(state.world_h - view_h, target.y - view_h / 2))
        state.cam_x = int(world_cam_x - off_x)
        state.cam_y = int(world_cam_y - off_y)
        if state.shake > 0:
            state.cam_x += random.randint(-7, 7)
            state.cam_y += random.randint(-7, 7)

    return {"cam_x": state.cam_x, "cam_y": state.cam_y,
            "view_w": view_w, "view_h": view_h,
            "off_x": off_x, "off_y": off_y}
