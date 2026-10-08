# Home Wide Wrestling — Game Design Doc

Sep 27, 2026 · @Mike

## Concept

A small, finishable NES-style wrestling game starring your real friends as made-up wrestlers. It has a tiny roster, simple move sets, and lots of personality from presentation rather than asset count. Title: **Home Wide Wrestling**. The logo should be in the style of classic 80s wrestling logos: bold block letters, an original design rather than a copy of any real logo.

**Inspirations**

- *Pro Wrestling* (NES): the character select screen, simple controls, and characters with clear identities.
- *Tecmo World Wrestling* (NES): the commentator, the "go get 'em" hype moments, and the training gym.

**Design pillars**

1. **Finishable.** Small on purpose: 4–5 wrestlers, limited moves, reused assets.
2. **Feels like a real NES game.** Old-school look, sound, and screen flow.
3. **Your friends, recognizable.** Each sprite has one standout detail that says who it is.
4. **Personality over content.** The commentator, poses, and catchphrases do the heavy lifting.

## Roster

Four wrestlers (decided), with a hard cap of five: Mighty Mike, Big Beefy Stew, Jim "The Goat" and Nimble Niko. Their looks, styles, finishers, specials, catchphrases and stats are all in the sections below.

**Sprite rule (updated):** each wrestler is a 3D stick figure drawn as Tag Team-style pixels, and one standout detail makes each friend readable at NES size: Mike's curly mane and beard, Stew's size and yell, Jim's blond hair and goatee, Niko's height and bowl of hair.

**Character looks (draft, from photos)**

| Wrestler | Ring name (decided) | Body | Standout detail (what survives at NES size) | Classic outfit | Main color |
| --- | --- | --- | --- | --- | --- |
| Mike | **Mighty Mike** | Short, strong | Big curly black mane, short beard, tan skin, big grin | Trunks, boots, kneepads, wristbands | Red |
| Niko | **Nimble Niko** | Tallest, skinny | Shaggy straight black hair with bangs, clean-shaven | Long tights with a side stripe, light-blue wristbands (headband dropped: it read as a visor when tiny) | Navy |
| Jim | **Jim "The Goat"** | Tall, chubby | Short blond wavy hair, goatee, fair skin | **Old-school giant look (decided):** green one-strap singlet over one shoulder, tall red boots, white wrist tape | Green |
| Stew | **Big Beefy Stew** | Tall, fattest | Short dark swept-up hair, round face, clean-shaven, loud yelling face | **Big-man singlet (decided):** full blue singlet with a black band across the belly, jagged white edges and a yellow zigzag line, bare legs, black boots. **Signature pose:** yelling fist pump from his photo (one fist by his jaw, the other thrust high) instead of the double-bicep flex. | Blue and black |

Each wrestler has a different main color, so they stay easy to tell apart even when they're tiny and overlapping.

**Fighting styles and finishers (decided)**

| Wrestler | Style | Finisher | Why it fits | CPU habit (and how to beat it) |
| --- | --- | --- | --- | --- |
| Mighty Mike | Powerhouse | **Powerbomb** | The short guy lifting giants is the best visual in the game. Power 3 wins tie-ups. | Always goes for tie-ups. Stay out of reach with strikes, since his reach is short. |
| Nimble Niko | High-flyer | **DDT** | Fast and snappy, a quick strike out of nowhere. | Climbs the top rope a lot. Run in and knock him off. |
| Jim "The Goat" | Technician | **Sleeper hold** | The all-rounder who wears you down and puts you to sleep. Loves the Boston crab too. | Goes for holds on a downed opponent. Get up fast and he's left open. |
| Big Beefy Stew | Bruiser | **Running lariat** | A freight train. Heavy weight wins running collisions, so the lariat is scary. | Charges at you constantly. Block, and he's wide open after the anti-spam push-back. |
| Hidden champion | Veteran | **Figure-four leglock** | The classic champion's submission, a slow and cruel way to end a title run. | TBD with the champion. |

**Rock-paper-scissors:** Mike out-muscles Jim, Jim's holds punish Stew's slowness, Stew's charges flatten Niko, and Niko's speed and reach keep Mike away.

**Special moves (decided).** Each wrestler's 2 specials replace a default move on the same input. All are classic moves built from shared poses.

| Wrestler | Special 1 (replaces) | Special 2 (replaces) | Poses reused |
| --- | --- | --- | --- |
| Mighty Mike | Military press slam (body slam, tie-up Up + A) | Bear hug (headlock, tie-up A) | Lift held overhead; tie-up |
| Nimble Niko | Flying crossbody (drop kick, running S) | Missile dropkick (flying knee drop, top rope A) | Airborne; kick |
| Jim "The Goat" | Vertical suplex (back drop, tie-up Left/Right + S) | Hip toss (knee lift, tie-up S) | Lift; throw |
| Big Beefy Stew | Headbutt (headlock, tie-up A) | Seated butt drop (knee/elbow drop, opponent down Left/Right + S) | Tie-up; sitting up plus airborne |

**Catchphrases (decided)**

| Wrestler | Catchphrases |
| --- | --- |
| Mighty Mike | "SMALL BODY. BIG POWER!" / "I PUT THE MIGHT IN MIGHTY!" |
| Nimble Niko | "LONG ARMS. SHORT MATCH." / "FROM UP HERE, YOU LOOK TINY!" |
| Jim "The Goat" | "THE GOAT NEVER SLEEPS... YOU DO." / "BAAAH! TOO EASY." |
| Big Beefy Stew | "STEW'S READY!" / "ALL ABOARD THE BEEF TRAIN!" |

## Presentation & asset reuse

The goal is to mimic Tecmo World Wrestling as closely as possible and stay faithful to NES limits. Tighter limits make better, more authentic sprites.

**NES limits we follow**

- Limited palette, with a few colors per sprite
- Small sprites and tile-based backgrounds
- Chiptune music and sound effects
- Reuse every sprite as many times as possible

**Match screen layout (Tecmo style)**

| Area | What's there |
| --- | --- |
| Top | Names and energy bars for both wrestlers |
| Middle | The ring, both wrestlers, and the referee |
| Bottom | A black commentary bar with the announcer's face and text lines |

The black bar is cheap and adds a lot. It's drawn as background, not sprites, so it costs nothing against the sprite limit. It also shrinks the play area, and the commentary gives the match life through text instead of new animation.

**Cast in the frame:** the referee and the announcer are generic for now. Remember: update them later, possibly as friends. Generic announcer lines are written (see Words, codes and score), and Mike may swap in his own.

**One pose, three uses.** Each wrestler has a single signature pose, used for the entrance (at the top of the entrance ramp), the victory pose, and the select or versus screen.

**Per-wrestler assets (kept small):** signature pose, taunt, 2 extra moves, finisher animation, and a catchphrase as text.

**Shared across everyone:** the pose library (drawn once per body type), the entrance ramp, the ring, and UI.

**Sprite rules (decided)**

- **4 body types**, one per friend, reusable for future characters (a new character gets a new head, hair, and colors on an existing body):

| Body | Build | Friend |
| --- | --- | --- |
| 1 | Short, chubby, strong | Me |
| 2 | Tall, skinny | Niko |
| 3 | Tall, chubby | Jim |
| 4 | Tall, fat | Stew |

- **Facing** (updated): all 4 diagonal directions, drawn from the same 3D figure, so no mirroring is needed.
- **2 frames per animation**, very NES.
- **Two-wrestler poses:** avoid combined pictures. Draw each wrestler separately and position them together, so any body can do any move to any other body.

* **Separate heads (decided):** the head is its own piece on top of the body. A future character can be just a new head, hair, and colors.
* **Height order (decided):** Me (shortest), then Stew, then Jim, then Niko (tallest).

**Body type affects gameplay (decided; numbers proposed)**

Three simple stats, rated 1–3:

| Body | Speed | Power | Weight | Feel |
| --- | --- | --- | --- | --- |
| Me (short, strong) | 2 | 3 | 2 | Wins tie-ups, hits hard |
| Niko (tall, skinny) | 3 | 1 | 1 | Fast, easy to throw |
| Jim (tall, chubby) | 2 | 2 | 2 | All-rounder |
| Stew (tall, fat) | 1 | 2 | 3 | Slow, very hard to lift |

