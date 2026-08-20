"""Paint-matched land. Same hash as play_ui so the mill-race hits water you see."""


def land_hash(x: int, y: int) -> int:
    return abs((x * 19 + y * 37 + (x * y * 7)) % 256)


def n01(x: int, y: int) -> float:
    return land_hash(x, y) / 255.0


def elev(x: int, y: int) -> float:
    return n01(x, y) * 0.5 + n01(x >> 1, y >> 1) * 0.32 + n01((x + 5) >> 2, (y + 3) >> 2) * 0.18


_WATER = {}


def water_grid(width: int, height: int):
    key = (int(width), int(height))
    cached = _WATER.get(key)
    if cached is not None:
        return cached
    w, h = key
    kind = [["grass"] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            e = elev(x, y)
            lake = n01(x >> 2, y >> 2)
            k = "grass"
            if e < 0.28:
                k = "water"
            elif e < 0.34:
                k = "shore"
            if lake > 0.78 and e > 0.26 and e < 0.58:
                k = "water"
            kind[y][x] = k
    ry = 6 + (land_hash(2, 9) % 10)
    for x in range(w):
        if 0 <= ry < h:
            kind[ry][x] = "water"
        if ry > 2 and kind[ry - 1][x] != "water":
            kind[ry - 1][x] = "shore"
        if ry < h - 3 and kind[ry + 1][x] != "water":
            kind[ry + 1][x] = "shore"
        step = land_hash(x, ry) % 4
        if step == 0 and ry > 3:
            ry -= 1
        elif step == 1 and ry < h - 4:
            ry += 1
    water = [[kind[y][x] == "water" for x in range(w)] for y in range(h)]
    _WATER[key] = water
    return water


def is_water(x: int, y: int, width: int, height: int) -> bool:
    if x < 0 or y < 0 or x >= width or y >= height:
        return False
    return bool(water_grid(width, height)[y][x])


def nearest_water(mx: int, my: int, world, reach: int = 4):
    w, h = int(world.width), int(world.height)
    grid = water_grid(w, h)
    best = None
    best_d = reach + 1
    y0, y1 = max(0, my - reach), min(h, my + reach + 1)
    x0, x1 = max(0, mx - reach), min(w, mx + reach + 1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = abs(x - mx) + abs(y - my)
            if d == 0 or d > reach or d >= best_d:
                continue
            if grid[y][x]:
                best_d = d
                best = (x, y)
    for stx in world.structures:
        if stx.type != "irrigation":
            continue
        d = abs(int(stx.x) - mx) + abs(int(stx.y) - my)
        if d == 0 or d > reach or d >= best_d:
            continue
        best_d = d
        best = (int(stx.x), int(stx.y))
    return best
