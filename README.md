# Artnet Controller

**Professional DMX lighting control for [Ctrlable Pro](https://ctrlable.com).**
Drive **Art-Net**, **sACN (E1.31)** and **KiNET** fixtures directly from Ctrlable
Pro — configured entirely in the UI with a visual **Art-Net Patch** panel for
laying out universes and fixtures. No YAML required.

> This is the **source** repository (private). The installable build lives at
> [`Ctrlable/artnet-controller`](https://github.com/Ctrlable/artnet-controller).
> Published builds ship as obfuscated panel JS and compiled native (`abi3`)
> Python — the source here is the plain, readable original.

---

## Highlights

- **UI-first** — discover or add nodes, patch fixtures, and assign entities
  without touching a config file.
- **Visual patch panel** — drag fixtures onto a 512-channel grid per universe;
  overlaps and channel-512 overflow are flagged live.
- **Every fixture is an entity** — each Art-Net node becomes a device; every
  patched fixture becomes a `light` entity grouped under it.
- **Rich color handling** — independent RGB + cool/warm white + master
  brightness, 16-bit DMX output, and smooth transitions at the node's max FPS.
- **Output correction curves** — per-universe and per-fixture `linear`,
  `quadratic`, `cubic`, `quadruple` response for clean LED fades.
- **Reusable fixture profiles** — save a fixture's channel layout as a named
  profile and reapply it across patches.
- **Broad protocol + hardware support** — any Art-Net, sACN (E1.31) or KiNET
  interface.

---

## Requirements

- Ctrlable Pro 2024.12 or newer.
- A DMX-over-IP interface (Art-Net / sACN / KiNET) reachable on the local
  network.
- An **Artnet Controller license** (issued from the Ctrlable portal). The
  integration runs a one-time license gate; see [Licensing](#licensing).

---

## Installation (HACS)

1. In **HACS → ⋮ → Custom repositories**, add
   `https://github.com/Ctrlable/artnet-controller` with category
   **Integration**.
2. Search for **Artnet Controller**, **Download**, and **restart Ctrlable Pro**.

> Updates are delivered through HACS. The native modules load from a per-build
> cache, so in-place HACS updates apply cleanly without disrupting the running
> process.

---

## Licensing

Artnet Controller is a licensed Ctrlable product. On first setup, open the
**Art-Net Patch** panel (or the integration's options) and paste the license key
issued for your instance from the Ctrlable portal. The license is verified
offline against an embedded public key and re-checked periodically; one license
covers the whole installation (all nodes on the instance).

---

## Setup

1. **Settings → Devices & Services → Add Integration → "Artnet Controller"**.
2. Choose **Scan** (ArtPoll discovery) or **Manual** (enter the node's IP). An
   entry and device are created.
3. Open the **Art-Net Patch** panel from the sidebar:
   - Pick the node (or **+ Add** to scan/create one).
   - Set node options (port, protocol, max FPS, refresh).
   - Add universes, then place fixtures on the 512-channel grid; overlaps and
     overflow past channel 512 are flagged.
   - **Save** — the entry reloads and the `light` entities appear under the
     node's device.
4. Fixtures can also be added/removed from the entry's **Configure** (options)
   dialog without the panel.

Removing the integration entry removes its entities and frees the node's UDP
socket.

---

## Fixture types

`dimmer`, `binary`, `fixed`, `color_temp`, `rgb`, `rgbw`, `rgbww`, `xy`.

### channel_setup

A string customizing the channel layout of a fixture (entered in the panel's
fixture inspector, or as `channel_setup` in the options dialog). For example
`Wrgb` = white (unscaled), red, green, blue. Numeric entries set a static value.

#### Definition

- `d` = dimmer (brightness 0 to 255)
- `c` = cool white value, scaled for brightness
- `C` = cool white value, unscaled
- `h` = warm white value, scaled for brightness
- `H` = warm white value, unscaled
- `t` = temperature (0 = warm, 255 = cold)
- `T` = temperature (255 = warm, 0 = cold)
- `r` = red, scaled for brightness
- `R` = red, unscaled
- `g` = green, scaled for brightness
- `G` = green unscaled
- `b` = blue, scaled for brightness
- `B` = blue, unscaled
- `w` = white, scaled for brightness
- `W` = white, unscaled
- `u` = hue
- `U` = saturation
- `x` = X value in XY color mode
- `y` = Y value in XY color mode
- [`0`, `255`] = static value between the range [0, 255]

#### Compatibility

| Type       |     |     |     |     |     |     |     |     |     |     |     |     |     |       |       |     |     | Static    |     |     | Default |
|------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------|-------|-----|-----|-----------|-----|-----|---------|
| fixed      |     |     |     |     |     |     |     |     |     |     |     |     |     |       |       |     |     | `[0,255]` |     |     | `0`     |
| binary     |     |     |     |     |     |     |     |     |     |     |     |     |     |       |       |     |     | `[0,255]` |     |     | `0`     |
| dimmer     |     |     |     |     |     |     |     |     |     |     |     |     |     |       |       |     |     | `[0,255]` |     |     | `0`     |
| color_temp | `d` | `c` | `C` | `h` | `H` | `t` | `T` |     |     |     |     |     |     |       |       |     |     | `[0,255]` |     |     | `ch`    |
| rgb        | `d` |     |     |     |     |     |     | `r` | `R` | `g` | `G` | `b` | `B` | `w`\* | `W`\* | `u` | `U` | `[0,255]` |     |     | `rgb`   |
| rgbw       | `d` |     |     |     |     |     |     | `r` | `R` | `g` | `G` | `b` | `B` | `w`   | `W`   | `u` | `U` | `[0,255]` |     |     | `rgbw`  |
| rgbww      | `d` | `c` | `C` | `h` | `H` | `t` | `T` | `r` | `R` | `g` | `G` | `b` | `B` |       |       | `u` | `U` | `[0,255]` |     |     | `rgbch` |
| xy         | `d` |     |     |     |     |     |     |     |     |     |     |     |     |       |       |     |     | `[0,255]` | `x` | `y` | `dxy`   |

\* When a white channel is used on an RGB fixture, the white channel is
automatically calculated.

---

## Supported features

- **Color mode** — independent control of RGB, cool/warm white and an overall
  brightness, so color and white levels can be set independently and dimmed as a
  whole without shifting color.
- **16-bit DMX output** — 65k steps for smooth low-level fades.
- **Transitions** — fade to a color/value (runs at the node's max FPS).
- **Brightness** and **color temperature** (for tunable-white fixtures).

### Output correction

Per-universe and per-fixture output curves: `linear` (default), `quadratic`,
`cubic`, `quadruple`. Quadratic/cubic give smoother LED-strip fades.

<img src='curves.svg'>

### Recorder note

DMX setups can produce many frequently-changing entities. To avoid database
bloat, exclude them from the recorder, e.g.:

```yaml
recorder:
  exclude:
    entity_globs:
      - light.pixelstrip*
```

### Supported hardware

- Any Art-Net, KiNET or sACN (E1.31) DMX interface.
- Tested: DMX King eDMX4, ENTTEC DIN Ethergate 2 (Art-Net); esPixelStick,
  Falcon F16v2 (sACN).

---

## Troubleshooting

- **No fixtures appear after saving** — confirm the node is reachable (the panel
  shows node status) and that fixtures don't overflow past channel 512.
- **Entities show as unavailable** — the node isn't responding; check the IP,
  port and that no other controller holds the node's UDP socket.
- **License prompt won't clear** — re-paste the key from the portal and confirm
  the instance matches the one the license was issued for.

### Debug logging

```yaml
logger:
  logs:
    custom_components.artnet_controller: debug
```

---

## See also

- [Art-Net (Wikipedia)](https://en.wikipedia.org/wiki/Art-Net) · [art-net.org.uk](https://art-net.org.uk/)

## Credits & licensing

Based on [Breina/ha-artnet-led](https://github.com/Breina/ha-artnet-led) by
corb3000 and contributors, distributed under the MIT License. Ctrlable's
config-entry conversion, patch panel, and licensing layer are additive; see
[`LICENSE`](LICENSE), which retains the original copyright.

---

## Legal

**Art-Net™ Designed by and Copyright Artistic Licence Holdings Ltd.**
