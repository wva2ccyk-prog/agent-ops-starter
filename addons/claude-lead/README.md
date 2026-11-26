# Claude 리드 확장팩

[agent-ops-starter](../../README.md) 위에 얹는 선택형 애드온입니다. Claude가 리드가 되어
GPT(Codex), agy(Gemini Neon), GPT Pro를 필요할 때 불러 쓰게 해 줍니다.

## 쓰는 법

설치는 직접 하지 않아도 됩니다. 이 레포를 받은 뒤 Claude Code(Opus)에게 이렇게 말하세요.

> `addons/claude-lead/APPLY.md` 읽고 내 컴퓨터와 내 업무에 맞게 판단해서 적용해 줘.

Opus가 필수와 선택을 구분해 설치하고, 이 컴퓨터에서 GPT·agy가 실제로 불리는지 확인한 뒤 결과를 알려 줍니다.

## 설치 후에는

- "GPT 불러서 엑셀 정리 시켜", "agy한테 자료조사 맡겨"처럼 이름만 말하면 됩니다.
- 모델을 말하지 않으면 Claude가 아래 표에서 맞는 걸 한 줄로 제안하고 확인받은 뒤 실행합니다.
- 유사성 분석 작업은 "유사성 분석 시작하자"라고 하면 `projects/doc-similarity/`의 7단계 흐름을 따릅니다.

| 모델 | 이럴 때 적합 |
|---|---|
| Claude (대화 상대) | 무엇을 할지 판단, 최종 검토, 대외 문서 톤 |
| GPT sol (기본) | 파일을 직접 만지는 일: 엑셀 정리·변환, 여러 파일 일괄 처리. 검토자로 쓰면 숫자·논리 검증 |
| GPT astra | 직접 지명할 때만 |
| agy Neon | 자료조사, 긴 PDF 요약, 문서 대조표(high) / 두 번째 의견(xhigh) |
| GPT Pro (ChatGPT에서 직접) | 한 번에 큰 일: 긴 보고서 전체 검토, 대량 자료 분석 |

## 꼭 알아둘 것

GPT, agy, GPT Pro, 그리고 Claude도 외부 서비스입니다. 기관 문서를 보내기 전에 Claude가 무엇을 어디로 보내는지 묻습니다.
비공개·개인정보 문서는 보내지 않고 내 컴퓨터 안에서만 처리합니다 (`projects/doc-similarity/SECURITY.md`).
