"""Data sintetis hanya untuk tes, bukan parameter permainan produksi."""
import json
import io

import cairo
import pytest

from app import create_app, handle_click, render_frame, tooltip_at
from game.data_loader import RegionMonth, load_config, load_records
from game.formulas import Config, climate_factor, drying_days, sale_value
from game.logic import Game
from game.ui import draw_ui


@pytest.fixture
def config():
    return Config(
        rain_range=(0, 100, 200, 400), temp_range=(10, 20, 30, 40),
        base_growth=0.5, care_bonus=0.2, dry_base_days=1,
        dry_rain_factor=1, grade_factors={"A": 1, "B": 0.7, "C": 0.4},
        roast_factors={"light": 1, "medium": 1.1, "dark": 0.9},
        water_cost=5, fertilizer_cost=10, starting_balance=100,
        star_target=120, trees_per_ha=1000, ripen_days=2,
        grade_yellow_at=0.4, grade_red_at=0.8, season_days=10,
    )


@pytest.fixture
def records():
    source = {"climate": "DUMMY", "production": "DUMMY", "price": "DUMMY"}
    return {
        ("a", 1): RegionMonth("a", 1, 150, 25, 10000, 1, 10, source),
        ("a", 2): RegionMonth("a", 2, 300, 25, 10000, 1, 10, source),
    }


def test_data_loader_validates_columns_units_sources_and_duplicates(tmp_path):
    row = dict(region_id="a", month=1, rain_mm=150, temp_c=25,
               production_kg=10000, area_ha=1, price_idr_per_kg=10,
               sources={"climate": "DUMMY", "production": "DUMMY", "price": "DUMMY"})
    path = tmp_path / "data.json"
    for changes, message in [({"area_ha": 0}, "luas"),
                             ({"month": 13}, "bulan"),
                             ({"sources": {}}, "sumber")]:
        path.write_text(json.dumps([{**row, **changes}]))
        with pytest.raises(ValueError, match=message):
            load_records(path)
    path.write_text(json.dumps([row, row]))
    with pytest.raises(ValueError, match="duplikat"):
        load_records(path)
    path.write_text(json.dumps([row]))
    assert load_records(path)[("a", 1)].yield_kg_per_ha == 10000


def test_config_requires_sources_and_all_parameters(config, tmp_path):
    path = tmp_path / "config.json"
    values = {**vars(config), "sources": {"agronomy": "DUMMY", "postharvest": "DUMMY", "economy": "DUMMY"}}
    path.write_text(json.dumps(values))
    assert load_config(path).base_growth == config.base_growth
    del values["base_growth"]
    path.write_text(json.dumps(values))
    with pytest.raises(ValueError, match="parameter hilang"):
        load_config(path)


def test_formulas_are_bounded_and_grade_affects_sale(config):
    assert [climate_factor(v, config.rain_range) for v in (-1, 50, 150, 300, 500)] == [0, 0.5, 1, 0.5, 0]
    assert drying_days(300, config) > drying_days(0, config)
    assert sale_value(10, 10, {"A": 1}, "light", config) > sale_value(10, 10, {"C": 1}, "light", config)
    with pytest.raises(ValueError):
        sale_value(-1, 10, {"A": 1}, "light", config)


def test_one_season_care_harvest_process_sell_and_stars(config, records):
    game = Game(records, config, "a", 1)
    game.plant(0, "Robusta")
    game.care(0, "water")
    with pytest.raises(ValueError, match="sudah dilakukan"):
        game.care(0, "water")
    game.advance_day()
    assert game.state.plots[0].growth == 0.6
    assert game.state.balance == 95
    game.advance_day()
    assert game.state.plots[0].stage == 4
    batch = game.harvest(0, [0, 0.5, 1])
    assert batch.grades == {"A": 1, "B": 1, "C": 1}
    with pytest.raises(ValueError, match="urutan"):
        game.process(batch, "roasted", "light")
    for step in ("sorted", "pulped", "drying"):
        game.process(batch, step)
    with pytest.raises(ValueError, match="belum selesai"):
        game.process(batch, "dried")
    for _ in range(2):
        game.advance_day()
    game.process(batch, "dried")
    game.process(batch, "roasted", "medium")
    assert game.sell(batch) > 0
    while not game.state.finished:
        game.advance_day()
    assert game.stars() == 2
    with pytest.raises(ValueError, match="berakhir"):
        game.plant(1, "Arabika")


def test_region_changes_growth_and_unknown_region_rejected(config, records):
    wet = Game(records, config, "a", 1)
    drier = Game(records, config, "a", 2)
    wet.plant(0, "Robusta")
    drier.plant(0, "Robusta")
    wet.advance_day()
    drier.advance_day()
    assert wet.state.plots[0].growth > drier.state.plots[0].growth
    with pytest.raises(ValueError, match="tidak tersedia"):
        wet.select_region("missing", 1)


def test_ui_renders_data_dummy_label_and_end_screen(config, records):
    game = Game(records, config, "a", 1)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 320, 180)
    ctx = cairo.Context(surface)
    draw_ui(ctx, game, selected_plot=0, show_data=True, tooltip="Petak kosong")
    game.state.finished = True
    draw_ui(ctx, game, show_data=True)
    output = io.BytesIO()
    surface.write_to_png(output)
    assert output.getvalue().startswith(b"\x89PNG")


def test_server_options_frame_and_canvas_actions(config, records):
    app = create_app(records, config)
    assert app.test_client().get("/").status_code == 200
    assert len(app.test_client().get("/options").json) == 2
    game = Game(records, config, "a", 1)
    selected, show_data = handle_click(game, 10, 135, None, False)
    assert selected == 0
    selected, show_data = handle_click(game, 10, 166, selected, show_data)
    assert game.state.plots[0].variety == "Robusta"
    assert selected == 0 and not show_data
    for _ in range(2):
        handle_click(game, 280, 166, selected, show_data)
    handle_click(game, 80, 166, selected, show_data)
    assert game.state.batches[0].stage == "harvested"
    for _ in range(3):
        handle_click(game, 125, 166, selected, show_data)
    with pytest.raises(ValueError, match="belum selesai"):
        handle_click(game, 125, 166, selected, show_data)
    for _ in range(2):
        handle_click(game, 280, 166, selected, show_data)
    handle_click(game, 125, 166, selected, show_data)
    handle_click(game, 163, 166, selected, show_data)
    handle_click(game, 125, 166, selected, show_data)
    assert game.state.balance > config.starting_balance
    assert not game.state.batches
    assert render_frame(game, selected, True).startswith(b"\x89PNG")
    assert "Petak 1" in tooltip_at(game, 10, 135)
