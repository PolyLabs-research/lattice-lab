// The website's contact form (site/src/contact.html) posts here. Deployed as a web app from
// contact@polylabs-research.net, it emails each message to that inbox with Reply-To set to the
// sender, so replying in Gmail answers them. Setup is in site/README.md.

const TO = 'contact@polylabs-research.net';
const PER_HOUR = 30;   // at most this many emails an hour, whoever is sending

function doPost(e) {
  const p = e.parameter || {};
  // Bots fill in the hidden "website" field, or post faster than a person can type. Tell them it
  // worked, so they have nothing to learn from.
  if (p.website || Number(p.t || 0) < 3000) return reply_(true);

  const line = s => String(s || '').replace(/[\r\n]+/g, ' ').trim();
  const name = line(p.name).slice(0, 200);
  const email = line(p.email).slice(0, 200);
  const message = String(p.message || '').trim().slice(0, 10000);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return reply_(false, 'email');
  if (!message) return reply_(false, 'message');

  const cache = CacheService.getScriptCache();
  const hour = 'sent-' + Math.floor(Date.now() / 3600000);
  const sent = Number(cache.get(hour) || 0);
  if (sent >= PER_HOUR) return reply_(false, 'busy');
  cache.put(hour, String(sent + 1), 3600);

  try {
    MailApp.sendEmail({
      to: TO,
      replyTo: email,
      name: 'PolyLabs website',
      subject: 'Website message from ' + (name || email),
      body: 'From: ' + (name ? name + ' <' + email + '>' : email) + '\n\n' + message,
    });
  } catch (err) {
    return reply_(false, 'send');
  }
  return reply_(true);
}

function reply_(ok, error) {
  return ContentService.createTextOutput(JSON.stringify({ ok: ok, error: error || null }))
    .setMimeType(ContentService.MimeType.JSON);
}
