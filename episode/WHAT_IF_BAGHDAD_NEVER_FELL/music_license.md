# Music & SFX licence entry: WHAT_IF_BAGHDAD_NEVER_FELL

This follows the format of the 01-BRAND/MUSIC_LICENSE_REGISTER.md file on Drive: title, creator, URL, license, date, SHA-256 and processing.

| Field | Music | SFX |
|---|---|---|
| Title | «Hijaz Ruwaq — What If Baghdad» (bed + sonic logo) | Ruwaq SFX set (impact_soft, whoosh_low, paper, tick, sonic_logo) |
| Creator | Riwaq production, procedural synthesis in code | Riwaq production, procedural synthesis in code |
| URL / source | `episode/WHAT_IF_BAGHDAD_NEVER_FELL/tools/build_music_sfx.py` (in the repo) | same file |
| License | **ORIGINAL**: owned by the channel. No samples and no third-party licence. | **ORIGINAL** |
| Date | 2026-11-25 | 2026-11-25 |
| SHA-256 | see `sha256` in `exports/.../publish/manifest.json` | same |
| Processing | Hijaz on D. Drone, pads, Karplus-Strong oud plucks and a frame drum (scenes 09–13), with reverb. Ducked −12 dB under the VO using word timings. Final mix at −14 LUFS / −1 dBTP. | 21 events in the long video, 5 in the Short. Placed from timeline.json. |

## Owner's request: YouTube Audio Library (**BLOCKED**)

- **Why it is blocked:** the YouTube Audio Library sits inside YouTube Studio and needs the channel's Google sign-in. The sandbox has no session for it, and its hosts are outside the allowed network.
- **Do not fabricate:** no track was claimed to come from the library.
- **Alternative used:** original music. The register says to use original audio "if the license is unprovable", so this follows the register's own rule.
- **To switch to a Library track (about 5 minutes):**
  1. Download a track from YouTube Studio → Audio Library. "Cinematic / Dramatic" works well, with "Attribution not required".
  2. Put it in `exports/WHAT_IF_BAGHDAD_NEVER_FELL/audio/yt_library_track.wav`.
  3. Re-run the mix step in `build_music_sfx.py` with the music source replaced. The VO, SFX and ducking stay as they are.
  4. Re-mux with `tools/mux_only.sh`, which replaces the audio only, so no video re-render is needed.
  5. Log the title, artist and licence here and in the main register.
