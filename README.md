# Banking Simulator

A simulated banking system with lazy cashback settlement, temporal balance
auditing, and account mergers. Built as a layered full-stack application:
a pure Python domain engine, a thin FastAPI layer, and a React dashboard.

**Live demo:** https://banking-simulator.vercel.app
**API docs:** https://banking-simulator-api.onrender.com/docs

> Note: the API runs on Render's free tier. The first request after idle
> can take up to a minute while the service wakes. State is in-memory by
> design and resets on restart, so every visitor gets a clean slate.

## Architecture
Layer 4:  React dashboard (Vite + TypeScript + TanStack Query)
|  HTTP
Layer 3:  FastAPI (thin routers + Pydantic validation)
|  method calls
Layer 2:  BankingService orchestration (settle-then-execute)
|
Layer 1:  Domain engine (pure Python, zero dependencies)

The domain engine has an empty runtime dependency list. All business
logic (accounts, ledger, cashback scheduling, mergers) uses only the
standard library. FastAPI and the frontend were added in later stages
with zero diffs to domain files, which was the point of the layering.

The API deliberately splits into two routers:

- `/operations/*`: spec operations. Every call carries a simulation
  timestamp and advances simulated time (settling due cashbacks first).
  All are POST, including reads, because reads mutate state here.
- `/views/*`: observability endpoints for the dashboard. No timestamps,
  no settlement, no side effects. The UI layout mirrors this split:
  controls on the left, observability on the right.

## Key design decisions

**Lazy cashback settlement with a min-heap.** Time in this system is
simulated, not wall-clock. Cashbacks are due 24 simulated hours after a
payment and must apply before any operation whose timestamp crosses the
due time. A background scheduler (Celery, cron) would be architecturally
wrong, not just heavier: it fires on real time, and this domain has none.
Instead, pending cashbacks sit in a `heapq` keyed on execution time, and
every operation pops and applies due entries before running. O(log n)
scheduling, O(log n) per settlement, no infrastructure.

**Settlement records history at the scheduled time, not the trigger
time.** If a cashback due at t=86,400,005 settles because an operation
arrived at t=99,999,999, the balance history entry is written at
86,400,005. Without this, historical balance queries between those two
times would miss money that had, in simulation time, already landed.

**Append-only balance history with bisect lookups.** Balances are never
overwritten in isolation. Every mutation appends `(timestamp, balance)`
to a per-account history, and `getBalance(account, timeAt)` is a binary
search (`bisect_right`, so a query at an exact event timestamp reflects
state after that event, per spec). O(log n) temporal audits, and the
structure maps one-to-one onto a transactions table if a database is
added later.

**Integer math for cashback (2%).** `amount * 2 // 100` instead of
`int(amount * 0.02)`. Float-then-floor is a real bug class: 0.02 has no
exact binary representation, and the pattern produces off-by-one errors
at certain magnitudes. Integer arithmetic makes the question unaskable.

**Mergers use redirect pointers, not deletion.** A merged account gets
`merged_into` set and becomes inactive. Old payment IDs still resolve by
chasing the pointer chain (union-find without path compression, which is
unnecessary at this scale). Pending cashbacks are not rewritten at merge
time; settlement resolves the pointer when it fires. Late binding avoids
O(n) heap surgery per merge.

**Pre-merger balance queries return the primary account alone.** The
spec says a merged account's history is "inherited" but leaves pre-merger
queries ambiguous: after B merges into A at t=5000, is A's balance at
t=3000 just A, or A+B combined? I chose A alone. The merge is an event;
history before it is immutable. The absorbed account's history remains
queryable under its own ID, which satisfies "inheritance" without
rewriting the past. Retroactive summing would mean an audit endpoint
whose answers change over time, which defeats auditing. Documented and
pinned by a test.

**The spec's own example is internally inconsistent.** It has account2
make a payment, then checks that payment's status against account1 and
credits the cashback to account1 in its final arithmetic. I implemented
the spec's rules (cashback goes to the paying account) rather than its
example, and encoded the corrected sequence as an integration test.

## Bugs encountered and fixed

1. **Flexbox crushing the operation log.** The log is a flex column with
   `max-height` and `overflow-y: auto`. When entries exceeded the height,
   rows compressed and clipped mid-glyph instead of scrolling, because
   flex children default to `flex-shrink: 1` and shrink before overflow
   is consulted. Fix: `flex-shrink: 0` on entries.
2. **Frontend timestamp counter reset on refresh.** The auto-increment
   timestamp lived in a React ref, so a page refresh reset it to 1 while
   the engine was at t=28, risking out-of-order writes that would
   silently corrupt the ledger's sorted invariant. Fix: the engine now
   tracks `last_timestamp` (updated in `_settle`, the one choke point
   every operation passes through), exposes it via `/views/clock`, and
   the frontend initializes from it.
3. **CSS variables inside Recharts SVG attributes were unreliable**,
   which forced hardcoded hex, which then broke when light/dark themes
   arrived. Fix: a single palette source in TypeScript consumed by chart
   components via a theme context, with CSS variables redefined per
   `data-theme` for everything else.

## Running locally

Backend:

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt -r requirements-dev.txt
    pip install -e . --no-deps
    pytest                       # full engine + API suite
    uvicorn banking.api.main:app --reload

Frontend (separate terminal):

    cd dashboard
    npm install
    npm run dev                  # expects the API on 127.0.0.1:8000

## Known limitations

- In-memory state: resets on deploy or restart. Acceptable for a
  simulator; a Postgres repository behind the existing layer boundary is
  the production upgrade path.
- Single uvicorn worker, by design: the engine is a per-process
  singleton, so multiple workers would mean multiple divergent banks.
- No auth: all visitors share one simulated bank.
- Unbounded settlement per request: a pathological gap could make one
  request settle many cashbacks. A production system would bound work
  per request.