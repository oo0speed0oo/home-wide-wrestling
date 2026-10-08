"""One wrestler walking a square in the angled ring, showing all 4 facings."""
import sys
who = sys.argv[1] if len(sys.argv) > 1 else "mike"   # read before iso_ring resets argv
import chars3d as c3        # noqa: E402
import iso_ring as ring     # noqa: E402
path = [((30, 30), (78, 30), "down-right"), ((78, 30), (78, 78), "down-left"),
        ((78, 78), (30, 78), "up-left"), ((30, 78), (30, 30), "up-right")]
cycle = ["walkA", "stand", "walkB", "stand"]
frames, n = [], 0
for (x0, y0), (x1, y1), face in path:
    steps = 12
    for i in range(steps):
        t = i / steps
        X, Y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        feet = ring.P(X, Y)
        pose = cycle[n % 4]
        fn = lambda img, feet=feet, pose=pose, face=face: c3.render(who, pose, face, feet, ring.W, ring.H, img)
        frames.append(ring.main(n % 8, actors=[(feet, fn)]))
        n += 1
out = f"{ring.OUT}{who}_walk.gif"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=110, loop=0, disposal=1)
frames[6].crop((150, 180, 620, 520)).save(f"{ring.OUT}{who}_walk_f6.png")
frames[30].crop((150, 180, 620, 520)).save(f"{ring.OUT}{who}_walk_f30.png")
print(len(frames), out)
