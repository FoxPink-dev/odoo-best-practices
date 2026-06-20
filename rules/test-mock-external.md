---
priority: MUST
tags: [testing, mocking, external-apis]
odoo_versions: [14.0, 15.0, 16.0, 17.0, 18.0, 19.0, master]
triggers:
  - task: "mocking external services in tests"
    includes: ["tests/test_*.py"]
---
# Test Mock External

## Description

Always mock external API calls (payment gateways, shipping carriers, SMS, email, third-party REST/SOAP services) in unit tests. Use `unittest.mock` (`patch`, `MagicMock`) to replace network calls. Never let tests hit real external endpoints: this creates flaky tests, dependency on network/external services, and may incur costs or hit rate limits.

## Correct

```python
from unittest.mock import patch
from odoo.tests import TransactionCase

class TestShipping(TransactionCase):
    @patch('odoo.addons.delivery.models.delivery_carrier.DeliveryCarrier._send_rate_request')
    def test_rate_parsing(self, mock_send):
        mock_send.return_value = {'total': 12.50, 'currency': 'USD'}
        carrier = self.env['delivery.carrier'].search([], limit=1)
        rate = carrier.rate_shipment(self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Test'}).id,
        }))
        self.assertEqual(rate['price'], 12.50)
```

## Incorrect

```python
class BadTestShipping(TransactionCase):
    def test_rate_live(self):
        # Hits real API: flaky, slow, and may cost money
        carrier = self.env['delivery.carrier'].search([], limit=1)
        rate = carrier.rate_shipment(self.env['sale.order'].browse(1))
```

## Rationale

External API calls make tests slow, non-deterministic, and dependent on network/external service availability. Mocking isolates the code under test and guarantees fast, repeatable results. Always mock at the lowest integration point (the actual HTTP call or external library call), not at high-level business logic.

## References

- Python `unittest.mock` documentation
- Odoo coding guidelines: tests should be fast and isolated
