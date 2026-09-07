# Agent Ops Starter

**한국어** | [English](#english)

Codex를 중심으로, 다른 AI CLI에도 옮겨 쓸 수 있게 만든 **portable agent-ops
baseline**입니다. 한 컴퓨터에서만 성립하는 개인 경로나 특정 모델 조합은 빼고,
몇 달 이상 운영하며 반복해서 다시 필요했던 규칙·상태·메모리·handoff·검사 구조만
남겼습니다. 비개발자가 반년간 실제 운영하며 겪은 붕괴(비용 폭발, 규칙 비대화,
메모리 부패)에서 살아남은 구조가 바탕입니다.

왜 이런 구조여야 하는지는 [ESSAY.md](ESSAY.md)를 먼저 읽어보세요.
10분이면 됩니다.

## 시작하기 (5분)

1. 이 폴더 내용물을 Codex를 실행하는 작업 폴더(프로젝트 루트)에 복사합니다.
2. Codex는 루트 `AGENTS.md`를 읽습니다. 다른 AI CLI에 옮길 때는 그 CLI의 native
   instruction entry point에서 `AGENTS.md`를 읽게 하거나 얇게 연결하세요. 운영 문서
   전체를 도구별로 복제하지 않는 것이 핵심입니다.
3. `docs/STATE.md`와 `docs/MEMORY_LEDGER.md`를 자신의 상황으로 채우세요.
   빈칸 채우기 형식입니다.

## 파일 지도

| 파일 | 역할 | 누가 읽나 |
|---|---|---|
| `AGENTS.md` | 항상 로드되는 유일한 파일. 라우터 — 규칙집이 아님 | AI (매 세션) |
| `docs/RETRIEVAL_MAP.md` | 문서 이름표. AI는 여기서 경로를 찾아 필요한 것만 엶 | AI (필요할 때) |
| `docs/OPERATING_PRINCIPLES.md` | 핵심 규칙: 규칙 추가 게이트, 다이어트 규칙, 사람 승인이 필요한 경계 | AI (규칙 작업 때) |
| `docs/STATE.md` | canonical ongoing work의 현재 스냅샷 (일기 금지) | AI (재개/인계 때) |
| `docs/MEMORY_LEDGER.md` | 재사용할 교훈만 축적 | AI (관련될 때) |
| `docs/HANDOFF_TEMPLATE.md` | AI에게 bounded task를 줄 때 쓰는 작업 지시 양식 | 사람이 복사해서 사용 |
| `.agents/skills/chatgpt-collaboration/SKILL.md` | 인앱 브라우저에서 ChatGPT와 협업하는 선택형 Codex 스킬 | Codex (관련 요청 때) |
| `tools/check_docs.py` | 문서 무결성 검사 (Python, 모든 OS). 월 1회 실행 | 사람 |
| `tools/check_docs.ps1` | 같은 검사의 PowerShell 판. 파이썬이 없을 때 | 사람 |
| `ESSAY.md` | 이 구조가 나온 이유 — 반년 운영의 실패 기록과 원리 | 사람 |

## 운영 루틴 (사람이 할 일)

- **매일**: 없음. AI가 알아서 필요한 문서만 읽습니다.
- **일이 끝날 때**: canonical ongoing thread를 진전시킨 의미 있는 작업이면
  `STATE.md`를 갱신합니다. bounded/parallel work는 shared state를 직접 덮지 말고
  다음 단계나 변경된 전제를 controlling thread에 보고합니다. 재사용할 교훈이
  있을 때만 `MEMORY_LEDGER.md`에 한 줄 추가합니다.
- **월 1회 (5분)**: `python3 tools/check_docs.py` 실행 → `RESULT: PASS` 확인.
  (파이썬이 없으면 `pwsh -NoProfile -File tools/check_docs.ps1`)
  FAIL이면 출력을 AI에게 붙여넣고 "고쳐줘".
- **분기 1회**: AI에게 "OPERATING_PRINCIPLES의 Diet Protocol에 따라 삭제 후보를
  순위 목록으로만 제안해. 적용하지 마." → 훑어보고 승인한 것만 지우게 함.

검사기는 `docs/` 아래의 등록되지 않은 Markdown도 기본적으로 FAIL 처리합니다.
문서 이동 중 잠시 허용해야 할 때만 `--allow-orphans`(PowerShell은
`-AllowOrphans`)를 명시하세요. 이 옵션은 고아 문서만 WARN으로 낮추며 다른 오류는
그대로 실패합니다.

`docs/`는 AI가 실제 검색 대상으로 취급하는 **active retrievable corpus**입니다.
초안, 원시 로그, 보관본처럼 active retrieval에 참여하면 안 되는 자료는 검사기
통과를 위해 억지로 등록하지 말고 `docs/` 밖에 두세요.

## 규칙을 추가하고 싶을 때 (가장 중요)

추가하기 전에 `docs/OPERATING_PRINCIPLES.md`의 Intake Gate 세 질문을 통과해야
합니다. 요지: **측정되거나 실제로 겪은 문제가 없으면 규칙을 쓰지 마세요.**
이 킷이 작은 것은 미완성이라서가 아니라, 그게 원리이기 때문입니다.

## 커스터마이즈

- 새 문서를 만들면 반드시 `docs/RETRIEVAL_MAP.md`에 한 줄 등록하세요.
  등록 안 된 문서는 AI에게 존재하지 않는 문서이며 월간 검사도 실패합니다.
- 반복 작업 유형(보고서 작성, 자료 정리 등)에만 필요한 규칙은
  `docs/lanes/<작업명>/`에 두고 trigger로 불러오세요. 루트 `AGENTS.md`에는 넣지
  마세요.
- 특정 코드 디렉터리/subtree에만 적용되는 규칙은 그 subtree의 nested
  `AGENTS.md`에 두세요. **task-type rule은 lane, path-type rule은 nested
  `AGENTS.md`**로 나누면 retrieval이 단순해집니다.
- 새 컴퓨터에서 그대로 성립하지 않는 절대 경로, 계정·비밀, 특정 머신 전용 도구나
  일회성 모델 라우팅은 이 portable baseline에 넣지 말고 로컬 설정으로 두세요.
- 검사기는 두 판 모두 같은 항목을 검사합니다. 둘 중 편한 것을 쓰세요.
  자가검사는 `python3 tools/check_docs.py --self-test` 또는
  `pwsh -NoProfile -File tools/check_docs.ps1 -SelfTest`로 실행합니다.

## Codex 선택 기능: ChatGPT 협업

Codex 앱에서 "GPT와 협업해" 또는 "GPT Pro에게 리뷰시켜"라고 요청하면
`.agents/skills/chatgpt-collaboration/` 스킬이 인앱 브라우저 협업 절차를
제공합니다. 작은 질문은 새 채팅에서 직접 주고받고, 여러 파일이나 프로젝트
전체 검토는 선별한 ZIP 패킷으로 전달합니다.

이 기능은 Codex 인앱 브라우저와 로그인된 ChatGPT 계정이 있을 때만
작동합니다. 외부로 보낼 비공개 파일은 사용자가 해당 파일과 목적지를
명시적으로 승인해야 합니다. 이 스킬은 선택될 때만 전체 내용을 읽으므로
`AGENTS.md`의 상시 입력 비용을 늘리지 않습니다.

답변이 수십 분 걸릴 수 있는데, 소요 시간을 미리 추정할 필요는 없습니다.
스킬은 완료 신호에 대기를 걸어 답변이 끝나는 순간 이어서 작업하고, 대화 URL을
기록해 두므로 탭이 닫혀도 결과를 다시 찾습니다. 대기 중에는 ChatGPT로 아무것도
전송되지 않습니다.

---

# English

[한국어](#agent-ops-starter) | **English**

A **portable agent-ops baseline** built around Codex and designed to carry over
to other AI CLIs. It leaves out one-machine paths and model-specific routing,
while keeping the rules, state, memory, handoff, and integrity-check structure
that proved worth rebuilding across environments. The design comes from six
months of real operation by a non-developer through cost blowups, rule bloat,
and memory rot.

Read [ESSAY.md](ESSAY.md) first to see why the kit is shaped this way.
It takes ten minutes.

## Quickstart (5 minutes)

1. Copy the contents of this folder into the working folder (project root)
   where you run Codex.
2. Codex reads the root `AGENTS.md`. When porting the kit to another AI CLI,
   wire that CLI's native instruction entry point to `AGENTS.md` or use a thin
   adapter. Do not duplicate the whole operating-doc tree per tool.
3. Fill in `docs/STATE.md` and `docs/MEMORY_LEDGER.md` for your own situation.
   They are fill-in-the-blank templates.

## File Map

| File | Role | Read by |
|---|---|---|
| `AGENTS.md` | The only always-loaded file. A router — not a rulebook | AI (every session) |
| `docs/RETRIEVAL_MAP.md` | Name tags for docs. The AI resolves a path here and opens only what it needs | AI (on demand) |
| `docs/OPERATING_PRINCIPLES.md` | Core rules: intake gate for new rules, diet protocol, boundaries needing human approval | AI (rule work) |
| `docs/STATE.md` | Current snapshot of the canonical ongoing work (never a diary) | AI (resume/handoff) |
| `docs/MEMORY_LEDGER.md` | Reusable lessons only | AI (when relevant) |
| `docs/HANDOFF_TEMPLATE.md` | Task-instruction form for bounded work | Humans (copy per task) |
| `.agents/skills/chatgpt-collaboration/SKILL.md` | Optional Codex workflow for collaborating with ChatGPT in the in-app browser | Codex (matching requests) |
| `tools/check_docs.py` | Docs integrity check (Python, any OS). Run monthly | Humans |
| `tools/check_docs.ps1` | Same checks in PowerShell, for machines without Python | Humans |
| `ESSAY.md` | Where this structure came from — six months of failures and principles | Humans |

## Operating Routine (the human's job)

- **Daily**: nothing. The AI reads only the docs it needs.
- **When meaningful work finishes**: if it advanced the canonical ongoing
  thread, update `STATE.md`. Bounded or parallel work should report changed
  assumptions and the next step to the controlling thread instead of mutating
  shared state. Add one line to `MEMORY_LEDGER.md` only for a genuinely reusable
  lesson.
- **Monthly (5 min)**: run `python3 tools/check_docs.py` → confirm `RESULT: PASS`
  (no Python? `pwsh -NoProfile -File tools/check_docs.ps1`).
  If FAIL, paste the output to the AI and say "fix it."
- **Quarterly**: tell the AI "following the Diet Protocol in
  OPERATING_PRINCIPLES, propose deletion candidates as a ranked list only. Do
  not apply." → skim, approve, and let it delete only the approved items.

By default the checkers also FAIL on any unregistered Markdown file under
`docs/`. During an intentional migration only, pass `--allow-orphans`
(PowerShell: `-AllowOrphans`). It downgrades only orphan docs to WARN; every
other integrity error still fails.

`docs/` is the **active retrievable corpus**. Drafts, raw logs, archives, and
other material that should not participate in active retrieval belong outside
`docs/`; do not register them merely to satisfy the checker.

## Before Adding Any Rule (the most important part)

New rules must pass the three Intake Gate questions in
`docs/OPERATING_PRINCIPLES.md`. The gist: **no measured gap or lived failure,
no rule.** This kit stays small by design, not because it is unfinished.

## Customizing

- Every new doc must get one row in `docs/RETRIEVAL_MAP.md`. An unregistered
  doc does not exist for the AI and fails the monthly check.
- Put rules triggered by a recurring kind of work (reports, research, etc.) in
  `docs/lanes/<task>/` and load them on that trigger — not in root `AGENTS.md`.
- Put rules that apply only to a code directory/subtree in a nested
  `AGENTS.md` inside that subtree. **Task-type rules belong in lanes; path-type
  rules belong in nested `AGENTS.md`.**
- Keep absolute paths, accounts/secrets, one-machine-only tools, and temporary
  model routing out of this portable baseline. Those belong in local setup.
- Both checkers run the same checks — use whichever fits your machine. Run
  `python3 tools/check_docs.py --self-test` or
  `pwsh -NoProfile -File tools/check_docs.ps1 -SelfTest` to prove detection.

## Optional Codex Feature: ChatGPT Collaboration

When you ask Codex to "collaborate with GPT" or "review this with GPT Pro,"
the skill under `.agents/skills/chatgpt-collaboration/` supplies the in-app
browser workflow. Small questions use a clean chat directly; multi-file or
project-wide reviews use a curated ZIP packet.

This requires the Codex in-app browser and a signed-in ChatGPT account. Private
files may be uploaded only when the user explicitly authorizes those files and
ChatGPT as the destination. Codex loads the full skill only when it matches the
request, so it does not add the workflow to the always-loaded `AGENTS.md`.

A reply can take tens of minutes, and you never have to estimate how long. The
skill blocks on the completion signal so it resumes the moment the answer lands,
and it records the conversation URL so the result is recoverable even if the tab
closes. Waiting sends nothing to ChatGPT.

## License

MIT — see [LICENSE](LICENSE).
