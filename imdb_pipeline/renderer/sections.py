"""
Slide section renderers.

Each public function renders one section of the video and writes JPEG
frames into *frames_dir*, starting at *start_idx*.  It returns the
next available frame index so callers can chain sections without
needing to track the count themselves.

Section signature
-----------------
    def section_*(movie, frames_dir, start_idx, **kwargs) -> int
"""

import logging
from pathlib import Path

from PIL import Image, ImageDraw

from ..config import COLORS as C, FPS, FRAME_FORMAT, FRAME_QUALITY
from ..models import MovieData
from ..config import VIDEO_WIDTH as W, VIDEO_HEIGHT as H
from .primitives import (
    draw_pill, draw_star_rating, ease_out, font, gradient_bg,
    apply_post, wrap_text,
)

log = logging.getLogger(__name__)


# ── Frame I/O helper ───────────────────────────────────────────────────────────

def _save(img: Image.Image, frames_dir: Path, idx: int) -> None:
    apply_post(img).save(
        frames_dir / f"frame_{idx:05d}.jpg",
        format=FRAME_FORMAT,
        quality=FRAME_QUALITY,
    )


# ── Section renderers ──────────────────────────────────────────────────────────

def section_title(movie: MovieData, frames_dir: Path, start_idx: int) -> int:
    """Animated title card — 4 s."""
    n = 4 * FPS
    for i in range(n):
        t = i / n
        img  = gradient_bg(C["bg_dark"], (12, 10, 28))
        draw = ImageDraw.Draw(img)

        # Expanding gold rule
        bar_w = int(W * 0.65 * ease_out(t * 3))
        bx    = (W - bar_w) // 2
        draw.line([(bx, 185), (bx + bar_w, 185)], fill=C["gold"], width=2)

        # Eyebrow label
        ef   = font("light", 16)
        etxt = "✦   MOVIE SPOTLIGHT   ✦"
        draw.text(((W - ef.getbbox(etxt)[2]) // 2, 158), etxt, font=ef, fill=C["gold_dim"])

        # Main title — slides in from below
        raw  = movie.title.upper()
        tsz  = 68
        tf   = font("bold", tsz)
        if tf.getbbox(raw)[2] > W - 80: tsz = 50; tf = font("bold", tsz)
        if tf.getbbox(raw)[2] > W - 80: tsz = 38; tf = font("bold", tsz)
        tw   = tf.getbbox(raw)[2]
        ty   = 215 + int(50 * (1 - ease_out(min(1.0, t * 2.5))))
        draw.text(((W - tw) // 2 + 2, ty + 2), raw, font=tf, fill=(0, 0, 0))  # shadow
        draw.text(((W - tw) // 2,     ty),     raw, font=tf, fill=C["white"])

        if t > 0.25:
            yf  = font("regular", 26)
            ys  = f"— {movie.year} —"
            yw  = yf.getbbox(ys)[2]
            yy  = 295 + int(20 * (1 - ease_out(min(1.0, (t - 0.25) * 3))))
            draw.text(((W - yw) // 2, yy), ys, font=yf, fill=C["gray"])

        if movie.rating != "N/A" and t > 0.4:
            bf  = font("bold", 32)
            bt  = f"★  {movie.rating}"
            bw  = bf.getbbox(bt)[2] + 44
            bx2 = (W - bw) // 2
            by2 = 340 + int(20 * (1 - ease_out(min(1.0, (t - 0.4) * 3))))
            draw.rounded_rectangle([bx2, by2, bx2 + bw, by2 + 52], radius=8, fill=C["gold"])
            draw.text((bx2 + 22, by2 + 8), bt, font=bf, fill=C["bg_dark"])

        if movie.genre and t > 0.55:
            gf      = font("medium", 15)
            total_w = sum(gf.getbbox(g)[2] + 38 for g in movie.genre[:4]) + 10 * (len(movie.genre[:4]) - 1)
            gx      = (W - total_w) // 2
            gy      = 415 + int(20 * (1 - ease_out(min(1.0, (t - 0.55) * 3))))
            for g in movie.genre[:4]:
                gx = draw_pill(draw, g, gx, gy, gf, bg=(25, 25, 60)) + 12

        if movie.director and t > 0.65:
            df   = font("light", 19)
            dtxt = f"Directed by  {movie.director}"
            dw   = df.getbbox(dtxt)[2]
            dy   = 485 + int(15 * (1 - ease_out(min(1.0, (t - 0.65) * 3))))
            draw.text(((W - dw) // 2, dy), dtxt, font=df, fill=C["light_gray"])

        if movie.tagline and t > 0.75:
            tlf   = font("light", 17)
            tltxt = f'"{movie.tagline}"'
            tlw   = tlf.getbbox(tltxt)[2]
            if tlw < W - 100:
                tly = 530 + int(15 * (1 - ease_out(min(1.0, (t - 0.75) * 3))))
                draw.text(((W - tlw) // 2, tly), tltxt, font=tlf, fill=C["gray"])

        draw.line([(bx, 598), (bx + bar_w, 598)], fill=C["gold_dim"], width=1)
        _save(img, frames_dir, start_idx + i)

    return start_idx + n


def section_stats(movie: MovieData, frames_dir: Path, start_idx: int) -> int:
    """Film details & stats grid — 5 s."""
    n = 5 * FPS
    for i in range(n):
        t    = i / n
        img  = gradient_bg((10, 10, 26), (18, 12, 38))
        draw = ImageDraw.Draw(img)

        bar_h = int(H * 0.72 * ease_out(min(1.0, t * 4)))
        draw.rectangle([55, (H - bar_h) // 2, 60, (H + bar_h) // 2], fill=C["gold"])

        draw.text((80, 55), "FILM DETAILS", font=font("bold", 13), fill=C["gold"])
        draw.text((80, 82), movie.title, font=font("bold", 38), fill=C["white"])
        draw.line([(80, 132), (W - 80, 132)], fill=(35, 35, 70), width=1)

        stats = [(lbl, val) for lbl, val in [
            ("⏱  Runtime",    movie.duration),
            ("🎬  Rated",      movie.pg_rating),
            ("🎥  Director",   movie.director),
            ("👥  IMDb Votes", movie.votes),
            ("🏆  Awards",     movie.awards),
            ("📅  Year",       movie.year),
        ] if val]

        col_w = (W - 190) // 2
        lf    = font("light",  17)
        vf    = font("medium", 21)
        for j, (lbl, val) in enumerate(stats[:6]):
            col, row = j % 2, j // 2
            sx  = 80 + col * col_w
            sy  = 158 + row * 88
            st  = ease_out(min(1.0, t * 4 - j * 0.12))
            ox  = int(25 * (1 - st))
            draw.text((sx + ox, sy),      lbl,       font=lf, fill=C["gray"])
            draw.text((sx + ox, sy + 24), val[:38],  font=vf, fill=C["white"])
            vw = vf.getbbox(val[:38])[2]
            draw.line([(sx + ox, sy + 52), (sx + ox + vw, sy + 52)], fill=C["gold_dim"], width=1)

        if movie.rating != "N/A" and t > 0.15:
            sf  = font("bold", 86)
            sx2 = W - 245
            sy2 = 148
            sw  = sf.getbbox(movie.rating)[2]
            draw.text((sx2 + (180 - sw) // 2, sy2), movie.rating, font=sf, fill=C["gold"])
            draw.text((sx2 + 55, sy2 + 92),  "/ 10",        font=font("light", 24), fill=C["gray"])
            draw.text((sx2 + 28, sy2 + 124), "IMDb Rating", font=font("light", 15), fill=C["gray"])
            draw_star_rating(draw, movie.rating, sx2 + 15, sy2 + 150, size=20)

        if movie.genre and t > 0.35:
            gf = font("medium", 14)
            gx = 80
            for g in movie.genre[:5]:
                gx = draw_pill(draw, g, gx, H - 75, gf, bg=(22, 22, 55), fg=C["light_gray"]) + 10

        _save(img, frames_dir, start_idx + i)

    return start_idx + n


def section_cast(movie: MovieData, frames_dir: Path, start_idx: int) -> int:
    """Cast showcase grid — 5 s."""
    if not movie.cast:
        log.warning("No cast data; skipping cast section")
        return start_idx

    n    = 5 * FPS
    cast = movie.cast[:6]

    for i in range(n):
        t    = i / n
        img  = gradient_bg((6, 6, 22), (14, 10, 32))
        draw = ImageDraw.Draw(img)

        draw.text((80, 52), "FEATURING", font=font("bold", 13), fill=C["gold"])
        draw.text((80, 78), "THE CAST",  font=font("bold", 50), fill=C["white"])
        draw.line([(80, 145), (W - 80, 145)], fill=(30, 30, 65), width=1)

        card_w = (W - 160 - (len(cast) - 1) * 16) // len(cast)
        card_h = 285

        for j, name in enumerate(cast):
            cx   = 80 + j * (card_w + 16)
            cy   = 168
            ct   = ease_out(min(1.0, t * 3.5 - j * 0.18))
            oy   = int(45 * (1 - ct))

            draw.rounded_rectangle(
                [cx, cy + oy, cx + card_w, cy + card_h + oy],
                radius=10, fill=(18, 18, 46),
            )

            av_r  = min(42, card_w // 2 - 8)
            av_cx = cx + card_w // 2
            av_cy = cy + av_r + 18 + oy
            draw.ellipse(
                [av_cx - av_r, av_cy - av_r, av_cx + av_r, av_cy + av_r],
                fill=C["bg_dark"], outline=C["gold"], width=2,
            )

            initials = "".join(p[0].upper() for p in name.split()[:2])
            if_sz    = max(18, min(26, av_r - 4))
            iff      = font("bold", if_sz)
            iw       = iff.getbbox(initials)[2]
            draw.text((av_cx - iw // 2, av_cy - if_sz // 2), initials, font=iff, fill=C["gold"])

            nf     = font("medium", max(11, min(14, card_w // 7)))
            parts  = name.split()
            lines2 = [parts[0]] + ([" ".join(parts[1:])] if len(parts) > 1 else [])
            for li, ln in enumerate(lines2):
                lw = nf.getbbox(ln)[2]
                draw.text((cx + (card_w - lw) // 2, av_cy + av_r + 10 + li * 20 + oy),
                          ln, font=nf, fill=C["light_gray"])

            af = font("light", 11)
            aw = af.getbbox("Actor")[2]
            draw.text((cx + (card_w - aw) // 2, av_cy + av_r + 55 + oy),
                      "Actor", font=af, fill=C["gray"])

        if t > 0.5:
            rf   = font("light", 15)
            rtxt = f"in  {movie.title}"
            rw   = rf.getbbox(rtxt)[2]
            draw.text(((W - rw) // 2, H - 52), rtxt, font=rf, fill=C["gray"])

        _save(img, frames_dir, start_idx + i)

    return start_idx + n


def section_plot(
    movie: MovieData,
    frames_dir: Path,
    start_idx: int,
    n_frames: int,
) -> int:
    """Narrated synopsis — variable length tied to audio duration."""
    plot = movie.plot or "An unforgettable cinematic experience."

    for i in range(n_frames):
        t    = i / n_frames
        img  = gradient_bg((4, 10, 24), (10, 6, 28))
        draw = ImageDraw.Draw(img)

        draw.text((42, 5), "\u201c", font=font("bold", 130), fill=(22, 22, 55))
        draw.text((105, 62), "SYNOPSIS", font=font("bold", 13), fill=C["gold"])
        draw.line([(105, 88), (W - 105, 88)], fill=(28, 28, 58), width=1)

        pf    = font("regular", 23)
        lines = wrap_text(plot, pf, W - 210)[:9]
        lh    = 38
        sy    = max(110, (H - len(lines) * lh) // 2)

        for li, line in enumerate(lines):
            lt = ease_out(min(1.0, t * (len(lines) + 1) - li * 0.12))
            if lt <= 0:
                continue
            ox = int(18 * (1 - lt))
            draw.text((105 + ox + 2, sy + li * lh + 2), line, font=pf, fill=(0, 0, 0))
            draw.text((105 + ox,     sy + li * lh),     line, font=pf, fill=C["white"])

        # Progress bar
        bx1, by1, bx2, by2 = 80, H - 36, W - 80, H - 24
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=5, fill=(22, 22, 50))
        px2 = bx1 + int((bx2 - bx1) * t)
        if px2 > bx1:
            draw.rounded_rectangle([bx1, by1, px2, by2], radius=5, fill=C["gold"])

        draw.text((80, H - 58), movie.title, font=font("light", 15), fill=C["gray"])

        _save(img, frames_dir, start_idx + i)

    return start_idx + n_frames


def section_highlights(movie: MovieData, frames_dir: Path, start_idx: int) -> int:
    """'Why Watch?' bullet reveals — 30 s."""
    trivia = (movie.trivia or [
        f"IMDb Rating: {movie.rating}/10",
        f"Directed by {movie.director}" if movie.director else "A must-watch classic",
        f"Starring {', '.join(movie.cast[:2])}" if movie.cast else "An unforgettable cast",
        f"Runtime: {movie.duration}" if movie.duration else "A perfectly paced film",
        f"Awards: {movie.awards}" if movie.awards else "Critically acclaimed worldwide",
        "An experience that will stay with you long after the credits roll",
    ])[:6]

    n = 30 * FPS
    for i in range(n):
        t    = i / n
        img  = gradient_bg((7, 5, 20), (15, 10, 35))
        draw = ImageDraw.Draw(img)

        draw.text((80, 48), "WHY WATCH?", font=font("bold", 13), fill=C["gold"])
        draw.text((80, 74), "Reasons to See This Film", font=font("bold", 40), fill=C["white"])
        draw.line([(80, 130), (W - 80, 130)], fill=(30, 30, 62), width=1)

        sf      = font("light", 17)
        n_vis   = int(t * (len(trivia) + 1))
        for j, tri in enumerate(trivia):
            if j >= n_vis:
                break
            jt = ease_out(min(1.0, t * (len(trivia) + 1) - j))
            oy = int(20 * (1 - jt))
            jy = 150 + j * 78 + oy
            draw.text((80, jy + 3), "◆", font=font("bold", 14), fill=C["gold"])
            for li, ln in enumerate(wrap_text(tri, sf, W - 180)[:2]):
                draw.text((105, jy + li * 22), ln, font=sf, fill=C["light_gray"])

        wf  = font("light", 15)
        ww  = wf.getbbox(movie.title)[2]
        draw.text((W - ww - 60, H - 45), movie.title, font=wf, fill=C["gray"])

        if movie.rating != "N/A":
            rbf = font("bold", 48)
            rbw = rbf.getbbox(movie.rating)[2]
            draw.text((W - rbw - 65, 80), movie.rating, font=rbf, fill=C["gold"])
            draw.text((W - 65, 90), "/10", font=font("light", 18), fill=C["gray"])

        _save(img, frames_dir, start_idx + i)

    return start_idx + n


def section_quote(movie: MovieData, frames_dir: Path, start_idx: int) -> int:
    """Full-bleed tagline / legacy quote card — 10 s."""
    n     = 10 * FPS
    quote = movie.tagline or (movie.plot[:120] if movie.plot else "A timeless film.")

    for i in range(n):
        t    = i / n
        img  = gradient_bg(C["deep_blue"], (8, 8, 20))
        draw = ImageDraw.Draw(img)

        draw.text((55, 10), "\u201c", font=font("bold", 110), fill=(18, 18, 42))

        qf     = font("regular", 30)
        lines  = wrap_text(quote, qf, W - 220)[:4]
        lh     = 46
        tot_h  = len(lines) * lh
        qy     = (H - tot_h) // 2 - 20

        for li, ln in enumerate(lines):
            lw = qf.getbbox(ln)[2]
            draw.text(((W - lw) // 2 + 2, qy + li * lh + 2), ln, font=qf, fill=(0, 0, 0))
            draw.text(((W - lw) // 2,     qy + li * lh),     ln, font=qf, fill=C["white"])

        draw.text((60, qy + tot_h + 20), "\u201d", font=font("bold", 110), fill=(18, 18, 42))

        if t > 0.4:
            af   = font("light", 20)
            atxt = f"— {movie.title}"
            aw   = af.getbbox(atxt)[2]
            draw.text(((W - aw) // 2, qy + tot_h + 55), atxt, font=af, fill=C["gold"])

        if movie.awards and t > 0.55:
            awf  = font("medium", 17)
            awtxt = f"🏆  {movie.awards}"
            aww   = awf.getbbox(awtxt)[2]
            draw.rounded_rectangle(
                [(W - aww - 32) // 2, H - 80, (W + aww + 32) // 2, H - 46],
                radius=8, fill=(22, 22, 55),
            )
            draw.text(((W - aww) // 2, H - 73), awtxt, font=awf, fill=C["light_gray"])

        _save(img, frames_dir, start_idx + i)

    return start_idx + n


def section_outro(movie: MovieData, frames_dir: Path, start_idx: int) -> int:
    """Fade-in / hold / fade-out closing card — 6 s."""
    n = 6 * FPS
    for i in range(n):
        t    = i / n
        img  = gradient_bg(C["bg_dark"], C["bg_mid"])
        draw = ImageDraw.Draw(img)

        alpha = (ease_out(t / 0.3)          if t < 0.3
                 else 1.0                    if t < 0.65
                 else 1 - ease_out((t - 0.65) / 0.35))

        rows = [
            (movie.title.upper(), font("bold",    46), C["white"]),
            (f"({movie.year})",   font("light",   27), C["gray"]),
            ("",                  None,               None),
            (f"★  {movie.rating} / 10  ·  " + "  ·  ".join(movie.genre[:3]),
             font("regular", 20), C["gold"]),
        ]
        cy = (H - 200) // 2
        for txt, f2, color in rows:
            if f2 is None:
                cy += 22
                continue
            tw = f2.getbbox(txt)[2]
            draw.text(((W - tw) // 2, cy), txt, font=f2, fill=color)
            cy += 50

        af   = font("light", 15)
        atxt = "Data sourced from IMDb.com  ·  Pipeline by imdb_pipeline"
        aw   = af.getbbox(atxt)[2]
        draw.text(((W - aw) // 2, H - 52), atxt, font=af, fill=C["gray"])

        if alpha < 1.0:
            base = Image.new("RGB", (W, H), C["bg_dark"])
            img  = Image.blend(base, img, alpha=alpha)

        _save(img, frames_dir, start_idx + i)

    return start_idx + n
