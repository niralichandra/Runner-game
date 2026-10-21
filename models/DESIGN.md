# Romantic Runner — 10 Map Design Breakdown & Integration Guide

Every map uses the same gameplay grid and asset conventions as the original set. You can drop the new maps into the existing game without touching movement, collision or track generation; only the art changes.

---

## Shared rules (all 10 maps)

| Rule | Value |
|---|---|
| Lanes | x = −2.6 / 0 / +2.6 m |
| Running direction | +Y in Blender = −Z in glTF / three.js = +Z in Unity (FBX) |
| Ground segment | 10 m long, tileable, origin at segment start |
| Running surface height | 0.44 m (stone paths) · 0.56 m (rail tops) · 0.32 m (plank bridge) |
| Clear running corridor | 8.4 m wide, nothing decorative below 6 m over the lanes |
| Low obstacle (`obstacle_low`) | ≤ 1.3 m tall → **jump** |
| High obstacle (`obstacle_high`) | blocking bar from ≈ 1.5 m up → **slide** |
| Train (`obstacle_train`) | 12 m long, roof ≈ 3.7 m; reach the roof via a `ramp` |
| Collectible (`coin`) | themed shape about 0.9 m tall, faces the player, hovers at surface + 0.75 m |
| Power-up (`powerup`, new) | ≈ 1 m icon, hovers at surface + 1.1 m |

**Visual language shared by all maps:** rounded, chunky shapes; baked painted textures (albedo + normal); pink / peach / lavender / cream / gold accents; glowing heart motifs; and a warm key light with a cool fill. The foreground holds walls, lamps and flowers; the mid-ground holds trees, houses and statues; the background holds a big landmark plus sky elements.

---

## 1 · Enchanted Jungle Temple
- **Mood:** a magical ruin that has just been discovered. Bright late-morning sun and a pink-to-blue sky.
- **Track:** warm brown flagstone path with low mossy walls. Pink hibiscus grows on the wall tops.
- **Landmark:** stepped stone temple with vines. A **glowing heart emblem** with a gold outline hangs above the doorway, and there are stone stairs in front.
- **Side elements:**
  - Heart lanterns and fire torches alternate on the wall posts.
  - Flowering jungle trees, palms, ferns and flower bushes.
  - Tiki stone statues wearing flower crowns, broken pillars and a side stone archway.
  - Waterfalls and cliffs, with **butterfly swarms** hovering at head height.
- **Obstacles:** spiked stone block (jump) · vine beam gate with flowers (slide) · fallen mossy log (jump).
- **Pickups:** **Emerald gem** in a gold frame with leaves (collectible) · **Magnet** · Heart (extra life).

## 2 · Romantic City Subway
- **Mood:** a sunny European old town on a celebration day.
- **Track:** three-lane railway with a cream sidewalk and a pink curb.
- **Landmark:** a big **city gate arch** with turret roofs and a glowing heart, high above the tracks.
- **Side elements:**
  - Pastel buildings (rose, peach, lavender, cream, coral, mint) with **flower boxes under every window**, a heart shop sign, striped awnings and balconies.
  - Victorian double lamps with flowers at the base.
  - **Heart garlands** and fairy-light strings across the street.
  - Benches, flower planters, a railway signal, blossom trees and distant towers.
- **Obstacles:** **pink heart train** (dodge, or climb the ramp) · pink-and-white low barrier (jump) · high barrier with a sign (slide).
- **Pickups:** **Pink bow** with a pearl knot (collectible) · **Magnet** · Heart.

## 3 · Sunset Desert Kingdom
- **Mood:** golden hour. The sky runs from lavender to peach, with long warm shadows.
- **Track:** sandstone tile bridge with carved walls and gold star inlays.
- **Landmark:** **desert palace**: an arched gate, a rose-gold central dome, two domed towers, red banners with gold stars, and arched windows.
- **Side elements:** guardian lion statues, fire braziers, golden heart lanterns, red banner poles, palms, flowering shrubs, rose-coloured dunes and pink cliffs.
- **Obstacles:** heart-stamped crate stack (jump) · **spiked iron ball** trap (jump) · sandstone lintel (slide).
- **Pickups:** **Golden sun** with a spiral (collectible) · **Shield** · Heart.

