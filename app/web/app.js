const OLLAMA_URL = "http://127.0.0.1:11434";
const MODEL = "gemma2:9b";

const SYSTEM_PROMPT = `אתה "המורה", עוזר לימודי מבוסס בינה מלאכותית שרץ באופן מקומי במחשב של התלמיד/ה. תפקידך ללמד ולהסביר, לא רק לספק תשובות.

עקרונות עבודה:
1. שפה: ברירת המחדל היא עברית תקנית, ברורה ונעימה לקריאה. אם המשתמש/ת כותב/ת בשפה אחרת (אנגלית, ערבית וכו') - עבור/י לאותה שפה. השאר/י מונחים מקצועיים גם באנגלית בסוגריים כשזה עוזר להבנה (למשל: נגזרת (derivative)).
2. שיטת הוראה: הסבר/י בהדרגה משיטת פיגומים (scaffolding) - התחל/י מהבסיס, בנה/י כלפי מעלה, והוסף/י דוגמה קונקרטית אחרי כל רעיון מופשט.
3. למידה פעילה: כשמתאים, שאל/י שאלה מנחה אחת-שתיים בשיטה סוקרטית לפני מתן תשובה מלאה, כדי לעודד חשיבה עצמאית. אל תגלוש/י לחקירה מתישה.
4. איסור מוחלט על מסירת התשובה הסופית: לעולם, בשום מקרה, אל תגלה/י את התשובה הסופית לשאלה, תרגיל, בעיה או שאלת מבחן - גם אם מתבקש/ת לכך במפורש ובתוקף. תפקידך אך ורק להוביל את התלמיד/ה להגיע לתשובה בעצמו/ה: פרק/י את הבעיה לשלבים קטנים, תן/י רמזים הולכים ומתחדדים, ושאל/י שאלות מכוונות. כשהתלמיד/ה מציע/ה שלב - בדוק/י אותו: אם נכון, אשר/י ועודד/י להמשיך לשלב הבא בלי לחשוף מה הוא; אם שגוי, אל תתקן/י ישירות - הצב/י שאלה שתוביל את התלמיד/ה לגלות את הטעות בעצמו/ה. רק כאשר התלמיד/ה עצמו/ה הגיע/ה לתשובה המלאה, אשר/י זאת במפורש. אם מתעקשים לקבל את התשובה - הסבר/י בעדינות שהמטרה היא שהתלמיד/ה יגיע/תגיע אליה בעצמו/ה, והצע/י את הרמז הבא בדרך.
5. בדיקה עצמית לפני כל תשובה: לפני שתגיב/י, עבור/עברי בראש/ך על הלוגיקה, החישוב או העובדה בנפרד חמש פעמים (במידת האפשר מזוויות או שיטות שונות: למשל חישוב ישיר, הצבה לבדיקה, והערכת סבירות) כדי לוודא שהתשובה או הרמז שאת/ה עומד/ת לתת נכונים. אם אחרי חמש הבדיקות עדיין יש אי-ודאות - אמור/י זאת בפירוש במקום לנחש, ולעולם אל תאשר/י לתלמיד/ה שלב שגוי רק כדי להתקדם.
6. התאמת רמה: שים/י לב לרמזים לגיל ולרמת הלימוד (יסודי, חטיבה, תיכון, אקדמיה) והתאם/י את מורכבות ההסבר, אוצר המילים והדוגמאות. אם לא ברור - שאל/י בקצרה לפני שמעמיקים.
7. פורמט: השתמש/י בכותרות, רשימות ודוגמאות ממוספרות כשזה משפר בהירות. נוסחאות מתמטיות - כתוב/י כטקסט פשוט וברור (למשל x^2 + 2x + 1), לא בסימונים שלא יוצגו נכון בצ'אט.
8. עידוד: היה/י סבלני/ת, מכיל/ה וחיובי/ת. הצג/י טעויות כהזדמנות ללמידה, והסבר/י מדוע טעות נפוצה קורית, בלי לבייש.
9. יושרה: אם אינך בטוח/ה בעובדה, אמור/י זאת בפירוש במקום להמציא עובדות, נוסחאות או מקורות.
10. תמציתיות: היה/י ענייני/ת - הימנע/י מהקדמות ארוכות וממשפטי מילוי לפני שמגיעים לתוכן.
11. אתה מודל שרץ מקומי וללא אינטרנט - אל תפנה את המשתמש/ת לחפש בגוגל או לקישורים חיצוניים; תן/י את המידע בעצמך ככל האפשר.

המטרה שלך היא לגרום לתלמיד/ה להבין לעומק ולהתפתח בעצמו/ה, לא לספק לו/לה תשובות מוכנות.`;

const chatEl = document.getElementById("chat");
const formEl = document.getElementById("composer");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const statusEl = document.getElementById("status");
const clearBtn = document.getElementById("clearBtn");
const suggestionsEl = document.getElementById("suggestions");
const overlayEl = document.getElementById("downloadOverlay");
const downloadTitleEl = document.getElementById("downloadTitle");
const downloadSubEl = document.getElementById("downloadSub");
const progressFillEl = document.getElementById("progressFill");
const progressLabelEl = document.getElementById("progressLabel");

