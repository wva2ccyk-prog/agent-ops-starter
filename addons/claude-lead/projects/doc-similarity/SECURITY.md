# 기관 문서 외부 전송 체크 (Security check)

Claude, GPT(Codex), agy, GPT Pro는 모두 외부 클라우드 서비스입니다. 문서 내용을 넣는 순간 그 회사(Anthropic,
OpenAI, Google)로 전송됩니다. 유사도 계산용 클라우드 임베딩 API도 같습니다. 아래를 통과한 묶음만 보냅니다.

## 1. 보내기 전 (묶음마다)

- [ ] 기관의 생성형 AI 사용 지침을 확인했다. 지침이 이 문서보다 우선한다.
- [ ] 문서 등급을 확인했다: 공개 / 비공개 / 대외비.
- [ ] 개인정보(이름, 주민번호, 연락처, 주소 등)가 들어 있는지 확인했다.
- [ ] 비공개·대외비·개인정보 포함 문서는 외부 모델에 본문을 넣지 않는다. 로컬 단계(작업 흐름 2·3단계)로만 처리하거나,
      가린(마스킹) 사본만 보낸다.
- [ ] 무엇을(파일 목록), 어디로(서비스), 왜 보내는지 Claude가 말했고 사용자가 확인했다.

## 2. 보낼 때

- 필요한 부분만 보낸다: 후보 쌍의 해당 문서, 또는 발췌. 전체 묶음을 통째로 보내지 않는다.
- 가린 사본은 원본과 다른 폴더에 두고, 가린 규칙(무엇을 어떻게 바꿨는지)을 기록한다.
- 계정 정보, 키, 내부 시스템 주소는 어떤 경우에도 넣지 않는다.

## 3. 보낸 뒤

- 전송 기록을 남긴다: 날짜, 서비스, 파일 목록, 승인한 사람. (`<RUNTIME_DIR>/DocSimilarity/sent-log.csv`)
- 외부 결과물은 검증 전까지 초안으로만 다룬다.

## AI에게 (instructions)

- Before the first send of any file in a batch, state the files, the service and the purpose, and wait for the user's
  OK. Record each send in the sent log.
- If classification is unknown, treat the file as non-public: local steps only.
