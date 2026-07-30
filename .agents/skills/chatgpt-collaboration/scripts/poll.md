# Waiting On A Long ChatGPT Run

Reference for the Codex in-app browser, verified 2026-07-30 on macOS and on a
Windows machine using the Korean ChatGPT UI. Paste these blocks into the Node
REPL `js` tool after the browser runtime and the in-app browser binding exist.

The timing measurements below come from one macOS machine and one ChatGPT web
build. The completion signal, localized labels, and URL recovery were
re-confirmed on Windows with the Korean UI. The approach holds; exact labels and
DOM attributes can still drift. Re-confirm the completion signal once on a new
machine before trusting a long unattended wait.

## Completion signal

While a reply is streaming, the composer buttons are gone: the send control is
absent and no stop-streaming button exists in these builds. The reliable edge is
the latest assistant turn's response-actions group appearing.

The assistant copy action becoming visible means generation finished. It is
localized (`Copy response` in English, `응답 복사` in Korean), so the runnable
code uses the stable `copy-turn-action-button` test ID and scopes it to the
latest assistant turn. Do not watch the test ID globally: the user-message copy
button uses the same ID and would be a false positive.

The tier labels are localized too. The Korean UI showed `높음`, `매우 높음`,
and `Pro` where the English UI showed `High`, `Extra High`, and `Pro`. Select
the exact visible menu item and confirm its checked state; never use a loose
`High` text match.

Rejected alternatives, each tested and each wrong:

- sentinel tokens (`DONE_MARKER`): the token appears mid-stream, long before the
  answer is complete;
- text growth: pauses mid-answer look identical to completion;
- CDP network events: see below. This one looks correct and is not.

### Why network events do not work

Tempting, because `text/event-stream` is exactly the response that carries the
answer. Measured 2026-07-30: sending a prompt opens two `/backend-api/f/conversation`
POSTs, one `application/json` and one `text/event-stream`. The event-stream
request emits `loadingFinished` at ~4.3KB roughly 100ms after send, while the
answer keeps generating for another minute. A later watch across a full answer saw
no further stream open/close events before the answer completed.

So `loadingFinished` on the stream is not the end of the answer, and there is no
second network event to key on. Any wait built on it returns `done` in ~15ms with
an empty answer. Do not rebuild this.

Page-side observers are also unavailable: `tab.playwright.evaluate` runs in a
read-only scope where `localStorage` is `undefined`, so a `MutationObserver` that
records completion for later cannot be installed.

## Send without waiting

Record the current turn count before sending, then record the conversation URL
immediately after send. The baseline prevents an older completed answer from
satisfying the wait; the URL is the durable recovery handle.

```js
globalThis.turnsBeforeSend = tab.playwright.locator(
  'section[data-testid^="conversation-turn-"]'
);
globalThis.turnCountBeforeSend = await turnsBeforeSend.count();
await tab.playwright.getByTestId("send-button").click();
await tab.playwright.waitForTimeout(4000);   // let the URL settle to /c/<id>
globalThis.convUrl = await tab.url();        // https://chatgpt.com/c/<id>
nodeRepl.write(convUrl);                     // save this into the run notes
```

Write `convUrl` into the packet directory so it survives context compaction.

## Waiting without knowing the duration

You do not need to estimate the runtime. Block on the signal with `waitFor` and
let it return the moment the answer lands.

`waitFor` has its own short internal ceiling in this runtime — a 60s request
failed after ~3s — so wrap it in a loop that re-arms until the budget is spent.
Each iteration is a blocking wait, not an interval sample.