- **Speed:** walking and running speed.
- **Power:** strike damage, plus a small push bonus in tie-ups.
- **Weight:** heavy wrestlers get a receiver bonus against lifts (body slam, powerbomb, and the like), and win running collisions. Light wrestlers get thrown farther.

**Balance note (figure out later):** "Me" has the highest stat total, 7 vs. 5–6, so he needs a real weakness. Idea: **reach**. Being short means shorter arms and legs, so the tall guys can hit him from farther away, and he has to get close to do damage. Niko's reach plus speed could make him the counter to Me. Revisit with the CPU balancing talk. Principle: balanced, but every wrestler can beat every other one once you figure out how.

**Pose list (approved).** Shared poses, drawn once per body at 2 frames each:

- **Moving:** stand, walk, run
- **Striking:** punch, kick, block, taunt
- **Getting hit:** hit, stunned, knocked down, getting up
- **Grappling:** tie-up, lift, throw, being lifted, being thrown
- **Ground and air:** pin, stomp, airborne, sitting up
- **Special:** victory pose, finisher pieces

**Title screen**

1. Logo
2. Menu (updated Oct 5): 1 PLAYER (pick Easy, Medium or Hard, then your wrestler), VS MODE, PASSWORD, HOW TO PLAY
3. Credits: "TM and © 1990 Best Friend Games Ltd. Licensed by Friends of Japan Inc."

**Screens:** title, character select, versus/entrance, match, and results/victory.

## Controls

Copy Tecmo World Wrestling's control scheme, trimmed to our smaller move set. Keyboard first; gamepad support comes later.

**Input: keyboard first.** Arrow keys plus just three buttons: **A, S, D**, with Enter to pause. The goal is as few buttons as possible. If there are too many moves, cut some or make them automatic. Gamepad support comes later.

**Reference only: how Tecmo did it.** This is not our game. It's here so we can compare.

| Situation | Tecmo input | Result |
| --- | --- | --- |
| Separated | A / B | Kick / Punch |
| Walk into opponent | (automatic) | Clinch starts, then mash to win it |
| In clinch | A, B, or Up/Down/Left/Right + A or B | Different holds and slams |
| In clinch | Left/Right | Throw opponent into the ropes |
| Running | Double-tap Left/Right | Run and bounce off the ropes |
| Running | A / B | Two running attacks |
| Opponent down | B | Pin |
| Opponent down | Up/Down + B | Stomp |
| In a corner | Up | Climb to the top rope |
| On top rope | A / B | Two diving attacks |
| Being pinned | Mash A or B | Kick out |
| Opponent outside | Press toward the ropes | Climb out; press toward the ring to get back in |

**Our controls (v1, keyboard): this is the one we build.**

| Key | Job |
| --- | --- |
| Arrows | Move (double-tap to run) |
| A | Punch, and the "light" button in every situation |
| S | Kick, and the "heavy" button in every situation |
| D | Smart button: **block** when close, **taunt** when far away |
| Enter | Pause |

**D is context-sensitive (your idea).** Nobody taunts up close, so D blocks when the opponent is near and taunts when they're far.

**Full Tecmo move set, mapped to our keys.** On the NES pad, B is on the left and A is on the right. Our keyboard matches that: **A key = NES B** (punch side) and **S key = NES A** (kick side). D is our extra key.

| Situation | Input | Move |
| --- | --- | --- |
| Standing | A | Punch |
| Standing | S | Kick |
| Standing | D | Block (close) / Taunt (far) |
| Tie-up | S | Knee lift |
| Tie-up | Up + S | Brain buster |
| Tie-up | A | Headlock |
| Tie-up | Up + A | Body slam |
| Tie-up | Left/Right + S | Back drop |
| Tie-up | Down + S | Pile driver |
| Tie-up | D + any direction | Whip into that rope (all four sides) |
| Opponent bouncing off the ropes | A or S | Shoulder throw |
| Running | S | Drop kick |
| Running | A | Clothesline |
| Running | D | Stop |
| Opponent down | A | Pin |
| Opponent down | Up/Down + A | Stomp |
| Opponent down | Left/Right + S | Knee drop or elbow drop (per wrestler) |
| Opponent down | Left/Right + A | Regular submission: a shared leg-lock-style hold for everyone (Boston crab, decided), which looks different from the finishers |
| Top rope | S | Diving body attack |
| Top rope | A | Flying knee drop |
| Outside the ring | Left/Right + A | Slam into the post |
| In a corner | Up | Climb |
| At the ropes | Push outward | Go outside |
| Pinned, stunned, or down | Mash A or S | Kick out / shake off / get up |

**How tie-ups work with this:** hold a direction and mash a button. The input you use picks the move, and the tug-of-war meter decides who gets theirs in. If the energy gap is 30% or more, there's no meter, so one press does it.

**Per-wrestler moves, Tecmo style:** each wrestler has 2 special moves that *replace* a default move (for example, their Left/Right + S tie-up move is a suplex instead of a back drop). Their **finisher** replaces the move in whichever situation fits it (tie-up, running, ground, or top rope) once the opponent is under 30%.

**Reversal tiers**

| Tier | Moves | Too early means |
| --- | --- | --- |
| Light (anytime) | Knee lift, headlock, body slam, whip | — |
| Heavy (opponent under 70%) | Back drop, brain buster, pile driver, special moves | The receiver's tie-up gets much easier |
| Finisher | Finisher | Can't be too early: it only exists once the opponent is under 30% |

**Sprite cost warning:** 20+ moves means many more animations than we planned. We'll keep it manageable by sharing frames: brain buster and pile driver share a "lift" frame, body slam and back drop share a "throw" frame, and the knee drop, elbow drop, and dives share an "airborne" frame.

**Rule: share as many frames as possible.** This isn't just about saving work. Heavy frame reuse is what gives old games their look. Too many unique frames would make the game bigger and look different from what we want.

### Finishers: classic moves, cheap to draw

Old-school moves only; modern finishers are too wild for the NES feel. Each finisher happens in the situation that fits it, replacing that situation's move once the opponent is under 30%. A screen flash plus an announcer line makes it feel big without a cutscene.

| Finisher | Type | Where it happens | Frames reused | New frames |
| --- | --- | --- | --- | --- |
| Sleeper hold | Submission | Tie-up | Headlock | 0–1 |
| Running lariat | Strike | Running | Clothesline, got hit | 0 |
| Leg drop | Ground | Opponent down | Airborne, knocked down | 1 |
| Powerbomb | Power | Tie-up | Lift, knocked down | 1 |
| Big splash | Top rope | Top rope | Airborne, knocked down | 0–1 |
| DDT | Power | Tie-up | Lift, knocked down | 1–2 |
| Figure-four leglock | Submission | Opponent down | — | 2 (both wrestlers tangled) |

**Chosen finishers (5):** running lariat, sleeper hold, powerbomb, DDT, and figure-four leglock. That's one per wrestler, including the optional 5th slot. Big splash and leg drop are out. Assigned: Mike powerbomb, Stew running lariat, Jim sleeper hold, Niko DDT. The figure-four waits for the v2 champion.

**Decided:** each finisher happens in the situation that fits it, and every finisher gets a screen flash plus an announcer line. Close-up cutscenes wait for v2.

**Exclusive finishers (decided):** the sleeper hold and figure-four belong only to the wrestlers who own them as finishers. No one else can use them. Everyone gets one regular submission instead, a Boston crab (decided). The attacker stands over the downed opponent and pulls their legs back, which looks nothing like the sleeper or the figure-four. One shared pose per body.

## In the ring

Everyone shares the same basic moves and sprites, plus 2 extra moves and a finisher each. Matches are decided by the energy meter, and every struggle is fought on a tug-of-war meter.

### Moves

- **Shared (same sprites for everyone):** the full Tecmo World Wrestling move set (see Controls).
- **Per wrestler:** 2 extra moves plus 1 finisher.
- **Finisher:** everyone has one. It's the big closing move, but it's not an instant win. You still have to pin them afterward: the opponent goes down and still *might* mash their way back up. That's what keeps matches exciting.

