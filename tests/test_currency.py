import unittest
from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from cachetools import TTLCache

from utils import currency


class FrankfurterTests(unittest.TestCase):
    def setUp(self):
        currency.frankfurterRateCache.clear()

    @patch.object(currency.requests, "get")
    def test_conversion_and_shared_cache(self, get):
        get.return_value = Mock(json=Mock(return_value={"date": "2026-09-16", "base": "USD", "quote": "HKD", "rate": 7.8501}))
        amount, rate = currency.convert_price(Decimal("2"), "usd", "hkd")
        self.assertEqual(amount, Decimal("15.7002"))
        self.assertEqual(rate, Decimal("7.8501"))
        self.assertEqual(currency.get_fx_rate("HKD", "USD"), Decimal(1) / rate)
        get.assert_called_once_with("https://api.frankfurter.dev/v2/rate/USD/HKD", timeout=10)

    @patch.object(currency.requests, "get")
    def test_cache_expires_after_five_minutes(self, get):
        now = [0]
        cache = TTLCache(maxsize=1, ttl=300, timer=lambda: now[0])
        # The decorator holds the original cache; replace its timer for this test.
        original_timer = currency.frankfurterRateCache._TimedCache__timer
        currency.frankfurterRateCache._TimedCache__timer = cache.timer
        self.addCleanup(setattr, currency.frankfurterRateCache, "_TimedCache__timer", original_timer)
        self.addCleanup(currency.frankfurterRateCache.clear)
        get.return_value = Mock(json=Mock(return_value={"date": "2026-09-16", "base": "USD", "quote": "HKD", "rate": 7.8}))
        currency.get_fx_rate("USD", "HKD")
        now[0] = 299
        currency.get_fx_rate("USD", "HKD")
        self.assertEqual(get.call_count, 1)
        now[0] = 300
        get.return_value.json.return_value["rate"] = 7.9
        self.assertEqual(currency.get_fx_rate("USD", "HKD"), Decimal("7.9"))
        self.assertEqual(get.call_count, 2)

    @patch.object(currency.requests, "get")
    def test_failures_not_cached(self, get):
        for rate in [None, 0, -1, "NaN", "Infinity", True]:
            get.return_value = Mock(json=Mock(return_value={"date": "2026-09-16", "base": "USD", "quote": "HKD", "rate": rate}))
            self.assertEqual(currency.convert_price(Decimal(1), "USD", "HKD"), (None, None))
            self.assertEqual(len(currency.frankfurterRateCache), 0)
        get.side_effect = requests.Timeout()
        self.assertIsNone(currency.get_fx_rate("USD", "HKD"))
        get.side_effect = None
        get.return_value.json.return_value = {"date": "2026-09-16", "base": "USD", "quote": "HKD", "rate": 7.8}
        self.assertEqual(currency.get_fx_rate("USD", "HKD"), Decimal("7.8"))

    @patch.object(currency, "_get_fx_rate_cached", return_value=Decimal("7.7"))
    @patch.object(currency.requests, "get")
    def test_historical_and_other_currencies_keep_existing_path(self, get, old):
        self.assertEqual(currency.get_fx_rate("usd", "hkd", 123), Decimal("7.7"))
        old.assert_called_with("USD", "HKD", 123)
        currency.get_fx_rate("EUR", "USD")
        old.assert_called_with("EUR", "USD", None)
        get.assert_not_called()