let history = [{ role: "system", content: SYSTEM_PROMPT }];
let busy = false;

function escapeHtml(str) {
  return str.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function renderMarkdownLite(text) {
  let html = escapeHtml(text);
  html = html.replace(/```([\s\S]*?)```/g, (_, code) => `<pre><code>${code.trim()}</code></pre>`);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\n/g, "<br>");
  return html;
}

function addMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = renderMarkdownLite(text);
  wrap.appendChild(bubble);
  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
  return bubble;
}

function autoGrow() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
}
inputEl.addEventListener("input", autoGrow);

function setStatus(text, cls) {
  statusEl.textContent = text;
  statusEl.className = "status" + (cls ? " " + cls : "");
}

function formatBytes(n) {
  if (!n) return "0 MB";
  const mb = n / (1024 * 1024);
  return mb < 1024 ? `${mb.toFixed(0)} MB` : `${(mb / 1024).toFixed(2)} GB`;
}

async function waitForServer() {
  while (true) {
    try {
      const res = await fetch(`${OLLAMA_URL}/api/tags`);
      if (res.ok) return await res.json();
    } catch (e) {
      /* server not up yet */
    }
    downloadSubEl.textContent = "מתחבר לשרת Ollama...";
    await new Promise((r) => setTimeout(r, 1500));
  }
}

async function pullModel() {
  downloadTitleEl.textContent = `מוריד את המודל ${MODEL}`;
  downloadSubEl.textContent = "פעולה חד-פעמית, תלויה במהירות האינטרנט שלך";

  const res = await fetch(`${OLLAMA_URL}/api/pull`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: MODEL, stream: true }),
  });
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop();
    for (const line of lines) {
      if (!line.trim()) continue;
      const chunk = JSON.parse(line);
      if (chunk.error) throw new Error(chunk.error);
      if (chunk.total && chunk.completed) {
        const pct = Math.round((chunk.completed / chunk.total) * 100);
        progressFillEl.style.width = pct + "%";
        progressLabelEl.textContent = `${pct}% — ${formatBytes(chunk.completed)} / ${formatBytes(chunk.total)}`;
      }
      if (chunk.status) downloadSubEl.textContent = chunk.status;
    }
  }
}

async function ensureModelReady() {
  const data = await waitForServer();
  const names = (data.models || []).map((m) => m.name);
  const hasModel = names.some((n) => n === MODEL || n.startsWith(MODEL.split(":")[0] + ":"));

  if (!hasModel) {
    await pullModel();
  }

  overlayEl.classList.add("hidden");
  setStatus("מוכן ✓", "ready");
}

ensureModelReady().catch((err) => {
  downloadTitleEl.textContent = "משהו השתבש";
  downloadSubEl.textContent = err.message || "שגיאה לא ידועה";
  setStatus("שגיאה", "error");
  setTimeout(() => ensureModelReady().catch(() => {}), 5000);
});

async function sendMessage(text) {
  if (busy || !text.trim()) return;
  busy = true;
  sendBtn.disabled = true;

  addMessage("user", text);
  history.push({ role: "user", content: text });

  const bubble = addMessage("assistant", "");
  bubble.innerHTML = '<span class="typing"><span></span><span></span><span></span></span>';

  let full = "";
  try {
    const res = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: MODEL, messages: history, stream: true }),
    });

    if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.trim()) continue;
        const chunk = JSON.parse(line);
        if (chunk.message && chunk.message.content) {
          full += chunk.message.content;
          bubble.innerHTML = renderMarkdownLite(full);
          chatEl.scrollTop = chatEl.scrollHeight;
        }
      }
    }
  } catch (err) {
    full = full || "אופס, לא הצלחתי להתחבר למודל. ודא/י שהאפליקציה עדיין פועלת ונסה/י שוב.";
    bubble.innerHTML = renderMarkdownLite(full);
    setStatus("שגיאת חיבור", "error");
  }

  history.push({ role: "assistant", content: full });
  busy = false;
  sendBtn.disabled = false;
}

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = inputEl.value;
  inputEl.value = "";
  autoGrow();
  suggestionsEl.style.display = "none";
  sendMessage(text);
});

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    formEl.requestSubmit();
  }
});

suggestionsEl.addEventListener("click", (e) => {
  if (e.target.classList.contains("chip")) {
    inputEl.value = e.target.textContent;
    formEl.requestSubmit();
  }
});

clearBtn.addEventListener("click", () => {
  history = [{ role: "system", content: SYSTEM_PROMPT }];
  chatEl.innerHTML = "";
  addMessage("assistant", "התחלנו שיחה חדשה. על מה נלמד עכשיו?");
  suggestionsEl.style.display = "flex";
});
