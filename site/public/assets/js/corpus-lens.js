// Corpus Lens: a sketch of the citation gate's rule, run on an invented page. The rule as published
// (backend/agent/tools/write.py and normalise.py, private repository): the agent gives a quote, the
// server finds it; a quote must be at least 20 characters and occur exactly once on its page;
// matching forgives typography only (Unicode forms, curly quotes, dashes, spacing), never case or
// punctuation; what is stored is the page's own slice at the offsets the server found.

const PAGE = "Minutes of the board meeting held on 14 March 2024.\n\n" +
  "The board approved the transfer of £40,000 to Northgate Example Ltd, subject to a second " +
  "signature. The finance director’s note said the invoice had not yet been received. The chair " +
  "asked that the invoice be produced before any payment is made, and that any further payment " +
  "be subject to a second signature.";

const PRESETS = [
  "approved the transfer of £40,000 to Northgate Example Ltd",
  "the board agreed to pay Northgate £40,000",
  "approved the transfer of £40,000 before any payment is made",
  "subject to a second signature",
  "the invoice",
  "director's note said the invoice had  not yet been received",
];
const MIN_QUOTE_CHARS = 20;

// The normalised view of a text, and for each of its characters the raw index it came from.
function view(raw) {
  let text = "";
  const from = [];
  let lastSpace = false;
  for (let i = 0; i < raw.length; ) {
    const cp = raw.codePointAt(i), ch = String.fromCodePoint(cp), width = ch.length;
    let out = ch.normalize("NFKC")
      .replace(/[‘’‚‛′]/g, "'")
      .replace(/[“”„‟″]/g, '"')
      .replace(/[‐‑‒–—―−]/g, "-");
    if (/^\s+$/.test(out)) {
      if (!lastSpace) { text += " "; from.push(i); }
      lastSpace = true;
    } else {
      for (const c of out) { text += c; from.push(i); }
      lastSpace = false;
    }
    i += width;
  }
  from.push(raw.length);
  return { text, from };
}
const PV = view(PAGE);

function occurrences(hay, needle) {
  const at = [];
  for (let i = hay.indexOf(needle); i >= 0; i = hay.indexOf(needle, i + 1)) at.push(i);
  return at;
}

const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
function showPage(start, end) {
  const el = $("gate-page");
  if (start == null) { el.innerHTML = esc(PAGE); return; }
  el.innerHTML = esc(PAGE.slice(0, start)) + `<mark style="background: var(--gold-soft); color: var(--ink)">` +
    esc(PAGE.slice(start, end)) + "</mark>" + esc(PAGE.slice(end));
}

function judge() {
  const q = $("gate-quote").value, verdict = $("gate-verdict"), stored = $("gate-stored");
  const nq = view(q).text.trim();
  const refuse = why => {
    verdict.innerHTML = `<span class="badge bad">refused</span> ${why}`;
    stored.textContent = "nothing";
    showPage(null);
  };
  if (!nq) { verdict.textContent = "…"; stored.textContent = ""; showPage(null); return; }
  if (nq.length < MIN_QUOTE_CHARS) return refuse(`${nq.length} characters; a quote this short matches too much to prove anything (the floor is ${MIN_QUOTE_CHARS}).`);
  const at = occurrences(PV.text, nq);
  if (at.length === 0) return refuse("these words are not on the page. A paraphrase, an invention or a quote stitched from two places all fail the same way.");
  if (at.length > 1) return refuse(`it occurs ${at.length} times on the page, so it does not say which passage is meant.`);
  const start = PV.from[at[0]], end = PV.from[at[0] + nq.length];
  verdict.innerHTML = `<span class="badge ok">accepted</span> found once, at characters ${start} to ${end}.`;
  stored.textContent = `“${PAGE.slice(start, end)}”: the page's own characters${PAGE.slice(start, end) === q.trim() ? "" : ", not the agent's"}.`;
  showPage(start, end);
}

$("gate-quote").addEventListener("input", judge);
for (const b of document.querySelectorAll("[data-q]")) {
  b.addEventListener("click", () => { $("gate-quote").value = PRESETS[Number(b.dataset.q)]; judge(); });
}
$("gate-quote").value = PRESETS[0];
judge();