```js
globalThis.awaitAnswer = async ({ budgetMs = 240000, stepMs = 20000 } = {}) => {
  const turns = tab.playwright.locator(
    'section[data-testid^="conversation-turn-"]'
  );
  const until = Date.now() + budgetMs;
  const start = Date.now();
  let probes = 0;
  while (Date.now() < until) {
    probes++;
    const count = await turns.count();
    if (count > turnCountBeforeSend) {
      const candidate = turns.nth(count - 1); // safe: count was just checked
      const isAssistant = await candidate.locator(
        '[data-message-author-role="assistant"]'
      ).count();
      if (isAssistant > 0) {
        const done = candidate.getByTestId("copy-turn-action-button");
        try {
          await done.waitFor({
            state: "visible",
            timeoutMs: Math.min(
              stepMs,
              Math.max(1000, until - Date.now())
            )
          });
          return { status: "done", probes, elapsedMs: Date.now() - start };
        } catch { /* reply exists, still streaming */ }
        continue;
      }
    }
    await tab.playwright.waitForTimeout(
      Math.min(250, Math.max(1, until - Date.now()))
    );
  }
  return {
    status: "still-running",
    probes,
    elapsedMs: Date.now() - start
  };
};
nodeRepl.write(JSON.stringify(await awaitAnswer()));   // pass timeout_ms: 300000
```

Verified: a 52s answer returned `{status:"done", elapsedMs:52235}` from one call,
with no duration guess supplied.

Cost model:

- DOM checks and waits send nothing to ChatGPT;
- re-arming *inside* one `js` call costs nothing in the transcript;
- the only real cost is the number of `js` calls, so keep each call long. One
  call held a 120s sleep exactly (`held ms=119995`); 240s is safe under a 300s
  `timeout_ms`.

Call budget when the duration is unknown:

| Actual run | Calls spent |
| --- | --- |
| under ~4 min | 1 |
| 5-20 min | 2-5, re-arming on `still-running` |
| 20 min or more | switch to a heartbeat, 1 per wakeup |

On `still-running`, send one short commentary line and call it again. Do not
shorten `stepMs` to feel busy, do not re-snapshot the page while waiting, and
never resend the prompt.

## Resume across turns or after a reset

`tabs.finalize({ keep: [{ status: "handoff", tab }] })` did NOT leave the tab in
`iab.user.openTabs()` on this build, so do not rely on reclaiming a tab. Reopen
the conversation URL instead; the answer is server-side and fully rendered.

```js
globalThis.tab = await iab.tabs.new();
await tab.goto(convUrl);
await tab.playwright.waitForLoadState({ state: "domcontentloaded", timeoutMs: 60000 });
await tab.playwright.waitForTimeout(3000);
globalThis.recoveredTurns = tab.playwright.locator(
  'section[data-testid^="conversation-turn-"]'
);
globalThis.recoveredTurnCount = await recoveredTurns.count();
globalThis.recoveredDone = false;
if (recoveredTurnCount > 0) {
  globalThis.recoveredLastTurn = recoveredTurns.nth(recoveredTurnCount - 1);
  globalThis.recoveredDone =
    await recoveredLastTurn.locator(
      '[data-message-author-role="assistant"]'
    ).count() > 0 &&
    await recoveredLastTurn.getByTestId(
      "copy-turn-action-button"
    ).count() > 0;
}
nodeRepl.write("done=" + recoveredDone);
```

This survives a full `js_reset`, a lost tab, and a closed browser.

## Reading the answer

Read it from the DOM. The assistant copy action is a completion *signal* only:
clicking it did not populate the clipboard on the macOS build (verified
2026-07-30 — a sentinel written with `clipboard.writeText` survived the click
unchanged), so do not use the clipboard as the extraction path.

```js
globalThis.md = tab.playwright.locator("div.markdown");
const n = await md.count();                    // one per assistant response
globalThis.answer = await md.innerText({ timeoutMs: 15000 });
nodeRepl.write(answer);
```

With one response in the thread, `count()` is `1` and `innerText()` returns the
full markdown text. In a multi-turn thread `div.markdown` matches every response,
so scope to the last response group first and confirm `count()` is `1` before
reading; do not reach for `.last()` without checking.

A long answer can be large. Write it to the packet directory instead of dumping
it into the transcript when it is not needed inline.

## Waits of 20 minutes or more

Do not hold the session open. Persist `convUrl`, set a heartbeat automation on
the thread to wake after the expected duration, then on wakeup reopen `convUrl`
and check the completion signal once. Zero probes are spent while asleep.

This is the preferred path for Pro, Deep Research, and any Thinking Extra High
run over a wide packet, which can take tens of minutes. Nothing is lost by sleeping: the
answer is generated server-side whether or not a tab is watching.
