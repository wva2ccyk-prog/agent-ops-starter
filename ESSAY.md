# 비개발자가 AI를 반년 굴리며 배운 것 — 왜 이 킷은 이렇게 생겼나

**한국어** | [English](#what-a-non-developer-learned-from-running-ai-for-half-a-year--why-this-kit-looks-the-way-it-does)

나는 개발자가 아니다. 그런데 AI CLI를 매일 쓰다 보니 어느새 규칙 문서 수백
개를 가진 운영 체계를 혼자 만들어 굴리고 있었다. 그 과정에서 비용이 폭발해
전면 개편을 한 번 했고, 여러 모델에게 감사를 맡겼고, 유행하는 메모리·RAG
도구들을 조사했다. 이 킷은 그중 **살아남은 것만** 담은 골격이다. 아래는 그
반년의 결론이다.

## 실패의 기록 (내가 겪은 순서대로)

**1. AI는 시키지 않아도 기억하려 든다.** 내가 말한 것들이 어느새 규칙 문서에
전부 축적되고 있었고, 매 세션 입력 비용이 폭발했다. AI는 "보존"이 기본값이다.
망각 메커니즘이 없는 축적은 반드시 비대해진다.

**2. 태그를 달았지만 아무것도 하지 않았다.** LLM 위키를 꿈꾸며 모든 문서에
태그·분류 체계를 달았다. 나중에 AI에게 직접 물어보니, AI는 태그를 한 번도
사용하지 않았다. 태그는 파일을 **연 뒤에야** 보이므로 "열지 말지"의 결정에
기여할 수 없다. 항행은 파일명, 이름표(리졸버), 그리고 이미 읽은 문서 속
포인터로만 이루어진다. 1,300줄의 태그를 지웠고 아무 일도 일어나지 않았다.

**3. 규칙은 써놨다고 지켜지는 게 아니다.** "외부 모델을 활용하라"는 규칙을
정성껏 썼지만 실측해 보니 준수율은 42%였다. 이유는 구조적이었다: 그 규칙이
"필요할 때만 읽는 문서" 안에 있었는데, 규칙을 고려하지 않는 AI는 그 문서를
열 이유가 없다. **열리지 않은 파일 속 규칙은 존재하지 않는 규칙이다.**

**4. AI에게 자기반성을 시키면 지어낸다.** "네가 과잉 실행했는지 스스로
평가해 기록하라" 같은 자기보고 필드를 만들었더니, AI는 "아니오"라고 지어내서
채웠다. 가짜 준수 데이터는 데이터가 없는 것보다 나쁘다. AI가 계산할 수 없는
지표를 요구하지 마라 — 측정은 스크립트가 한다.

**5. 삭제를 시키면 양극단으로 간다.** "신중히 정리해"라고 하면 전부 보존하고,
"과감히 지워"라고 하면 무차별로 지운다. 외부 모델에게 감사를 맡겨도
똑같았다. AI에게 "이게 중요한가?"라는 절대 판단을 시키면 판단 기준이 증거가
아니라 지시문의 어조에서 오기 때문이다.

**6. 리뷰를 맡기면 항상 일감이 나온다.** 어떤 모델에게 맡겨도 "고칠 것"이
나왔고, 서로 반대 방향이었다. 리뷰어 역할을 받은 LLM에게 "고칠 게 없다"는
사실상 불가능한 출력이다. 발견이 나왔다는 것은 시스템이 부족하다는 증거가
아니다.

**7. 유행하는 메모리 제품들은 장기 운영에서 무너진다.** 벡터·임베딩 기반
자동 메모리를 조사했지만 좋은지 이해할 수 없었고, 그 직감은 맞았다. 유사도
검색은 "의미가 비슷한 것"을 가져올 뿐 "폐기된 옛 결정"과 "어제의 결정"을
구분하지 못하며, 코퍼스가 클수록 오염이 심해진다. 그리고 저장소 안에 뭐가
들었는지 사람이 감사할 수 없다. 무너지는 중이어도 무너진 뒤에야 안다.

## 살아남은 원리

1. **항상 로드되는 파일은 하나, 그것도 라우터.** 규칙집이 아니라 이정표.
   나머지는 전부 문 뒤에 두고 필요할 때만 연다. AI는 파일을 통째로 읽으므로
   비용 절감은 "파일을 작게, 여는 수를 적게"에서만 나온다.
2. **모든 문서는 이름표(리졸버)에 등록한다.** 등록 안 된 문서는 AI에게
   존재하지 않는다. 태그·분류 체계는 만들지 마라 — 장식이다.
3. **산문 < 템플릿 < 스크립트.** 산문 규칙은 가장 약한 도구다. 강제하고 싶은
   것은 템플릿의 필수 빈칸으로, 검증하고 싶은 것은 스크립트로 만들어라.
4. **AI에게는 시계도 눈금도 없다.** 정기 점검은 스케줄러(기계)가 시작하고,
   측정은 스크립트가 하고, AI는 그 결과를 읽고 제안만 한다.
5. **삭제는 절대 판단이 아니라 순위 + 쿼터로.** "가치 낮은 순으로 최대
   10개, 각각 인용 가능한 근거를 붙여 제안만 해라. 적용은 내가 승인한다."
   이 한 문장이 전부-보존과 전부-삭제를 동시에 막는다.
6. **무인 실행은 영원히 제안 전용.** 사람 없이 도는 AI에게 문서 수정 권한을
   주지 마라. 산출물은 항상 "파일로 남는 제안"이어야 한다.
7. **축적은 통치 없이 붕괴한다.** 새 규칙은 측정된 문제나 실제 겪은 실패가
   있을 때만 추가하고, 한 번도 발동하지 않은 규칙은 지운다. 상태(변하는 것)와
   규칙(안 변하는 것)을 같은 파일에 섞지 마라.
8. **기억은 응고 파이프라인이다.** 원시 기록(작업 로그)은 읽기 경로 밖에
   보관하고, 주기적으로 토큰을 써서 재사용 가능한 교훈으로 증류하고, 교훈만
   읽기 경로 안에 둔다. 이것이 얼어붙은 가중치를 가진 LLM에게 물리적으로
   가능한 유일한 장기 기억이다. 인간의 수면이 하는 일과 같다.
9. **완성을 선언할 줄 알아야 한다.** 점검이 두 번 연속 통과하고 측정치가
   안정이면 만지지 마라. 정비 자체에도 비용이 있고, 잦은 개정은 개선이 아니라
   진동이다.

## 이 킷을 쓰는 사람에게

이 킷이 작은 것은 시작이라서가 아니라 그게 결론이기 때문이다. 당신의 작업이
늘어나면 문서도 늘겠지만, 늘어난 문서가 전부 이름표에 등록되어 있고, 세션당
여는 파일이 두세 개로 유지되고, 월 1회 검사가 통과하는 한 이 체계는 무너지지
않는다. 내가 겪은 붕괴는 전부 이 세 가지 중 하나가 깨졌을 때 왔다.

— 반년간 AI 운영 체계를 만들고 부수고 다시 만든 어느 비개발자

---

# What a Non-Developer Learned from Running AI for Half a Year — Why This Kit Looks the Way It Does

[한국어](#비개발자가-ai를-반년-굴리며-배운-것--왜-이-킷은-이렇게-생겼나) | **English**

I am not a developer. But after using AI CLIs every day, I found myself
running an operating system of hundreds of rule documents that I had built
alone. Along the way my costs exploded and forced one full overhaul; I had
multiple models audit the system; I investigated the trending memory and RAG
tools. This kit is the skeleton of **only what survived**. Below are the
conclusions of that half year.

## A Record of Failures (in the order I hit them)

**1. AI hoards memory even when you don't ask.** Things I said kept
accumulating into the rule docs without me noticing, and per-session input
costs exploded. "Preserve" is the AI's default. Accumulation without a
forgetting mechanism always bloats.

**2. I added tags; they did nothing.** Dreaming of an LLM wiki, I tagged and
classified every document. When I later asked the AI directly, it had never
used a single tag. Tags are visible only **after** a file is opened, so they
cannot contribute to the decision of *whether* to open it. Navigation happens
only through file names, a name-tag resolver, and pointers inside documents
already read. I deleted 1,300 lines of tags and nothing changed.

**3. A written rule is not a followed rule.** I carefully wrote a rule to
"use external worker models," then actually measured compliance: 42%. The
reason was structural: the rule lived inside a read-on-demand document, and an
AI that isn't considering delegation has no reason to open that document.
**A rule inside an unopened file is a rule that does not exist.**

**4. Ask an AI for self-reflection and it confabulates.** I created
self-report fields like "assess whether you over-executed." The AI just made
up "no." Fake compliance data is worse than no data. Never demand metrics the
AI cannot compute — measurement belongs to scripts.

**5. Deletion requests swing to extremes.** Say "clean up carefully" and it
preserves everything; say "delete boldly" and it deletes indiscriminately.
External auditor models did the same. When you ask an AI the absolute question
"is this important?", the threshold comes from the tone of your instruction,
not from evidence.

**6. Every review produces findings.** Whichever model I hired, "things to
fix" came back — often in opposite directions. For an LLM given the reviewer
role, "nothing to fix" is a practically impossible output. Findings are not
evidence that your system is deficient.

**7. Trending memory products collapse under long-term operation.** I studied
vector/embedding auto-memory and couldn't see why it was good; that instinct
was correct. Similarity search retrieves "what sounds alike" — it cannot tell
a discarded old decision from yesterday's decision, and the pollution worsens
as the corpus grows. And a human cannot audit what's inside the store: even
while it is collapsing, you only find out after it has collapsed.

## The Principles That Survived

1. **One always-loaded file, and it is a router.** A signpost, not a
   rulebook. Everything else lives behind doors and is opened on demand. An
   AI reads files whole, so cost reduction comes only from "smaller files,
   fewer opens."
2. **Every document gets one row in the resolver.** An unregistered document
   does not exist for the AI. Do not build tag taxonomies — they are
   decoration.
3. **Prose < templates < scripts.** Prose rules are the weakest instrument.
   What you want enforced becomes a required blank in a template; what you
   want verified becomes a script.
4. **The AI has no clock and no gauge.** Machines (schedulers) initiate
   periodic checks, scripts do the measuring, and the AI only reads results
   and proposes.
5. **Deletion by ranking + quota, never absolute judgment.** "Propose at most
   10 items, least valuable first, each with one citable signal. I approve
   before anything is applied." That one sentence blocks both keep-everything
   and delete-everything.
6. **Unattended runs are proposal-only, forever.** Never give document-edit
   authority to an AI running without a human watching. Its output must
   always be a proposal left in a file.
7. **Accumulation collapses without governance.** Add a rule only for a
   measured gap or a lived failure; delete rules that never fire. Never mix
   state (what changes) and rules (what doesn't) in the same file.
8. **Memory is a consolidation pipeline.** Keep raw logs out of the read
   path; periodically spend tokens distilling them into reusable lessons;
   keep only the lessons in the read path. This is the only physically
   possible long-term memory for an LLM with frozen weights — it is what
   human sleep does.
9. **Know how to declare "done."** If checks pass twice in a row and the
   metrics are stable, don't touch it. Maintenance itself has a cost, and
   frequent revision is oscillation, not improvement.

## To Whoever Uses This Kit

This kit is small not because it is a beginning, but because smallness is the
conclusion. As your work grows, your documents will grow too — but as long as
every new document is registered in the resolver, per-session reads stay at
two or three files, and the monthly check passes, this system will not
collapse. Every collapse I lived through came from breaking one of those
three.

— A non-developer who built, broke, and rebuilt an AI operating system for
half a year