## 4 · Snowy Fairytale Railway
- **Mood:** a cozy magical night. It's purple rather than black, with warm windows and sparkle.
- **Track:** snowy railway with snow banks.
- **Landmark:** a stone tunnel framed with **pink and gold bulbs** and a glowing heart. A **pink fairy castle** with lit windows rises on the horizon.
- **Side elements:** pastel snow cottages with **light strings along the eaves**, decorated Christmas trees (baubles, light spiral, gold star), snowy pines, Victorian lamps, light strings over the tracks, snow piles and falling snow.
- **Obstacles:** pink-and-white snow train · snow fence (jump) · snowman with a red hat (jump) · snowy heart crates (jump).
- **Pickups:** **Ice snowflake** (collectible) · **Bubble (shield)** · Heart.

## 5 · Romantic Neon City
- **Mood:** a futuristic date night with pink, cyan and violet neon.
- **Track:** wet, reflective rails with glowing pink edges.
- **Landmark:** **neon heart arches** spanning the tracks every 40 m (8 m high). Glowing skyscrapers sit at the end.
- **Side elements:** dark glass buildings with glowing windows, neon strips and **heart outlines on the facades**. Also standing neon heart signs, floating **holographic hearts**, a catenary with glowing insulators, and dark palms.
- **Obstacles:** lilac **future train** with cyan windows · pink X laser gate (jump) · cyan laser bars (slide).
- **Pickups:** **Neon lightning bolt** (collectible) · **Magnet** · Heart.

## 6 · Tropical Flower Island
- **Mood:** a sunny lagoon paradise.
- **Track:** rope plank bridge over **turquoise water**, with **hibiscus clusters on every post**.
- **Landmark:** waterfalls and lush cliffs, with **tiki huts** on the islands.
- **Side elements:** sand-and-grass islands with flower carpets, palms, hibiscus bushes, **parrots on perches**, seashells and starfish, bamboo heart lanterns along the bridge, butterflies and shore rocks.
- **Obstacles:** heart crates (jump) · mossy log (jump) · **hanging flower-garland log** (slide).
- **Pickups:** **Starfish with a pearl** (collectible) · **Magnet** · Heart.

## 7 · Red Canyon Railway
- **Mood:** dramatic sunset canyon, from purple sky to orange horizon.
- **Track:** red-dirt railway.
- **Landmark:** a **natural rock arch** over the line, with **hot-air balloons** (pink and cream, lavender, peach and gold) floating in the sky.
- **Side elements:** layered mesas, a cliff wall on one side, a wooden trestle bridge, cacti with pink flowers, rocks, and warm lantern posts.
- **Obstacles:** red heart train · mine cart full of gold ore (jump) · heart crates (jump) · wooden high barrier (slide).
- **Pickups:** **Amber crystal** (collectible) · **Flame (speed boost)** · Heart.

## 8 · Cherry Blossom Kingdom
- **Mood:** soft pastel spring morning.
- **Track:** pale pink stone path, scattered with **petals**.
- **Landmark:** two **giant red torii gates**, with a **pink-roofed palace pagoda** at the end.
- **Side elements:** cherry trees, glowing stone lanterns, red paper lanterns on poles, **koi ponds** (with koi, lily pads and flowers), azalea bushes and garden rocks.
- **Obstacles:** flowering stone wall (jump) · small torii (slide) · lantern stone block (jump).
- **Pickups:** **Sakura flower with a pearl** (collectible) · **Wings (fly)** · Heart.

## 9 · Magical Underwater Railway
- **Mood:** a glowing aquarium dream in blue and pink.
- **Track:** blue railway inside a **glass tunnel**, whose ribs carry **pink and cyan light bulbs**.
- **Side elements:** **glowing jellyfish** (pink and blue), coral gardens (pink, purple, peach, yellow), coral fans, seaweed, schools of colourful fish, rising bubbles and sea rocks.
- **Obstacles:** red heart train · **spiked sea mine** (jump) · treasure chest (jump) · heart crate (jump) · pink pipe gate (slide).
- **Pickups:** **Blue scallop shell with a pearl** (collectible) · **Bubble (shield)** · Heart.

