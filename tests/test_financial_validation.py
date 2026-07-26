import pytest

from app.services.financial_validation import validate_financials, export_validation_xlsx, _num


@pytest.mark.parametrize("raw,expected", [
    (5000, 5000.0),
    (12.5, 12.5),
    ("50000", 50000.0),
    ("50,5", 50.5),            # decimale IT
    ("1.234,56 €", 1234.56),   # migliaia IT + decimale + valuta
    ("1,234.56", 1234.56),     # migliaia EN + decimale
    ("50.000", 50000.0),       # migliaia IT (3 cifre in coda -> non decimale)
    ("1.000.000", 1000000.0),
    ("50k", 50000.0),
    ("1,5k", 1500.0),
    ("2 mln", 2000000.0),
    ("-300,5", -300.5),
    ("n/d", None),
    ("", None),
    (True, None),
])
def test_num_parser(raw, expected):
    assert _num(raw) == expected


def _check(result, nome):
    return next(c for c in result["checks"] if c["nome"] == nome)


# Costi/margine noti: prezzo 10, costi variabili 4 -> margine 6.
# Costi fissi diretti 1200 + indiretti 300 = 1500 -> break-even 250 unità/mese.
_FINANCIAL = {
    "cost_breakdown": {
        "fixed_costs_eur_month": [{"item": "affitto", "amount": 800},
                                  {"item": "utenze", "amount": 400}],
        "indirect_costs_eur_month": [{"item": "commercialista", "amount": 200},
                                     {"item": "pulizie", "amount": 100}],
        "variable_costs_per_unit_eur": [{"item": "materie", "amount": 3},
                                        {"item": "packaging", "amount": 1}],
    },
    "pricing": {"unit_price_eur": 10, "unit_margin_eur": 6},
    "break_even": {"units_per_month": 250},
    "scenarios": [{"scenario": "base", "year1_revenue_eur": 40000}],
    "initial_capital": [{"item": "macchinari", "amount_eur": 5000}],
}
# Copertura: 1500 / 5000 = 30% -> dentro banda 25-30%, agente dice Sì -> coerente.
_FUNDING = {"available_capital_eur": 1500, "own_capital_check": {"meets_25_30_rule": True}}
_MARKET = {"market_sizing": {"som_eur": "50000"}}


def test_break_even_recalculated_from_costs_and_margin():
    result = validate_financials(_FINANCIAL, _FUNDING, _MARKET)
    margine = _check(result, "Margine unitario")
    assert margine["valore_ricalcolato"] == pytest.approx(6.0)
    assert margine["coerente"] is True
    be = _check(result, "Break-even (unità/mese)")
    assert be["valore_ricalcolato"] == pytest.approx(250.0)  # (1200 + 300) / 6
    assert be["coerente"] is True
    assert "indiretti 300" in be["nota"]
    assert result["overall_coherent"] is True


def test_wrong_declared_margin_is_incoherent():
    bad = {**_FINANCIAL, "pricing": {"unit_price_eur": 10, "unit_margin_eur": 8}}
    result = validate_financials(bad, _FUNDING, _MARKET)
    margine = _check(result, "Margine unitario")
    assert margine["valore_dichiarato"] == pytest.approx(8.0)
    assert margine["valore_ricalcolato"] == pytest.approx(6.0)
    assert margine["coerente"] is False
    assert result["overall_coherent"] is False


def test_missing_data_is_non_verificabile_without_exceptions():
    result = validate_financials({}, {}, {})  # nessun dato, non deve sollevare
    assert result["checks"]  # tutti i check presenti
    assert all(c["coerente"] == "non_verificabile" for c in result["checks"])
    # non_verificabile non conta come incoerenza
    assert result["overall_coherent"] is True


def test_copertura_uses_declared_total_and_matches_agent():
    # Voci sommano 23.000 ma il totale dichiarato è 28.000: il fabbisogno
    # corretto è 28.000. 8.000 / 28.000 = 28,6% -> dentro banda, agente Sì.
    fin = {
        "initial_capital": [{"item": "a", "amount_eur": 15000},
                            {"item": "b", "amount_eur": 8000}],
        "initial_capital_total_eur": 28000,
    }
    funding = {"available_capital_eur": 8000,
               "own_capital_check": {"meets_25_30_rule": True}}
    result = validate_financials(fin, funding, {})
    cop = _check(result, "Copertura capitale proprio")
    assert cop["valore_ricalcolato"] == pytest.approx(28.6, abs=0.1)  # non 34,8%
    assert cop["coerente"] is True
    assert "rientra" in cop["nota"]


def test_copertura_out_of_band_but_agent_says_yes_is_incoherent():
    # 12.000 / 28.000 = 42,9% -> fuori banda, ma agente dichiara Sì -> incoerente.
    fin = {"initial_capital_total_eur": 28000}
    funding = {"available_capital_eur": 12000,
               "own_capital_check": {"meets_25_30_rule": True}}
    result = validate_financials(fin, funding, {})
    cop = _check(result, "Copertura capitale proprio")
    assert cop["valore_ricalcolato"] == pytest.approx(42.9, abs=0.1)
    assert cop["coerente"] is False
    assert "fuori" in cop["nota"]
    assert result["overall_coherent"] is False


def test_export_xlsx_writes_file(tmp_path):
    result = validate_financials(_FINANCIAL, _FUNDING, _MARKET)
    out = export_validation_xlsx(result, str(tmp_path / "val.xlsx"))
    from pathlib import Path
    assert Path(out).exists()