### The two meters

| Meter | Where | What it does |
| --- | --- | --- |
| Energy meter | Top of the screen | Standard health. Hits drain it. How low it is decides who wins, and it also weights every struggle. |
| Tug-of-war meter | Just under the top bar, only during a struggle | Mash to push it to your side. Like the SNES WWF games (Royal Rumble). No numbers, just the bar. |

**One meter graphic for every struggle (decided).** Same look everywhere, same rules underneath:

- **Two-sided (true tug-of-war), both mash:** tie-ups and submissions.
- **One-sided, only you mash:** pins, getting up, and shaking off a stun. You push toward the white line, and how far you need to go depends on your energy (the get-up numbers).

**Energy weights the mashing.** Mashing speed matters, but energy decides how much each press is worth, so a fresh wrestler has the edge and a fast masher can still fight back.

`push per press = 0.5 + (energy% ÷ 100)`

| Wrestler | Energy | Presses/sec | Push/sec |
| --- | --- | --- | --- |
| You | 100% | 6 | 9.0 |
| CPU | 40% | 8 | 7.2 |

You win this tie-up even though the CPU mashes faster. All numbers get tuned by playtesting.

**Balancing the tug-of-war (draft)**

1. **Energy weights each press** (the formula above). A fresh wrestler has the edge.
2. **Mash speed cap.** Only count presses up to about 10 per second, so turbo controllers and super-fast mashers can't dominate.
3. **The CPU mashes at human speed.** The CPU's speed rises with difficulty but always stays under the cap. The SNES WWF games let the CPU out-mash humans, and players hated it.
4. **Short tie-ups.** A tie-up lasts about 2 seconds at most. If nobody wins, both wrestlers break apart. Mashing comes in short bursts, never long ones.
5. **"Don't give up yet!"** twice per wrestler per match (see below).
6. **Wear them down first** (an idea from the N64 games): big moves are harder to win against a fresh opponent. The energy weighting already does this.

**When the tug-of-war meter appears (energy-gap rule)**

- **Energy within 30% of each other** (for example 60% vs. 75%): the meter appears and you mash it out.
- **30% or more apart** (for example 50% vs. 80%): no meter. The fresher wrestler wins the tie-up automatically. This cuts down on mashing a lot.
- **Exception, "Don't give up yet!":** twice per wrestler per match, the underdog still gets the meter, called out by the announcer (see below).

### Reversals (from the N64 games)

Go for a big move too early and it backfires. The reversal reuses the same throw sprites with the roles swapped.

| Move | Safe when the opponent's energy is | Too early means |
| --- | --- | --- |
| Throw / body slam | Anytime | — |
| Big moves | Under 70% | The tie-up gets much easier for the receiver. Not an automatic reversal, but they barely have to mash. |
| Finisher | Only available under 30% | Can't happen |

**"Don't give up yet!"** Twice per wrestler per match, a wrestler who's far behind in energy gets a push: a tie-up they'd lose automatically goes to the meter anyway, and their presses count extra. There's no pop-up graphic. The announcer says it, so the player knows it happened.

**Energy recovery:** every 10 seconds without being hit, energy goes up 10%, to a max of 100%. It works all the time: standing, down, or outside.

**Mashing fatigue watch:** the SNES WWF games were criticized for making every move a mash-off. Keep mashing to the big moments, and track how much a match asks for.

### Striking, stun, and knockdowns

- **Block (D, when close)** blocks punches, kicks, running attacks, and top-rope dives. A block takes no damage.
- Hits don't freeze you, so you can always move away.
- **Stun:** 3 unblocked hits in a row stun the opponent for 5 seconds (mashing shortens it). A stunned wrestler stays standing, wobbling with stars overhead, and you can do grapple moves on them, like suplexes and body slams. Walking away resets the hit count.
- **Knockdown:** one more hit while stunned knocks them down. Throws, slams, and finishers also knock down.

**Anti-spam (decided):**

- **Attacker:** after 3 blocked hits in a row, the attacker gets pushed back a step and has a short recovery, reusing the "got hit" frame.
- **Blocker:** you can't hide behind block forever. Walking into a blocker starts a tie-up, and a tie-up can't be blocked.
- **B**lock can't be held for more than about 3 seconds before it drops.

### Taunt (decided: all five effects, kept small)

Taunting (D when far away) is a risk-and-reward move. You're wide open while you do it. If you finish the taunt without getting hit:

1. **Hype:** the crowd pops, and your next hit does extra damage.
2. **Second wind:** you get a small bit of energy back.
3. **Show-off points:** score points.
4. **Bait:** the CPU gets annoyed and is more likely to charge at you, which sets up a counter.
5. **Personality:** every wrestler's taunt is their own pose.

Keep each effect small, since together they add up. A louder crowd in later arenas makes the hype bigger.

### Tie-ups (copied from Tecmo, meter from SNES WWF)

- A tie-up starts automatically when the wrestlers walk into each other. There's no grapple button.
- The tug-of-war meter appears. Whoever pushes it to their side gets their move in.
- You can't block a tie-up; mashing is the defense.

### Getting up

- **30% energy or more:** you get up on your own after a moment.
- **Under 30%:** you have to mash to get up within 5 seconds. The lower your energy, the harder it is.

**Get-up numbers (decided).** Most people mash about 5–7 presses a second, and fewer when they're tired or it's a long match. So this tops out around 4 per second:

| Energy | Presses to get up (in 5 sec) | Per second |
| --- | --- | --- |
| 0% | 20 | 4 |
| 10% | 16 | about 3 |
| 20% | 12 | about 2.5 |
| 30% | 8 | about 1.5 |

**If you fail:** you stay down and get another 5-second try, but you're open to a pin or stomp the whole time. The CPU uses the same numbers.

While you're down, the opponent can do ground moves: pin, stomp, elbow drop, or a submission (leg hold).

### Win conditions

**Pinfall, submission, and count-out.**

- **Pin:** the ref counts to 3 while the meter shows. Only the pinned wrestler mashes; the pinner just holds. Kick out by reaching the target before 3, using the get-up numbers: less energy means more presses. The meter always shows for pins; the energy-gap rule doesn't apply. Pins are allowed anytime but only count inside the ring. Outside, only the count-out applies.
- **Submission:** a tug-of-war where both wrestlers mash. The hold drains the victim's energy while it lasts. Push the meter to your side to escape; if it reaches the attacker's side, you tap out.
- **Count-out:** 20 seconds (slower against your nemesis). A double count-out ends the match and counts as a loss for the player in single-player. Count-breaking is allowed: roll back in and out to reset the count.
- **No KO in v1. Removed to keep things simple**.
- **No time limit and no double KO. A match timer runs in the background only so the win screen can show the match length**.

### Movement, ropes, and outside

- Free 8-direction movement on a Tecmo-style angled ring. It looks more alive than a flat side view.
- **The big change from Tecmo:** Tecmo only runs left and right. We run and bounce off all four sides.
- Double-tap to run. You can bounce back and forth as long as you like, and pressing D stops the run.
- Two running wrestlers who collide both bump, reusing the "got hit" sprite.
- Going over or under the ropes uses the same sprite, just at a different position.
- **Outside the ring:** every in-ring move works outside. The count-out runs while you're out there.

### Top rope

- Walk to a corner and press up to climb, like Tecmo. You can climb anytime, but the opponent can run in and knock you off.
- Knocked off, you fall to the floor outside, near that turnbuckle.

| Action | Reused sprite |
| --- | --- |
| Climbing | Walk frame, stepped up the turnbuckle |
| Standing on the top rope | Taunt or signature pose |
| Diving | Thrown/airborne frame |
| Landing | Knocked-down frame |

### Referee

- Stands in the ring and does all the counts. Generic for now; he may become a friend later.
- **Fair in every match except against your nemesis** (single-player only): he counts slower when you pin the nemesis, and way slower when the nemesis is outside. No DQs or restarts. Locked for now; may change later.

### CPU and balancing (approved standard version, tune later)

