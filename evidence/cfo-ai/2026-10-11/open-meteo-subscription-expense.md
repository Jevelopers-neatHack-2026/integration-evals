# Open-Meteo subscription expense — 2026-10-11

The project owner reported purchasing an Open-Meteo subscription on 2026-10-11 and subsequently storing the API key locally. The key field was verified as populated without reading out or retaining the value. This is a user-reported actual subscription expense, not a hypothetical forecast or independently verified payment receipt.

| Field | Recorded status |
| --- | --- |
| Vendor | Open-Meteo |
| Purpose | TicketStub event-weather research and commercial API access |
| Expense category | Recurring data/API subscription; fixed operating overhead |
| Purchase date | Subscription service starts 2026-10-11; receipt verification pending |
| Plan / historical API entitlement | API Standard, active per owner; historical weather is not included under current published plan terms |
| Amount and currency | EUR 29.00 per month, confirmed by owner subscription details; replaces earlier ambiguous dollar notation |
| Tax and total charged | No tax; EUR 29.00 total reported by owner |
| Billing frequency / service period | Monthly; 2026-10-11 through 2026-11-11 |
| Settlement and receipt | Purchase reported by owner; independent receipt verification pending |
| Integration status | Credential staged locally; customer endpoint integration and authenticated test pending |

## CFO.ai reconciliation

Add the confirmed amount to actual operating expenses and the recurring forecast. Preserve original currency and tax treatment. Do not enter unknown as zero, assume a plan price, or infer opening cash. If billed annually, record the actual cash charge separately from monthly expense allocation. Check existing fixed-overhead/data allowances before adding the cost so the same subscription is not counted twice. Keep promotional credits separate from the underlying cost.

The existing CFO.ai plan and native workbook are dated evidence snapshots. They have not been updated by this record. API Standard, EUR 29.00/month, no tax and the October 11–November 11 service period are confirmed by the owner. Update the actual CFO.ai canvas, recalculate scenarios/runway, and retain a new dated export and verification evidence. Do not overwrite the original snapshot or claim its earlier calculations include this expense.

Related: https://github.com/Jevelopers-neatHack-2026/getticketstub.com/issues/27

No API key, invoice identifier, payment method or private billing details are included.

## Plan limitation and currency treatment

Official pricing states historical weather requires Professional or higher: https://open-meteo.com/en/pricing. TicketStub currently selects the archive API for older events. Standard subscription cannot be treated as authorizing that commercial historical path. Resolve by disabling historical enrichment with an explicit unavailable result or selecting a suitable plan; no upgrade is authorized by this record.

The existing CFO model reports USD. Preserve EUR 29.00 as the source expense; do not enter it as USD 29.00 or invent an exchange rate. Any USD allocation needs a documented FX source, date and rate, or an actual settled USD amount from billing evidence. Actual CFO.ai canvas and forecast updates remain pending.