## 10 · Heavenly Sky Temple
- **Mood:** a bright, airy, heavenly destination above the clouds.
- **Track:** warm marble bridge with **gold edge trim**, and **flower pots** on the gold caps.
- **Landmark:** **heaven gate**: white columns, a gold-trimmed arch, a dome, a pink crystal, a glowing portal with a heart, and **giant angel wings**.
- **Side elements:** angel statues with halos, marble pillars (whole and broken), floating islands with pink trees and flowers, flower gardens, clouds above and below, and butterflies.
- **Obstacles:** fallen marble column (jump) · marble arch (slide) · pink crystal rock (jump).
- **Pickups:** **Angel wing with a blue gem** (collectible) · **Shield** · Heart.

---

## How to plug these maps into your existing game

### 1. Nothing about movement changes
All maps share the lane positions, running height range, obstacle heights and segment length listed above. Your character controller, lane switching, jump and slide stay exactly as they are. The only per-map value is the **surface height** (0.32–0.56 m): read it from your map config, or snap the runner to the segment's top.

### 2. One prefab per element
Every element exists as `mapN/glb/<name>.glb` (with `fbx/` for Unity). Make one prefab per file, and tag it with the `kind` from `mapN/manifest.json`:

| kind | Prefab setup |
|---|---|
| `segment` | Ground tile. Add a box collider for the floor only. |
| `obstacle_low` | Box collider from the ground to the top. Death on hit unless the player is airborne above it. |
| `obstacle_high` | Box collider for the **bar only**, from 1.45 m up. Sliding (hitbox 0.8 m) passes underneath. |
| `obstacle_train` | Front face is deadly. The roof is walkable (a trigger at roof height sets the ground). |
| `ramp` | Sloped walkable collider that leads onto the train roof. |
| `coin` | Trigger and spin. |
| `powerup` | Trigger, plus the effect named in the asset (magnet, shield, bubble, heart, wings, bolt, flame, snowflake, shell). |
| `prop`, `backdrop`, `landmark` | No collider (purely visual). Keep them outside x = ±4.2 m. |

### 3. Endless generation
Keep your current chunk generator and just give it a **map theme object**:

```
theme = {
  segment:   "en_path_segment",              // tiled every 10 m
  lows:      ["en_obstacle_spiked_block", "en_obstacle_fallen_log"],
  highs:     ["en_obstacle_vine_beam"],
  trains:    [], ramps: [],                  // rail maps only
  coin:      "en_coin",
  powerups:  ["en_powerup_magnet", "en_powerup_heart"],
  repeat:    [{asset:"en_heart_lantern", x:-4.65, z:2.05, every:10}],
  scatter:   [{assets:[...trees], x:[7.5,16], density:...}],
  sky:       {top:"#6fb8ff", horizon:"#ffe3f0", fog:[60,240]}
}
```

The spawner places the segment, then a pattern row: one low, one high or a train in up to two lanes, always leaving **one free lane** with coins. It then scatters side props outside the corridor. `sample_mapN/level.json` is a ready-made 300 m example of exactly this, with every placement listed. The `build_samples.py` patterns (`low`, `low_high`, `double`, `train`, `train_pair`) are the same ones you can port.

### 4. Lighting per map
Each map has one sun (colour, angle and strength) and a sky gradient, both listed in `maps_romantic.py` → `world`. Night maps (4 and 5) also rely on emissive materials, so turn on **bloom** in your engine. Use **fog** with the horizon colour to get the atmospheric depth seen in the reference.

### 5. Performance
- **Shared meshes:** props are shared meshes, so instance them rather than duplicating them.
- **Textures:** each asset has one albedo and one normal map (256–1024 px). Compress them to ASTC/ETC2 on mobile.
- **Recycling:** pool segments and obstacles as they leave the camera, and keep about 120 m of track alive.

### 6. Rebuilding or tweaking
```
blender -b --factory-startup --python blender_scripts/build_maps.py      -- all set=romantic
blender -b --factory-startup --python blender_scripts/build_samples.py   -- all set=romantic
blender -b --factory-startup --python blender_scripts/render_elements.py -- all set=romantic
python blender_scripts/compose_sheets.py
```
Colours, layouts and per-map elements are in `blender_scripts/maps_romantic.py`. The shared romantic models are in `romantic_lib.py`.