The standard approach: the CPU gets a little better at a few simple things each match. It's never superhuman, and every CPU has a habit you can learn and exploit.

| Setting | Match 1 | Match 2 | Nemesis (final) |
| --- | --- | --- | --- |
| Mash speed (presses/sec, always under the 10/sec cap) | 4 | 5.5 | 7 |
| Reaction delay before acting | 0.5 s | 0.35 s | 0.25 s |
| Chance to block your strikes | 20% | 40% | 60% |
| Chance to try a big move too early (a mistake you can punish) | 30% | 15% | 5% |

- **Habits:** each CPU wrestler repeats a pattern, like always running after a knockdown, or always going for the top rope. Learning it is how you beat them.
- **Same rules as the player:** the CPU uses the same energy weighting, the same get-up numbers, and gets "Don't give up yet!" too.
- **Never cheats:** no hidden damage bonuses and no mashing faster than a human could.

### Still open in this section

- [ ] Anti-spam: decided, all three rules
- [ ] Failed get-up: decided, another 5-second try while open to attack
- [ ] Double count-out: decided, a loss for the player
- [ ] Finisher close-ups: v2

## Game structure

Single-player is a short run: **3 matches**, with your nemesis last. Beat your nemesis and you win the title belt. v2 adds more matches and the hidden champion.

**Players:** v1 has 1 PLAYER mode and VS MODE against the CPU. VS against a second player is planned but hidden until v2.

**Losing, passwords, and score:** after a loss, the game-over screen shows your password right away, so you can continue later. **Score:** continuing resets your score to 0, so a low score shows you needed continues. Points are listed under Words, codes and score. One life: any loss ends the run, and you continue from the password. Score is kept, with a high-score table that takes full names (longer than 3 letters). The title menu has a Password option.

**Matches:** normal one-on-one singles matches only. No story mode or special match types in v1.

**Run order (decided):** you face the other two wrestlers first, then your **nemesis last** for the title. Each wrestler's order is fixed.

