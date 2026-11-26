"""Server Bagian A: aksi game + frame UI Pycairo melalui WebSocket."""
from __future__ import annotations

import io
import json
import sys
from math import isfinite
from pathlib import Path

import cairo
from flask import Flask, jsonify, send_from_directory
from flask_sock import Sock

from docs import colors
from game.data_loader import load_config, load_records
from game.formulas import Config
from game.logic import Game
from game.ui import draw_ui


def render_frame(game: Game, selected_plot: int | None, show_data: bool,
                 tooltip: str = "") -> bytes:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 960, 540)
    ctx = cairo.Context(surface)
    colors.set_source(ctx, colors.SKY_BOTTOM)
    ctx.paint()
    ctx.scale(3, 3)
    draw_ui(ctx, game, selected_plot, show_data, tooltip)
    output = io.BytesIO()
    surface.write_to_png(output)
    return output.getvalue()


def handle_click(game: Game, x: float, y: float,
                 selected_plot: int | None, show_data: bool) -> tuple[int | None, bool]:
    if (any(isinstance(v, bool) or not isinstance(v, (int, float))
            or not isfinite(v) for v in (x, y))
            or not 0 <= x < 320 or not 0 <= y < 180):
        raise ValueError("koordinat klik harus dalam kanvas 320x180")
    if 277 <= x and y < 16:
        return selected_plot, not show_data
    if 128 <= y < 152 and 8 <= x < 158:
        index = int((x - 8) // 30)
        return index, show_data
    if 162 <= y < 175 and not game.state.finished:
        if x >= 278:
            game.advance_day()
        elif selected_plot is not None and x < 114:
            plot = game.state.plots[selected_plot]
            action = int((x - 5) // 37)
            if x < 5 or (x - 5) % 37 >= 34:
                return selected_plot, show_data
            if not plot.variety and action in (0, 1):
                game.plant(selected_plot, ("Robusta", "Arabika")[action])
            elif plot.variety and action == 0:
                game.care(selected_plot, "water")
            elif plot.variety and action == 1:
                game.care(selected_plot, "fertilize")
            elif plot.variety and action == 2:
                game.harvest(selected_plot)
        elif game.state.batches and 124 <= x < 238:
            batch = game.state.batches[0]
            if (x - 124) % 38 >= 35:
                return selected_plot, show_data
            if batch.stage == "roasted":
                if x < 159:
                    game.sell(batch)
            elif batch.stage == "dried":
                choice = int((x - 124) // 38)
                if choice < 3:
                    game.process(batch, "roasted", ("light", "medium", "dark")[choice])
            elif x < 159:
                next_step = {"harvested": "sorted", "sorted": "pulped",
                             "pulped": "drying", "drying": "dried"}[batch.stage]
                game.process(batch, next_step)
    return selected_plot, show_data


def tooltip_at(game: Game, x: float, y: float) -> str:
    if (any(isinstance(v, bool) or not isinstance(v, (int, float))
            or not isfinite(v) for v in (x, y))
            or not 0 <= x < 320 or not 0 <= y < 180):
        raise ValueError("koordinat harus dalam kanvas 320x180")
    if 277 <= x and y < 16:
        return "Klik untuk lihat data dan sumber"
    if 128 <= y < 152 and 8 <= x < 158:
        index = int((x - 8) // 30)
        plot = game.state.plots[index]
        return f"Petak {index + 1}: {plot.variety or 'kosong'}, tahap {plot.stage}"
    if 162 <= y < 175 and x >= 278:
        return "Majukan satu hari permainan"
    return ""


def create_app(records, config: Config) -> Flask:
    app = Flask(__name__, static_folder="static")
    sock = Sock(app)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/options")
    def options():
        return jsonify([{"region_id": region, "month": month}
                        for region, month in sorted(records)])

    @sock.route("/ws")
    def websocket(ws):
        game = None
        selected_plot = None
        show_data = False
        tooltip = ""
        while message := ws.receive():
            try:
                command = json.loads(message)
                if not isinstance(command, dict):
                    raise ValueError("perintah harus objek JSON")
                if command.get("type") == "start":
                    game = Game(records, config, command["region_id"], command["month"])
                    selected_plot, show_data = None, False
                    tooltip = ""
                elif game is None:
                    raise ValueError("mulai permainan dulu")
                elif command.get("type") == "click":
                    selected_plot, show_data = handle_click(
                        game, command["x"], command["y"], selected_plot, show_data)
                    tooltip = ""
                elif command.get("type") == "hover":
                    tooltip = tooltip_at(game, command["x"], command["y"])
                else:
                    raise ValueError("perintah tidak dikenal")
                ws.send(json.dumps({"type": "state", "balance": game.state.balance,
                                    "day": game.state.day, "finished": game.state.finished}))
                ws.send(render_frame(game, selected_plot, show_data, tooltip))
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                ws.send(json.dumps({"type": "error", "message": str(exc)}))
    return app


if __name__ == "__main__":
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--dummy"):
        raise SystemExit("Penggunaan: python app.py [--dummy]")
    mode = "dummy" if "--dummy" in sys.argv else "processed"
    root = Path(__file__).resolve().parent / "data" / mode
    app = create_app(load_records(root / "regions.json"), load_config(root / "config.json"))
    app.run(debug=False)
