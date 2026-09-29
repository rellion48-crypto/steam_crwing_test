// Vercel 서버 함수: 화면에서 조건 두 개를 받아, 후보를 골라 Gemini 에게 한 개를 추천받는다.
// 열쇠(GEMINI_API_KEY)는 이 서버 안에서만 읽고, 화면으로는 절대 내보내지 않는다.

// 화면과 같은 data.json 을 서버에서도 읽는다(후보는 서버가 직접 고르므로 화면이 보낸 목록을 믿지 않는다)
const items = require("../data/data.json");

// 공식 문서(ai.google.dev/gemini-api/docs/models)의 안정판 중 가장 빠르고 저렴한 모델
const MODEL = "gemini-3.5-flash-lite";
// 공식 문서의 Interactions API 주소
const ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions";
// AI 에게 넘길 후보 최대 개수
const MAX_CANDIDATES = 5;
// AI 응답을 기다리는 최대 시간(밀리초)
const TIMEOUT_MS = 20000;

// 정렬·예산 비교용 가격: 숫자는 그대로, "무료"는 0, 그 밖의 글씨는 맨 뒤(index.html 과 같은 규칙)
function priceKey(price) {
  if (typeof price === "number") return price;
  if (price === "무료") return 0;
  return Infinity;
}

// 화면이 보낸 칸 값을 숫자나 null(조건 없음)로 바꾼다
function toCondition(v) {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

// 두 조건을 모두 만족하는 후보를 가격 낮은 순으로 최대 5개 고른다(index.html 과 같은 규칙)
function pickCandidates(budget, minRating) {
  return items
    .filter((it) => budget === null || priceKey(it.price) <= budget)
    .filter((it) => minRating === null || (typeof it.rating === "number" && it.rating >= minRating))
    .sort((a, b) => priceKey(a.price) - priceKey(b.price))
    .slice(0, MAX_CANDIDATES)
    // AI 에게는 name · price · release_date 만 넘긴다(data.json 에 없는 값은 null)
    .map((it) => ({ name: it.name, price: it.price, release_date: it.release_date ?? null }));
}

// AI 에게 주는 규칙(시스템 지시)
const SYSTEM_INSTRUCTION = [
  "너는 게임 비교 화면의 추천 도우미다.",
  "사용자 조건과 후보 표(JSON)를 받는다. 후보 중 정확히 하나를 고른다.",
  "name 에는 고른 후보의 name 을 글자 하나 바꾸지 말고 그대로 적는다.",
  "reasons 에는 이유를 정확히 두 줄 적는다. 각 줄은 공백 포함 40자 이내의 한 문장으로 짧게 쓴다.",
  "이유에는 후보 표의 price 와 release_date 값만 숫자로 쓴다. release_date 가 null 이면 출시일은 말하지 않는다.",
  "후보 표 밖의 게임, 표에 없는 정보(장르, 평가, 인기, 품질, 할인 등)는 말하지 않는다.",
  "고르는 기준은 순서대로: 1) price 가 낮은 것(\"무료\"는 0원), 2) 같으면 표에서 앞에 있는 것.",
].join("\n");

// Gemini 응답에서 모델이 쓴 글자를 꺼낸다(공식 예시: steps[].content[].text)
function extractText(data) {
  if (typeof data.output_text === "string") return data.output_text;
  for (const step of data.steps || []) {
    if (step.type !== "model_output") continue;
    for (const c of step.content || []) {
      if (c.type === "text" && typeof c.text === "string") return c.text;
    }
  }
  return null;
}

module.exports = async (request, response) => {
  // POST 만 받는다
  if (request.method !== "POST") {
    return response.status(405).json({ status: "error" });
  }

  // 요청 본문(JSON)을 읽는다. 깨진 JSON 이면 400
  let body;
  try {
    body = request.body || {};
  } catch {
    return response.status(400).json({ status: "error" });
  }
  const budget = toCondition(body.budget);
  const minRating = toCondition(body.minRating);

  // 후보를 서버에서 직접 고른다. 0개면 AI 를 부르지 않는다
  const candidates = pickCandidates(budget, minRating);
  if (candidates.length === 0) {
    return response.status(200).json({ status: "empty" });
  }

  // 열쇠가 없으면 AI 를 부를 수 없다(화면에는 "잠시 뒤 다시" 로 보인다)
  const key = process.env.GEMINI_API_KEY;
  if (!key) {
    return response.status(200).json({ status: "unavailable" });
  }

  // AI 에게 넘길 내용: 조건 두 개와 후보 표
  const input = JSON.stringify({
    conditions: { budget_won_max: budget, min_rating: minRating },
    candidates,
  });

  // 답의 모양을 JSON 으로 고정한다(name 은 후보 이름 중 하나, reasons 는 정확히 두 줄)
  const schema = {
    type: "object",
    properties: {
      name: { type: "string", enum: candidates.map((c) => c.name) },
      reasons: { type: "array", items: { type: "string" }, minItems: 2, maxItems: 2 },
    },
    required: ["name", "reasons"],
  };

  // 시간이 너무 오래 걸리면 끊는다
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let data;
  try {
    const res = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({
        model: MODEL,
        input,
        system_instruction: SYSTEM_INSTRUCTION,
        generation_config: { temperature: 0, max_output_tokens: 512 },
        response_format: { type: "text", mime_type: "application/json", schema },
        // 이 대화를 Google 서버에 저장하지 않는다
        store: false,
      }),
      signal: controller.signal,
    });
    // 한도 초과(429) 등 실패 응답이면 "잠시 뒤 다시"
    if (!res.ok) {
      console.error("Gemini HTTP", res.status);
      return response.status(200).json({ status: "unavailable" });
    }
    data = await res.json();
  } catch (err) {
    // 네트워크 오류 · 시간 초과
    console.error("Gemini fetch failed", err.name);
    return response.status(200).json({ status: "unavailable" });
  } finally {
    clearTimeout(timer);
  }

  // 답 글자를 JSON 으로 읽는다. 못 읽으면 "잠시 뒤 다시"
  const text = extractText(data);
  let answer;
  try {
    answer = JSON.parse(text);
  } catch {
    return response.status(200).json({ status: "unavailable" });
  }

  // 이름이 후보에 글자 그대로 없거나, 이유가 두 줄이 아니면 추천을 보여 주지 않는다
  const picked = candidates.find((c) => c.name === answer.name);
  const reasons = Array.isArray(answer.reasons) ? answer.reasons.map((r) => String(r).trim()) : [];
  if (!picked || reasons.length !== 2 || reasons.some((r) => r === "")) {
    return response.status(200).json({ status: "unverified" });
  }

  return response.status(200).json({ status: "ok", name: picked.name, reasons });
};