| Wrestler | Nemesis (decided, rock-paper-scissors) |
| --- | --- |
| Mighty Mike | Nimble Niko (speed and reach keep Mike away) |
| Nimble Niko | Big Beefy Stew (his charges flatten Niko) |
| Big Beefy Stew | Jim "The Goat" (holds punish Stew's slowness) |
| Jim "The Goat" | Mighty Mike (out-muscles Jim) |

**Champion:** no champion in v1. The hidden champion (figure-four, veteran style) arrives in v2.

**Ending:** you win the title belt, then a cheap, old-school ending scene like old Street Fighter, then credits.

**CPU difficulty:** the CPU gets harder with each match. Every wrestler has a weakness or trick that beats them once you learn it.

**Arenas: 4, built on one ring.** The ring itself never changes. Each arena layers more on top of it (crowd, lighting, logos), so the show gets bigger as you climb. The finished look is in the Arenas section below.

| Arena | Crowd | Lighting | Extras |
| --- | --- | --- | --- |
| 1 | Few people, mostly empty chairs | Bright, plain | — |
| 2 | More people sitting | Colorful lights around, not dark | — |
| 3 | About 75% full | Great lighting, flashy lights | Small logos in and around the ring |
| 4 | Completely full, crowd going crazy (movement) | Dark with massive lights | Everything |

**Decided:** one arena per match. With 3 matches, v1 uses **arenas 1, 2, and 4**, so the nemesis finale is in the packed arena, and arena 3 is saved for v2. The higher you climb, the louder the crowd, the more signs, and the livelier the crowd movement (2-frame crowd animation). The crowd also powers the taunt's hype effect. Arenas don't need names; the HWW logo is used everywhere.

**Pause menu:** Continue / Moves List / Password / Quit Match (decided Oct 5). The moves list shows only your own wrestler.

**Gym: moved to v2, not in v1. Saved idea:** Optional, between matches. Pick one exercise; each trains one body stat for the next match only, so the password stays simple. Each exercise uses a different skill, so it's not all mashing, and every exercise reuses existing poses.

| Exercise | Skill | Trains | Reused poses |
| --- | --- | --- | --- |
| Bench press | **Timing:** press when the bar is in the green zone | Power | Lift, plus a barbell |
| Jump rope | **Rhythm:** alternate A and S on the beat | Speed | Stand and walk frames |
| Arm wrestling vs. the trainer | **Mashing:** the tug-of-war meter | Tie-up strength | Tie-up |

## Scope, tech, and open questions

v1 is the smallest game that still feels complete. Bigger ideas wait for v2 and v3.

**In v1:** 4 wrestlers, shared moves plus 2 extras and a finisher each, the top rope, three arenas built on one ring (1, 2, and 4), a referee, a commentator, a 3-match run ending with your nemesis, the entrances, and VS mode against the CPU.

**Later (v2+):** local 2-player, the gym, the hidden champion, finisher close-ups, and anything bigger.

**Parked idea, remember this:** unlockables such as a hidden wrestler, a belt, or a special ending screen.

**Tech:** Python with Pygame. Claude makes the art, code, and music together with you, a piece at a time. Python runs on Windows, Mac, and Linux. Each needs its own build, for example with PyInstaller. Consoles and phones aren't realistic from Pygame. Screen: the game draws at the NES size, 256×240, and scales up cleanly (3× = 768×720, 4× = 1024×960).

**Visual decisions:** all made (see below and the sprite canvas).

- **Colors and palette:** decided: 3 NES colors per wrestler (see the sprite canvas).
- **Wrestler size vs. ring:** chunky wrestlers, but show more of the ring than the NES games did, about 30% more, or the whole ring. Decided: the announcer stays a solid black bar at the bottom. NES-style, but not overly strict.
- **Flicker:** none (decided Oct 5).
- **NES or SNES look:** decided: the Tag Team Wrestling look (style 3 of the sprite test), chosen after seeing the suplex animated in three styles. Small, stubby sprites with big heads, no outlines, and only 3 colors per wrestler (the real NES sprite limit). Side effects: Mike's kneepads and wristbands go red, Stew's singlet loses its white and yellow trim, Jim's red boots go green, and faces are only a few pixels. To fix: the on-screen font (make a proper 8x8 NES-style pixel font).

**Camera (decided): angled 3/4 ring view,** the ring seen from a corner (see the "Mockup: angled ring view" board on the sprite canvas). This replaces the flat side view.

- **Game logic stays flat:** the mat is a simple square grid, and the angle is only how it's drawn. Moves, tie-ups, pins, count-outs and all the rules work unchanged.
- **Sprites:** each pose is drawn in all 4 diagonal directions from the same 3D figure.
- **Running:** double-tap to run straight at the rope you're facing, then bounce back. All four ropes work.
- **Depth:** whoever is closer to the camera is drawn in front. Front ropes and the front post draw over the wrestlers.
- **Controls:** up on the arrow keys is up on the screen (decided).

**Crowd (decided direction):** a packed crowd in the style of the NES boxing games, built from small repeated fans: dark, dim back rows for depth and bright front rows with tiny faces. Character comes from extras layered on top: signs (MIKE!, STEW, HWW, #1, GO!), a foam finger, a photographer, random camera flashes, caps, and fans throwing their arms up (2-frame loop). How full each arena (1 to 4) looks comes from how many fans and extras are drawn.

**Arenas (decided, art done):** every arena uses the same angled ring. Outside the ring the floor is padded blue mats in square panels with light seams, drawn in the ring's perspective (not a flat color). The HWW logo sits on both front apron skirts, slanted to follow the apron, and the skirt has cloth folds. What changes per arena:

- **Arena 1 (first match, Mike vs Jim):** a few fans and empty seats, bright house lights, no signs.
- **Arena 2 (Mike vs Stew):** a fuller crowd with 2 signs and a photographer, plus pink, cyan and yellow lights sweeping across the floor mats.
- **Arena 4 (nemesis title match, Mike vs Niko):** packed crowd, dark house, darker mats, two white spotlights on the ring, camera flashes, a foam finger, and HWW logos along the barrier.

**Two-person moves (decided, art done):** grapples, throws, holds and strikes draw both wrestlers together as one scene, sorted by depth, so whoever is closer to the camera is drawn in front. Each move frame stores the attacker's pose, the defender's pose, where the defender stands relative to the attacker, and which way he faces. The gap between them grows with body size, so a punch on Big Beefy Stew lands on his belly and not inside it. Covered: punch, kick, tie-up, lift, throw, stomp, pin, Boston crab and dive for everyone, plus each wrestler's three signature moves (Mike: powerbomb, military press, bear hug; Stew: running lariat, headbutt, seated butt drop; Jim: sleeper hold, vertical suplex, hip toss; Niko: DDT, flying crossbody, missile dropkick). Each move has 2 frames in all 4 facings.

**Save point (Sep 30):** art for v1 is exported as game-ready sprite sheets at native NES size with transparent backgrounds. Each wrestler has a solo sheet (every move, 4 facings × 2 frames, 64×76 cells) and a two-person sheet (96×88 cells), plus a JSON file naming each row. The three arenas are saved as 8-frame strips at 256×216. The Python that draws everything is saved alongside. **(Updated by the Oct 5 exports: bigger solo sheets and all 12 matchups at 96×96.)**

**Match screen layout (decided, art done):** the full NES screen is 256×240. The top 24 pixels are the black top bar, the arena fills the middle, and the bottom 32 pixels are the black announcer bar. The arena is nudged up 8 pixels so the whole ring and apron fit.

- **Top bar:** both full names in each wrestler's colour (a short name if it doesn't fit), 24 energy pips each (the right-hand bar mirrors the left), and no clock (decided Oct 1: the win screen shows the match length instead). Under 30% energy the pips flash white.
- **Mash meter:** during grapples a tug-of-war bar drops in under the top bar, split in the two wrestlers' colours, with a white marker and a blinking MASH!.
- **Font:** bold 8×8 NES capitals with 2-pixel strokes, numbers, punctuation and a copyright sign for the credits. It can be drawn with a 1-pixel shadow, or at double size for big call-outs like the pin count and DING!.
- **Referee (generic for now):** striped shirt, bow tie, black trousers, built the same way as the wrestlers. Moves: stand, walk, pin count (kneel, slap the mat), count out, ask submit, raise hand, call for bell.
- **Announcer (generic for now):** a 24×24 portrait with slick hair, a headset, a blue blazer and a red tie. His mouth flaps while his 2 lines of up to 27 letters type out; a yellow arrow blinks when the line is finished.

**Wrestler select + profiles (decided, art done):** in the style of the classic NES select screen. Each wrestler has a big 80×72 bust portrait in his signature pose: Mike doing a double-bicep flex, Stew with a yelling fist pump, Jim with his arms crossed and a smug look, Niko pointing one long arm at the sky. Black hair is drawn in deep navy with blue highlights so it shows up on the black background, the NES trick. The select screen is a 2×2 grid with a blinking frame, and the selected name lights up in the wrestler's colour. Each profile card fills in row by row, then shows his catchphrase.

| Wrestler | From | Born | Height | Weight | Record | Specialty |
| --- | --- | --- | --- | --- | --- | --- |
| Mighty Mike | The Iron Dungeon | 7.4.1965 | 5'7" | 244 lb | 88-1-0 | Powerbomb |
| Big Beefy Stew | The All-You-Can-Eat Buffet | 11.23.1961 | 6'8" | 412 lb | 71-9-3 | Running lariat |
| Jim "The Goat" | The Top of the Mountain | 2.29.1964 (leap day) | 6'5" | 318 lb | 99-0-1 | Sleeper hold |
| Nimble Niko | High Above the Clouds | 9.9.1968 | 7'1" | 221 lb | 64-2-0 | DDT |

**Game screens (decided, art done):** all at 256×240.

- **Title:** the HWW logo in orange and red flame bands with sweeping searchlights, the HOME WIDE WRESTLING banner, and all four wrestlers in victory poses on a little stage. PUSH START blinks, then the menu shows 1 PLAYER, VS MODE, PASSWORD and HOW TO PLAY. Credits text: TM AND © 1990 BEST FRIEND GAMES LTD., LICENSED BY FRIENDS OF JAPAN INC.
- **VS:** a split backdrop in both wrestlers' colours. The portraits slide in and face each other, then a flashing VS, the tale of the tape (height, weight, record) and FIGHT!.
- **Win:** the winner under a spotlight with confetti, his catchphrase, how he won and the time, then NEXT OPPONENT. After the last match it says HOME WIDE CHAMPION! instead.
- **Lose (game over):** gloomy rain, the winner's portrait and catchphrase, how you lost, a big GAME OVER, and your password in a box (one life plus password).
- **Password:** 8 characters shown as XXXX-XXXX. The letter grid leaves out I, O, 0 and 1 so the code is easy to copy off the TV. DEL and END, with a message when the code is accepted.
- **Pause:** the live match dims behind a menu window with CONTINUE, MOVES LIST, PASSWORD and QUIT MATCH.
- **Credits:** scroll up over twinkling stars: the logo, the four stars, game design (Mighty Mike), art, code and music (Claude), the ref and announcer, special thanks, the © line, and THANK YOU FOR PLAYING!

**Sound (decided, made):** keep it minimal and reuse everything. All sound is NES-style chiptune made in code from the console's own voices: two square waves, a stepped triangle for bass, and a noise channel.

| Sound | Used for | Reused as |
| --- | --- | --- |
| Blip | Menu cursor, password letters, announcer text | Mash press (higher), wrong password (low and backwards) |
| Select | Pick an option, PUSH START, password OK | — |
| Hit | Punch, stomp | Kick (lower), the ref's count slaps (lower, quieter) |
| Slam | Slams, throws, powerbomb, suplex, knockdown, dive | — |
| Grunt | Big hit taken, lifting, getting up | Pitched per wrestler: Stew low, Jim, Mike, Niko high |
| Whiff | Missed punch or kick | Blocked hit (shorter) |
| Bell | Match start and end, the win DING! | — |
| Crowd | Cheer after big moves, taunts, kick-outs, the win | — |

**Music (3 tracks):** a heroic menu theme in C major (title, select, password, credits); a driving match theme in A minor for every match, played faster for the nemesis match; and a short win fanfare, which becomes the lose jingle when played in minor, slow.

## Hole check (Oct 1)

A full read of this doc against everything built so far. Decided so far:

1. **No clock on the match screen.** The top bar shows only names and energy. The match timer still runs in the background, and the win screen shows how long the match lasted.
2. **Run order (1 player) is locked:** Mike faces Jim, Stew, then Niko. Niko faces Mike, Jim, then Stew. Stew faces Mike, Niko, then Jim. Jim faces Niko, Stew, then Mike. **New: a VS mode** where you pick who you fight. VS mode can be against the CPU or against a second player, but **versus a second player is switched off in v1**. It comes back once the controls feel right.
3. **Finisher buttons:** Mike's powerbomb is tie-up Down+S, Niko's DDT is tie-up Up+S, Jim's sleeper is tie-up A, and Stew's lariat is running A. Players learn them from a **moves list in the pause menu**, which shows every move, what to press, and your finisher.
4. **Ground drops:** Mike does an elbow drop, Jim and Niko do a knee drop, and Stew does his seated butt drop.
5. **Score is kept:** hit 100, slam 300, taunt 300, finisher 2,000, win 5,000, plus a bonus for a quick win.
6. **Passwords:** Nintendo-style random-looking codes. Each wrestler has a coded name, and each wrestler and match number pair maps to its own fixed code. The real codes are listed under Words, codes and score.
7. **Taunt = the victory pose**, which is already unique for each wrestler.
8. **Entrance: important. Mockup done Oct 5 (see the Entrances board).** The idea is a WWE-style entrance: a ramp with a big video screen behind it showing the wrestler, fireworks, and the wrestler hitting his victory pose at the top of the ramp before walking down to the ring.

**Also decided (Oct 5):** Claude writes generic announcer lines for now, and Mike may swap in his own later. No mirror matches: a wrestler can't fight himself. Claude makes up the password codes.

**Final answers (Oct 5):**

- **Moves:** keep all 12 extra Tecmo moves (headlock, knee lift, brain buster, pile driver, back drop, rope whip, shoulder throw, clothesline, dropkick, knee/elbow drop, flying knee drop, post slam). They're built from existing poses, plus one new headlock pose.
- **Top rope:** add a climbing pose and a standing-on-top pose.
- **Score:** a top-5 high-score table with name entry.
- **Ending:** the champion holds the title belt over his head with fireworks, then the credits.
- **Title menu:** 1 PLAYER / VS MODE / PASSWORD / HOW TO PLAY, plus a difficulty choice of Easy / Medium / Hard for testing.
- **VS mode:** VS PLAYER is hidden in v1. You pick the arena and the CPU difficulty. After a VS match you go to New Match.
- **Pause menu:** Continue / Moves List / Password / Quit Match. The moves list shows only your own wrestler's moves, one page per situation.
- **Secret passwords:** yes, a few fun cheat codes.
- **Effects:** all of them: hit sparks, a finisher screen flash, and a shake on slams.
- **Also decided:** no flicker; the meter stays under the top bar; the bar is called "energy"; two-person moves for every matchup; a one-sided meter for pins and getting up; reused sounds for rope bounce, climbing, tap-out and finishers; the count-out shows big 1–20 numbers.
- **Entrance:** a mockup comes first (ramp, big screen, fireworks, victory pose at the top).

## Words, codes and score (Oct 5)

**Passwords:** 8 letters shown as XXXX-XXXX, using only the password grid letters (no I, O, 0 or 1). The first half is the wrestler's coded name and the second half is the match.

| Wrestler | Coded name | Match 1 | Match 2 | Match 3 (nemesis) |
| --- | --- | --- | --- | --- |
| Mighty Mike | MGHT | MGHT-K7RQ | MGHT-Z4WD | MGHT-X9PB |
| Big Beefy Stew | BEEF | BEEF-H3NV | BEEF-Q8MT | BEEF-W2CJ |
| Jim "The Goat" | BAAH | BAAH-R6FZ | BAAH-D5KX | BAAH-N7YG |
| Nimble Niko | TALL | TALL-P4SE | TALL-J9VA | TALL-U3HM |

**Secret codes** (typed on the password screen):

- **HVGE-HEDS:** big heads for everyone, until the game is turned off.
- **THNK-YALL:** plays the ending and credits straight away.
- **BELT-TYME:** skips straight to your nemesis title match.

**Score:** hit 100, slam 300, taunt 300, finisher 2,000, win 5,000. Quick-win bonus: +3,000 under 1 minute, +1,500 under 2 minutes. The top 5 go in the Hall of Fame with full names (up to 10 letters).

**Announcer:** generic lines for now, all in game\_text.py, each 2 lines of up to 27 letters. They cover the intro, bell, strikes, stuns, tie-ups, slams, the top rope, taunts, finishers, pins, the count, kick-outs, submissions, rope breaks, fighting outside, "Don't give up yet!", low energy, reversals, each kind of win, and the new champion. Mike can swap in his own lines any time.

**Art added Oct 5:** all four entrances (ramp, big screen, pyro, victory pose), the 12 extra moves plus the top-rope climb and stand poses, two-person sheets for all 12 matchups, title menu with difficulty, VS mode setup, pause moves list (your own wrestler only, 7 pages), How to Play, Hall of Fame, name entry, the champion ending with the title belt and fireworks, and the effects (hit sparks, finisher flash, slam shake, one-sided KICK OUT! meter).

**Sprites are built as simple 3D figures:** each wrestler's body, limbs and head are rounded shapes on a skeleton, drawn as Tag Team-style pixels from any angle. One pose gives all 4 facings, so the angled view doesn't double the work. Each wrestler is finished one at a time, all moves, before moving on.

**Mighty Mike: done (first pass).** 24 moves, 2 frames each, in all 4 facings: stand, walk, run, punch, kick, block, taunt, hit, stunned (with stars), knocked down, get up, tie-up, lift, throw, being lifted, being thrown, pin, stomp, dive, sit up, victory, powerbomb (finisher), military press, bear hug. Kneepads dropped (they turned into red spots at this size).

**Big Beefy Stew: done (first pass).** The same 20 shared moves plus his own: fist-pump victory (yelling), running lariat (finisher), headbutt, seated butt drop. Body widened so he's clearly the biggest wrestler. Fixed: his singlet no longer reaches his face, his guard sits at chest height, and his hair covers his head.

**Jim "The Goat": done (first pass).** The shared moves plus his own: victory (arms up, then pointing), sleeper hold (finisher), vertical suplex, hip toss. Green one-strap singlet, full blond hair, small goatee, chubby build, guard held wide so his arms don't blend into his body. The Boston crab was added to everyone's shared moves (Mike and Stew updated too).

**Nimble Niko: done (first pass).** The shared moves plus his own: victory, DDT (finisher), flying crossbody, missile dropkick. Tallest and skinniest, navy tights, bare chest, a bowl of shaggy black hair with his face peeking out under the bangs.

**All four wrestlers are built (first pass).** Two-person moves and all exports are done (see Oct 5).

**Sound and music (later):** done. See the Sound section above (8 effects, 3 songs).

## Building the game (Oct 5)

The playable game is built in 13 steps, one at a time, each ending with something to try before moving on: (1) window and loading, (2) movement, (3) two wrestlers and the HUD, (4) striking, (5) tie-ups, (6) running and ground moves, (7) ropes, outside and top rope, (8) specials and finishers, (9) referee, announcer and sound, (10) CPU, (11) screens and flow, (12) the single-player run, (13) tuning and build. The code lives in `game/` next to `export/`, and reads the art straight from `export/sprites`.

**Step 1 done (Oct 5):** a 256×240 window scaled 3× with sharp pixels (F11 for fullscreen), the keyboard, and every sprite sheet, the font and the arenas loaded. The arenas are split into a back layer and a front-ropes layer, so wrestlers stand inside the ropes. A test screen shows any wrestler (or the ref) doing any move in any facing, in arena 1, 2 or 4.

**Step 2 done (Oct 5): movement.** Up on the arrows is up on the screen. One arrow walks straight up, down, left or right on screen; two arrows together walk along a rope, the same way the 4 facings point. Walking is the same speed across the mat in every direction, set by the Speed stat (Niko fastest, Stew slowest). Double-tap an arrow to run at the rope you're facing: the runner presses into the rope for a moment, springs back the other way, and keeps bouncing off any of the four ropes until D stops him. Wrestlers can't go past the ropes yet (outside comes in step 7). Whoever is closer to the camera is drawn in front.

**Step 3 done (Oct 5): two wrestlers and the HUD.** The real match screen: you against a CPU wrestler, with the ref standing in his corner. The CPU presses the same buttons a player would; for now it just wanders the ring and turns to face you when it stops (the real CPU is step 10). Bodies can't overlap: each wrestler has a size on the mat (Stew biggest, Niko slimmest), a run into the other wrestler just stops for now (bumps are step 6), and the ref gets shoved aside until he moves on his own (step 9). The top bar shows both full names in their colours (a short name if one doesn't fit) and 24 energy pips each, the right bar mirrored, flashing white under 30%. The announcer bar types out the intro (the contest, then each wrestler's hometown and name, then the bell) with his mouth flapping, and the yellow arrow blinks when a line is done. The words come from `game/hww/game_text.py`, a copy of the one in `export/source`, so Mike's own lines go there.

**Step 4 done (Oct 5): striking.** Decided: **auto-facing.** Standing still or attacking, you turn to face the opponent by yourself; while walking you face the way you walk. A punches, S kicks. Hits don't freeze you: after a moment you can walk out of a hit. Reach: punches and kicks land only if the opponent is in front of you and close enough, and Mike's reach is the shortest and Niko's the longest (the balance note). Damage is scaled by Power. Three unblocked hits in a row stun the opponent for 5 seconds (mashing A/S shortens it, with a one-sided SHAKE IT OFF! meter); one more hit knocks him down. Walking away, or 2 seconds without a hit, resets the count. D blocks when close (no damage, drops after 3 seconds held), and 3 blocked hits in a row push the attacker back. D far away taunts with the victory pose: if you finish it, your next hit does 1.5× damage, you get 3% energy back and 300 points. Getting up uses the get-up numbers: 30% energy or more and you're up on your own; under 30% a GET UP! meter appears and you mash (20 presses at 0%, down to 8 at 30%), with another 5-second try if you fail. Every 10 seconds without being hit gives back 10% energy. Hit sparks from the effects art appear on every clean hit, and the announcer calls stuns, knockdowns, taunts, low energy and some of the hits. A downed wrestler still takes up space, so the other one steps off him. Starting numbers (to tune by playtest): punch 4%, kick 6% of full energy, times Power 0.85 / 1.0 / 1.2. Until the real CPU (step 10), a stand-in CPU walks up and trades punches and kicks, blocks about 30% of the time, and mashes 4 presses a second.

**Step 5 done (Oct 5): tie-ups.** Walking into each other locks you up (no grapple button; walking into someone blocking or stunned works too). The tug-of-war meter drops in under the top bar in both colours with a blinking MASH!: hold a direction and mash, and the button and direction you press pick your move. Each press is worth 0.5 + energy, Power adds a small push bonus (Mike +10%, Niko −5%), presses past 10 a second don't count, and the first to push the bar 4 presses-worth ahead wins. Nobody wins in 2 seconds: they break apart. Energy 30% or more apart: no meter, the fresher wrestler's first press does his move, unless the underdog still has a "Don't give up yet!" (2 per match), which brings the meter back with his presses worth 1.5× and the announcer calling it. A stunned wrestler can't fight a tie-up. Too early: going for a heavy move (back drop, brain buster, pile driver) while the opponent is at 70% or more makes his presses worth 2.5×, and the announcer calls the reversal. Stew is harder to lift (his presses worth 1.25× against body slam, brain buster and pile driver), and Niko gets thrown farther. The moves play from the two-person sheets: knee lift (5%, staggers him back), headlock (7%), body slam (10%), back drop (13%), brain buster (14%), pile driver (16%); slams knock him down and score 300. Rope whip (D + an arrow, all four ropes) sends him running; he bounces back, and A or S as he comes at you is a shoulder throw (10%). If you miss him he takes back control after the next rope. Running into someone just stops for now (bumps are step 6). The stand-in CPU sometimes walks in for a tie-up, mashes 4 a second, only sometimes tries a big move too early, and catches you with a shoulder throw most of the time.

**Step 6 done (Oct 5): running and ground moves, and the first full win.** Running: A clothesline (9%), S dropkick (10%); both knock him down and score 300, block stops them and bounces you back, and a missed dropkick lands you on your back (you get up on your own). Two runners who meet both bump; if one is heavier, the lighter one goes down (Stew flattens everyone, Niko loses to everyone). Ground moves on a downed opponent: A pin, Up/Down+A stomp (4%), Left/Right+A Boston crab, S knee drop (Jim, Niko) or elbow drop (Mike) (7%), and Stew's seated butt drop (8%). He stays down a moment longer after each. **Pin:** the ref hustles over, kneels beside them and counts, slapping the mat, with a big yellow 1, 2, 3 on screen. Only the pinned wrestler mashes (A, S or D) on a one-sided KICK OUT! meter, using the get-up numbers: 20 presses at 0%, 8 at 30%, down to 3 when fresh. **Boston crab:** a two-sided tug of war on the same meter; the hold drains about 4% energy a second; push the bar to your side to escape, to his and you tap out; after 10 seconds he lets go. **Winning:** pinfall or submission ends the match. The winner does his victory pose, the loser stays down, the ref raises the winner's hand, and the announcer calls it. Score: win 5,000, +3,000 under a minute, +1,500 under two. PUSH ENTER starts the match again (until the real screens in step 11). The ref now keeps out of the way on his own. The stand-in CPU runs at you for clotheslines and dropkicks, works you over on the ground, pins you when you're under 35%, and mashes 4 a second to kick out.

**Step 7 done (Oct 5): ropes, outside and the top rope.** Decided while building: **you go out over the two front ropes only.** The ring hides the floor behind it, so the floor you can fight on is the two strips in front of the down-right and down-left aprons. Keep walking into a front rope for a third of a second and you climb through (the climb sprite, the same both ways); outside, walk into the apron to climb back in. Anyone on the floor is drawn in front of the ring, with his shadow on the floor. Everything works outside except the pin and running; in a tie-up on the floor, Left/Right+A slams him into the ring post (12%). **Count-out:** the moment anyone is out, the ref goes to the ropes nearest him and counts to 20, one a second, swinging his arm, with big white numbers under the top bar. Everyone back in resets it (count-breaking is allowed). Reach 20 and whoever is still out loses; both out is a double count-out, nobody wins, and that's a loss for the player. **Top rope:** walk into a corner (or press Up there) and you climb the turnbuckle; anytime, but anyone who hits you while you're climbing or up there knocks you off, onto the floor outside near that corner (6%; from the back corner, with no floor to see, back into the ring). Up top you face him: S diving body attack (12%), A flying knee drop (11%), both aimed at him if he's within reach and in the ring, standing or down; walk away from the post to climb down. A block stops a dive, and a dive that hits only mat hurts you (5%). The stand-in CPU follows you outside about 40% of the time, always gets back in by 12, and climbs for a dive about 30% of the time when you're down.

**Step 8 done (Oct 5): specials and finishers.** Each wrestler's 2 specials always replace the default move on the same input, and count as big moves for the too-early rule (the opponent should be under 70%). Mike: military press slam (tie-up Up+A, 13%) and bear hug (tie-up A, 10%). Jim: vertical suplex (tie-up Left/Right+S, 14%) and hip toss (tie-up S, 8%). Niko: flying crossbody (running S, 11%, reaches farther than a dropkick, and a miss lands you on the mat) and missile dropkick (top rope A, 14%). Stew: headbutt (tie-up A, 9%, leaves him seeing stars for 3 seconds) and the seated butt drop (his ground drop). Finishers replace the move on their button once the opponent is under 30%, and before that the normal move comes out: Mike's powerbomb (tie-up Down+S), Niko's DDT (tie-up Up+S) and Stew's running lariat (running A) do 20% and knock him down; Jim's sleeper hold (tie-up A) is a submission like the crab but drains faster (about 7% a second). Every finisher scores 2,000 and gets the finisher flash (the arena goes white, then flickers out in a dither) and the announcer's "HERE IT COMES... THE POWERBOMB!!!". It's not an instant win: you still have to pin him (or he taps). Every slam now shakes the ring. The stand-in CPU goes for its finisher once you're under 30%.

**Step 9 done (Oct 5): referee, announcer and sound.** Every match opens with the intro: both wrestlers in opposite corners, the ref in the middle, and nobody can move while the announcer introduces them (about 7 seconds; Enter or A skips it). Then the bell rings, a big yellow DING! flashes, the ref calls for the bell, and the match music starts (the faster nemesis version is ready for step 12). Sounds, all from the 8 made in code, reused at other pitches: hit for punches, stomps and drops, the lower kick for kicks, whiff for misses, the short whiff for blocks, bumps and rope bounces, slam for every slam, throw, knockdown, crash and fall, grunts pitched per wrestler when he's lifted, slammed, stunned or drags himself up under 30%, the ref's count slaps, a blip per second of the count-out and for climbing, a higher blip for every press while you're mashing on a meter, the announcer's text blips as it types, select under the finisher flash, and the crowd for big slams (12% or more), every finisher, finished taunts (the taunt's crowd pop), kick-outs, escapes and the win. At the end the bell rings, the music stops, and the win or lose jingle plays (lose if the CPU wins or it's a double count-out). M mutes everything.

**Step 10 done (Oct 5): the CPU.** Decided: **Easy / Medium / Hard shifts the whole ramp one step.** Medium is the table above (match 1, match 2, nemesis); Easy starts one step softer (3 presses a second, 0.65 s reactions, blocks 10%, too early 45%) and Hard ends one step tougher (8.5 a second, 0.18 s, blocks 70%, too early 2%), always under the 10-a-second cap. Measured in the game: the CPU really mashes at 3.0, 3.9, 5.4, 7.0 and 8.4 presses a second, and decides to block 19%, 40% and 60% of the time from match 1 to the nemesis. The reaction delay: whenever something changes (you go down, get up, come back in), he waits that long before he attacks, grabs or runs. Too early: in a tie-up he only goes for a big move (or a special) while you're at 70% or more by mistake, at the table's rate; under 30% he goes for his finisher. **Habits:** Mike walks straight in for tie-ups and rarely strikes (kick him from range); Niko heads up a turnbuckle often, even while you're standing, and waits for you (run in and knock him off); Jim goes for the Boston crab when you're down and takes his time setting it up, so if you get up first he's left standing there open for about a second; Stew backs off to get room and charges with clotheslines over and over, and if you block one he stands there open for about a second after the push-back. **Taunt bait:** finish a taunt and the CPU is annoyed for 5 seconds and charges at you (it did in 10 out of 10 tries), which sets up a block or a counter. Same rules as you: the same energy weighting, get-up numbers and "Don't give up yet!", and no cheating. **Also decided while testing:** a submission can only make someone tap once he's under 30% energy; above that the hold drains him (Boston crab about 2.4% a second, Jim's sleeper about 5%) until he escapes or the attacker lets go after 6 seconds. Before this, the faster masher could make a fresh wrestler tap in 10 seconds, which ended almost every CPU-vs-CPU test that way. A runner now shoves the ref aside instead of stopping on him. A stress test of all 12 matchups, CPU against CPU, ran clean; matches lasted 30 to 100 seconds.

**Step 11 done (Oct 5): screens and flow.** The game now runs screen to screen, with the menu theme on the menus. Title: the logo with sweeping searchlights, the banner, the four wrestlers in their victory poses on the stage, the © lines, and PUSH START, then the menu (1 PLAYER, VS MODE, PASSWORD, HOW TO PLAY). 1 PLAYER: difficulty (Easy, Medium, Hard), then the select screen (2×2 portraits, blinking frame; S shows the profile card filling in row by row with the catchphrase), then each match: the VS screen (MATCH 1 OF 3, MATCH 2 OF 3, MATCH 3: NEMESIS!), both entrances (the CPU's first, then yours; A skips), the match (arena 1, 2, then 4 for the nemesis), then the win screen (how and how long, NEXT OPPONENT or HOME WIDE CHAMPION!) or the lose screen (GAME OVER and your password). VS MODE: you, the CPU (no mirror matches), the arena and the level, then VS screen, entrances and the match, then back to the setup for a new match. PASSWORD: the letter grid without I, O, 0 and 1, DEL and END; a good password picks up the run at that match after you choose the difficulty, a secret code is recognised (what they do comes in step 12), and a wrong one gets the low error blip. HOW TO PLAY: the controls page. In a match, Enter pauses: CONTINUE, MOVES LIST (your wrestler only, Left/Right turns the 7 pages, finishers blink), PASSWORD (your current password), QUIT MATCH (back to the title). The logo, the title backdrop and the entrances are built once from the art source and the exported reels (game/tools/build_screen_assets.py), along with a complete copy of the font, because the exported font sheet left out < > * % + =. The test keys in matches now need debug on (F3). Still for step 12: the score, the Hall of Fame, what the secret codes do, and the champion ending and credits (winning match 3 goes back to the title for now).

**Step 12 done (Oct 5): the single-player run.** The score now carries from match to match and shows on each win screen; a run picked up from a password starts at 0. Win the nemesis match and it's the win screen (HOME WIDE CHAMPION!), then the champion ending for whoever you played (belt held overhead, fireworks over the packed arena 4 crowd, the announcer's call, the win jingle), then the credits scrolling over the stars to THANK YOU FOR PLAYING! (hold A to speed them up). Then, win or lose, a top-5 score gets NEW HIGH SCORE!, name entry (up to 10 letters with SPACE, DEL and END) and the Hall of Fame with your new line blinking. The Hall of Fame starts with MIKE, STEW, JIM, NIKO and BFG and is saved on the computer (in the user's AppData folder), so it lasts between games. **The crooked ref:** against your nemesis only, he counts pins half again as slowly when you pin him (about 1.25 seconds a count instead of 0.8), and counts him out way slower when he's on the floor (1.75 seconds a count instead of 1). **Secret codes** (typed on the password screen): HVGE-HEDS gives everyone big heads until you quit (every sprite sheet was re-rendered from the 3D figures with the heads drawn twice as big; game/tools/build_bighead_sheets.py), THNK-YALL plays the champion ending and the credits, and BELT-TYME goes straight to the nemesis title match with Mighty Mike, the first wrestler on the select screen. The champion ending for each wrestler is rendered from the art source (export/champion_demo.gif only had Mike).

**Step 13 done (Oct 5): tuning and build. v1 is complete.** The balance pass used the CPU against itself, every matchup, both sides at the same level (game/tools/balance_sim.py, about 200 matches a run). What it found and what changed:
- **Tie-ups almost never produced a move** (10–17%): two equal mashers rarely got a full lead in 2 seconds. Now, when time runs out, a clear leader (40% of the bar or more) still gets his move; only a near-tie breaks apart.
- **A downed wrestler could be stomped forever**: every ground move restarted his get-up clock. Now a ground move only pauses it, so he gets up on schedule (one or two shots per knockdown).
- **Submissions ended most matches**: the tap-out line moved from 30% to **15%**; above that a hold only drains.
- **The ref stood in the way**: he walked into charging wrestlers and stalled them. Now he always gives way and steps away from the nearest wrestler.
- **Numbers:** clothesline 9% → 7%; the Power push bonus in tie-ups narrowed (Mike +10% → +5%, Niko −5% → −3%); Mike's punch reach 6 → 7 (still the shortest); Niko's reach 10/13 → 11/15 (his designed edge); Niko's strike damage 0.85× → 0.9×; Stew's CPU charges a bit less often.
- **Result** (same-level CPU vs CPU, habits on): Mike 43%, Stew 52%, Jim 55%, Niko 47%; matches average 1.8 minutes; about half end by pin, the rest mostly by submission, a few by count-out; finishers show up in most close matches. With the habits off, Power decides almost everything (Mike first, Niko last), because the CPU doesn't use speed and reach the way a player can. That's the balance note's point, and it's left for playtesting by hand.

**The build:** dist/HomeWideWrestling.exe, one file of about 21 MB with an HWW icon; it runs without Python. Rebuild with `python game/tools/build_exe.py`. The Hall of Fame lives outside the .exe (AppData), so it survives rebuilds. Mac and Linux need their own builds, made on those systems.

**Releases and the website (Oct 5).** After every update, `python game/tools/make_release.py "Version N"` puts a "Home Wide Wrestling - Version N" folder and zip in the main project folder (the Windows .exe, launchers for Windows, Mac and Linux, HOW TO PLAY.txt, the game) and a "Website Upload (Version N)" zip: the browser version, built with pygbag like the ELSC game, ready to unzip next to wp-admin on the WordPress site (READ ME FIRST.txt and a Custom HTML embed snippet inside). In the browser the sounds are OGG, the Hall of Fame is kept in each player's own browser, and there's no Esc-to-quit or F11 (the page has its own full screen).

**Version 2 (Oct 6): the crowd signs follow the match.** From the Oct 6 art update: in arenas 2 and 4 the fans hold signs with both wrestlers' names plus a fan sign each (MIGHTY, BEEF!, GOAT, TALL) instead of always MIKE and STEW; arena 1 (the small crowd) still has no signs. The game builds a back layer per matchup from the updated export/source/arenas.py and crowd.py (game/tools/build_arena_layers.py), with the player's wrestler as p1, and each match loads its own.

**Open questions**

- [x] Characters: gimmicks, recognizable sprite details, nemesis pairings, finisher assignments, special moves, habits
- [x] Which friends are the referee and the announcer
- [x] Logo design for Home Wide Wrestling
- [x] Visual examples: colors, wrestler size vs. ring, flicker, NES vs. SNES
- [x] Arena details
- [x] Starting damage numbers for each move (set Oct 5 in the build and the balance pass; fine-tune by playtest)
