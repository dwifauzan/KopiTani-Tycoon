"""Node scene graph.

CATATAN TIM: file ini hanya implementasi MINIMAL sesuai spesifikasi AGENTS.md
supaya modul Bagian C bisa dites sendiri. Jika Bagian B sudah punya
`graphics/node.py`, pakai versi Bagian B (asal punya atribut & method yang sama:
name, tx, ty, rotation, sx, sy, children, visible, clip, add, draw_self, render).
"""
from __future__ import annotations

from typing import Callable, Optional

import cairo


class Node:
    """Satu simpul scene graph dengan transformasi LOKAL."""

    def __init__(self, name: str = "node") -> None:
        self.name = name
        self.tx = 0.0
        self.ty = 0.0
        self.rotation = 0.0  # radian
        self.sx = 1.0
        self.sy = 1.0
        self.children: list[Node] = []
        self.visible = True
        self.clip: Optional[Callable[[cairo.Context], None]] = None

    def add(self, child: "Node") -> "Node":
        self.children.append(child)
        return child

    def draw_self(self, ctx: cairo.Context) -> None:
        """Override di subclass."""

    def render(self, ctx: cairo.Context) -> None:
        if not self.visible:
            return
        ctx.save()
        ctx.translate(self.tx, self.ty)
        ctx.rotate(self.rotation)
        ctx.scale(self.sx, self.sy)
        if self.clip:
            self.clip(ctx)
            ctx.clip()
        self.draw_self(ctx)
        for c in self.children:
            c.render(ctx)
        ctx.restore()
