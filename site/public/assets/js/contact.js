// Contact: the form posts to a Google Apps Script web app (site/apps-script/Code.gs), which
// emails the message to contact@. The form's data-endpoint is the web app's /exec address.
const contactForm = $("contact-form");
const contactStatus = $("contact-status");
const contactOpened = Date.now();
const FALLBACK = "Please write to contact@polylabs-research.net instead.";

function contactSay(text, kind) {
  contactStatus.textContent = text;
  contactStatus.className = kind ? `note ${kind}` : "note";
}

contactForm.addEventListener("submit", async e => {
  e.preventDefault();
  const endpoint = contactForm.dataset.endpoint;
  if (!endpoint) { contactSay(`The form is not connected yet. ${FALLBACK}`, "bad"); return; }
  const body = new URLSearchParams(new FormData(contactForm));
  body.set("t", String(Date.now() - contactOpened));   // the script ignores forms sent within 3 s
  const button = contactForm.querySelector("button[type=submit]");
  button.disabled = true;
  contactSay("Sending…");
  try {
    const reply = await (await fetch(endpoint, { method: "POST", body })).json();
    if (!reply.ok) throw new Error(reply.error);
    contactForm.reset();
    contactSay("Sent. Thank you, we will reply to the address you gave.", "ok");
  } catch {
    contactSay(`That did not send. ${FALLBACK}`, "bad");
  } finally {
    button.disabled = false;
  }
});
