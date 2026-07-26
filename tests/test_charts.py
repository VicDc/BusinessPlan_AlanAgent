from app.services import charts


def test_no_double_png_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(charts, "CHARTS_DIR", tmp_path)
    spec = {
        "chart_type": "bar",
        "title": "T",
        "labels": ["a", "b"],
        "series": {"s": [1, 2]},
        "filename": "revenue.png",  # già con estensione
    }
    path = charts._render_single(spec)
    assert path.endswith(".png")
    assert not path.endswith(".png.png")
