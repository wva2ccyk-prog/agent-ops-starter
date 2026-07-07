# Agent Ops Starter

**한국어** | [English](#english)

AI CLI(Codex, Claude Code, Gemini CLI 등)를 **몇 달 이상 무너지지 않게** 굴리기
위한 최소 골격입니다. 비개발자가 반년간 실제 운영하며 겪은 붕괴(비용 폭발,
규칙 비대화, 메모리 부패)에서 살아남은 구조만 남겼습니다.

왜 이런 구조여야 하는지는 [ESSAY.md](ESSAY.md)를 먼저 읽어보세요.
10분이면 됩니다.

## 시작하기 (5분)

1. 이 폴더 내용물을 AI CLI를 실행하는 작업 폴더(프로젝트 루트)에 복사합니다.
2. 끝입니다. 대부분의 AI CLI는 `AGENTS.md`를 자동으로 읽습니다
   (Claude Code는 `CLAUDE.md`라는 이름을 쓰므로, 복사본을 하나 더 만들거나
   `CLAUDE.md` 안에 "Read AGENTS.md first" 한 줄을 넣으세요).
3. `docs/STATE.md`와 `docs/MEMORY_LEDGER.md`를 자신의 상황으로 채우세요.
   빈칸 채우기 형식입니다.

## 파일 지도

| 파일 | 역할 | 누가 읽나 |
|---|---|---|
| `AGENTS.md` | 항상 로드되는 유일한 파일. 라우터 — 규칙집이 아님 | AI (매 세션) |
| `docs/RETRIEVAL_MAP.md` | 문서 이름표. AI는 여기서 경로를 찾아 필요한 것만 엶 | AI (필요할 때) |
| `docs/OPERATING_PRINCIPLES.md` | 핵심 규칙: 규칙 추가 게이트, 다이어트 규칙, 사람 승인이 필요한 경계 | AI (규칙 작업 때) |
| `docs/STATE.md` | 지금 무엇을 하고 있는가 — 스냅샷 (일기 금지) | AI (재개할 때) |
| `docs/MEMORY_LEDGER.md` | 재사용할 교훈만 축적 | AI (관련될 때) |
| `docs/HANDOFF_TEMPLATE.md` | AI에게 일 시킬 때 쓰는 작업 지시 양식 | 사람이 복사해서 사용 |
| `tools/check_docs.ps1` | 문서 무결성 검사 (Windows PowerShell). 월 1회 실행 | 사람 |
| `ESSAY.md` | 이 구조가 나온 이유 — 반년 운영의 실패 기록과 원리 | 사람 |

## 운영 루틴 (사람이 할 일)

- **매일**: 없음. AI가 알아서 필요한 문서만 읽습니다.
- **일이 끝날 때**: 의미 있는 작업이면 AI에게 "STATE.md 갱신하고, 재사용할
  교훈이 있으면 MEMORY_LEDGER에 한 줄 추가해" 라고 지시.
- **월 1회 (5분)**: `tools/check_docs.ps1` 실행 → `RESULT: PASS` 확인.
  FAIL이면 출력을 AI에게 붙여넣고 "고쳐줘".
- **분기 1회**: AI에게 "OPERATING_PRINCIPLES의 Diet Protocol에 따라 삭제 후보를
  순위 목록으로만 제안해. 적용하지 마." → 훑어보고 승인한 것만 지우게 함.

## 규칙을 추가하고 싶을 때 (가장 중요)

추가하기 전에 `docs/OPERATING_PRINCIPLES.md`의 Intake Gate 세 질문을 통과해야
합니다. 요지: **측정되거나 실제로 겪은 문제가 없으면 규칙을 쓰지 마세요.**
이 킷이 작은 것은 미완성이라서가 아니라, 그게 원리이기 때문입니다.

## 커스터마이즈

- 새 문서를 만들면 반드시 `docs/RETRIEVAL_MAP.md`에 한 줄 등록하세요.
  등록 안 된 문서는 AI에게 존재하지 않는 문서입니다.
- 반복 작업(보고서 작성, 자료 정리 등)이 생기면 `docs/lanes/<작업명>/` 폴더를
  만들고 그 안에 작업 전용 규칙을 두세요. AGENTS.md에는 넣지 마세요.
- macOS/Linux 사용자는 `check_docs.ps1`을 AI에게 주고 "bash로 포팅해 줘" 하면
  됩니다.

---

# English

[한국어](#agent-ops-starter) | **English**

A minimal skeleton for running AI CLIs (Codex, Claude Code, Gemini CLI, etc.)
**for months without collapse**. A non-developer operated a real system for
half a year, went through the failures — cost explosion, rule bloat, memory
rot — and kept only the structure that survived.

Read [ESSAY.md](ESSAY.md) first to see why the kit is shaped this way.
It takes ten minutes.

## Quickstart (5 minutes)

1. Copy the contents of this folder into the working folder (project root)
   where you run your AI CLI.
2. That's it. Most AI CLIs auto-load `AGENTS.md` (Claude Code uses the name
   `CLAUDE.md` — make a copy, or put one line "Read AGENTS.md first" in it).
3. Fill in `docs/STATE.md` and `docs/MEMORY_LEDGER.md` for your own situation.
   They are fill-in-the-blank templates.

## File Map

| File | Role | Read by |
|---|---|---|
| `AGENTS.md` | The only always-loaded file. A router — not a rulebook | AI (every session) |
| `docs/RETRIEVAL_MAP.md` | Name tags for docs. The AI resolves a path here and opens only what it needs | AI (on demand) |
| `docs/OPERATING_PRINCIPLES.md` | Core rules: intake gate for new rules, diet protocol, boundaries needing human approval | AI (rule work) |
| `docs/STATE.md` | What is being worked on now — a snapshot (never a diary) | AI (resuming) |
| `docs/MEMORY_LEDGER.md` | Reusable lessons only | AI (when relevant) |
| `docs/HANDOFF_TEMPLATE.md` | Task-instruction form for giving the AI bounded work | Humans (copy per task) |
| `tools/check_docs.ps1` | Docs integrity check (Windows PowerShell). Run monthly | Humans |
| `ESSAY.md` | Where this structure came from — half a year of failures and principles | Humans |

## Operating Routine (the human's job)

- **Daily**: nothing. The AI reads only the docs it needs.
- **When meaningful work finishes**: tell the AI "update STATE.md, and add one
  line to MEMORY_LEDGER only if there is a genuinely reusable lesson."
- **Monthly (5 min)**: run `tools/check_docs.ps1` → confirm `RESULT: PASS`.
  If FAIL, paste the output to the AI and say "fix it."
- **Quarterly**: tell the AI "following the Diet Protocol in
  OPERATING_PRINCIPLES, propose deletion candidates as a ranked list only. Do
  not apply." → skim, approve, and let it delete only the approved items.

## Before Adding Any Rule (the most important part)

New rules must pass the three Intake Gate questions in
`docs/OPERATING_PRINCIPLES.md`. The gist: **no measured gap or lived failure,
no rule.** This kit is small not because it is unfinished, but because that is
the principle.

## Customizing

- Every new doc must get one row in `docs/RETRIEVAL_MAP.md`. An unregistered
  doc does not exist for the AI.
- When a repeating task family emerges (reports, research, etc.), create
  `docs/lanes/<task>/` and keep task-specific rules there — not in AGENTS.md.
- On macOS/Linux, hand `check_docs.ps1` to your AI and say "port this to bash."

## License

MIT — see [LICENSE](LICENSE).
