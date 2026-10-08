"""Write the canvas board for one wrestler's full move sheet."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites")
import chars3d as c3  # noqa: E402

who, title, color, sheet_url, reel_url, file_ = sys.argv[1:7]
names = [n for n, _ in c3.moves_for(who)]
ta = title.replace('"', '&quot;')
labels = "\n".join(
    f'<div style="height: 228px; display: flex; align-items: center; justify-content: flex-end; font-family: \'Press Start 2P\', monospace; font-size: 13px; line-height: 1.5; color: #F5F1E8; text-align: right;">{n.upper()}</div>'
    for n in names)
H = 228 * len(names)
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}, all moves</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;family=IBM+Plex+Mono:wght@400;600&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;font-family:"IBM Plex Mono",monospace;background:#141210;color:#F5F1E8}}
a{{color:#F8B800}}a:hover{{color:#FCA044}}
</style>
</helmet>
<div style="width: 2200px; height: {H + 260}px; box-sizing: border-box; padding: 40px 48px; display: flex; gap: 40px; background: #141210;">
<div style="width: 300px; flex-shrink: 0; display: flex; flex-direction: column; gap: 20px;">
<div style="font-family: 'Press Start 2P', monospace; font-size: 20px; line-height: 1.6; color: {color};">{title.upper()}: ALL MOVES</div>
<div style="font-size: 16px; line-height: 1.5; color: #C9C2B4;">Every move on the approved pose list plus his own, 2 frames each, in all 4 directions. The reel plays them in order, facing down-right.</div>
<img src="{reel_url}" alt="Animated: {ta} performing every move in turn, facing down-right" style="width: 256px; height: 304px; image-rendering: pixelated; display: block;">
</div>
<div style="display: flex; flex-direction: column; gap: 12px;">
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); width: 1536px; margin-left: 220px; font-size: 15px; color: #C9C2B4; text-align: center;">
<div>Facing down-right</div><div>Facing down-left</div><div>Facing up-right</div><div>Facing up-left</div>
</div>
<div style="display: flex; gap: 20px;">
<div style="width: 200px; display: flex; flex-direction: column;">
{labels}
</div>
<img src="{sheet_url}" alt="Sprite sheet of every {ta} move, 2 frames each, in 4 directions" style="width: 1536px; height: {H}px; image-rendering: pixelated; display: block;">
</div>
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":2200,"height":{H + 260}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
open(file_, "w").write(html)
print(H + 260)
