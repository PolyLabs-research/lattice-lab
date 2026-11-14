# The website: polylabs-research.net

A static site, with no server code and no build step needed to deploy it: `public/` is the whole
site. It covers every PolyLabs Research programme. lattice-lab has a section of its own, whose
interactive figures compute in the browser from `public/assets/data.js`; each other programme has
one page.

```
site/
  build_data.py     writes public/assets/data.js from lattice-lab's records and code
  build_pages.py    wraps each body in src/ in the shared head, header and footer, and writes
                    sitemap.xml and robots.txt; its PAGES table gives each page's title,
                    description and programme, NAV the header's programmes and SUBNAV
                    lattice-lab's own row of pages
  build_icons.py    draws the mark as favicon.ico, apple-touch-icon.png and assets/mark-512.png
  og-card.html      the picture a shared link shows; its head says how to render assets/og.png
  preview.py        serves public/ on this machine the way Firebase does
  src/*.html        the page bodies
  public/           what gets deployed
    index.html                       the home page: every programme, and how we work
    lattice.html, model.html, parity.html, atlas.html, settling.html, proofs.html, codes.html,
    census.html                      lattice-lab's section
    tiny-alphazero.html, reckoner.html, protocell.html, organisation.html, corpus-lens.html
                                     one page per programme
    contact.html, 404.html
    sitemap.xml, robots.txt, favicon.ico, apple-touch-icon.png
    assets/site.css, assets/lib.js (shared maths, SHA-256, charts), assets/fonts/
    assets/js/<page>.js              each page's figures
    assets/img/                      screenshots, taken from the_organisation's docs/
    assets/og.png, assets/mark-512.png   the shared-link picture and the logo
  apps-script/      the contact form's backend (Google Apps Script)
  firebase.json     Firebase Hosting configuration
```

Until 14 November 2026 the home page was lattice-lab's; that page is now `lattice.html`, and every
other lattice-lab page kept its address.

## The other programmes' pages

The pages for Tiny AlphaZero, Reckoner, Protocell, the_organisation and Corpus Lens are written by
hand from those projects' own records, and are not rebuilt from them. Each chart's numbers are in
its `assets/js/<page>.js`, with the record they come from named in a comment. Update a page when
its programme records something new, and keep the home page's "Latest on the record" list and
cards in step.

- Tiny AlphaZero, Reckoner and the_organisation are public, and their pages link into them on
  GitHub at `main`.
- Protocell and Corpus Lens are private: their pages describe them and link nowhere.
- Corpus Lens's rules keep its owner's documents, and anything measured on them, out of any demo.
  Its page uses only synthetic and public data, and its citation-gate demonstration runs on an
  invented page.
- None of the pages names a person, a pod, a machine's paths or an account's spend.

## Rebuilding

```bash
uv run --no-sync python site/build_data.py     # after new records, pilots or proofs
uv run --no-sync python site/build_pages.py    # after editing site/src/ or the header/footer
```

Then commit `site/public/` and deploy. `build_data.py` reads only this repository. The state of
the m = 37 question on the site (the lattice page's card, the fourth pilot's row on the model page
and its account on the atlas page) is the `PILOT37` dictionary in `build_data.py`, edited by
hand. The rest of the m = 37 section, on the seventh pilot and rule 4850, is in
`src/atlas.html`.

Before deploying, check the pages locally:

```bash
python3 site/preview.py     # then open http://localhost:8000
```

`preview.py` serves `/census` from `census.html` and redirects `/census.html` to it, as Firebase's
`cleanUrls` does. The pages link to each other in that short form, so plain
`python3 -m http.server` would not follow the links.

## What search engines read

`build_pages.py` writes all of it, from the `PAGES` table:

- **A title and a description for each page.** The title names the subject in the words someone
  would search for, and the site's name follows it. A description over about 160 characters is
  cut off in a search result, and the builder says so when one is.
- **One address for each page.** Each page names its own address (`rel="canonical"`), without
  `.html`, and the links between pages use the same form, so no link goes through a redirect.
  Bodies in `src/` still write `census.html`; the builder shortens them, and `pageHref` in
  `lib.js` does the same for a link a script builds.
- **`sitemap.xml` and `robots.txt`**, listing every page but the 404 page.
- **What a shared link shows:** the Open Graph and Twitter tags, with `assets/og.png` as the
  picture. To change the picture, edit `og-card.html` and render it as its head says.
- **Structured data** (schema.org, as JSON-LD): the organisation and the site on the home page,
  and on every other page what the page is and its trail from the home page.

After the first deploy with these, add the site in
[Google Search Console](https://search.google.com/search-console) (a DNS TXT record at GoDaddy
proves the domain is yours) and give it `https://polylabs-research.net/sitemap.xml`. Bing's
Webmaster Tools can import the site from there.

A page's charts are drawn at the width of their box, and a table marked `class="stack"` becomes
a list of blocks on a phone. When adding a chart, give its box the class `fit`, draw it with
`chartWidth`, and give it a table of its numbers with `numbersTable` (all in `lib.js`). The
site's green and red are close to each other for a red-green colour-blind reader, so a chart
never tells two things apart by those colours alone: it uses a shape, a dash or a label as well.

lattice-lab is public, and the site links into it on GitHub at `main`: the footer on every page,
the lattice page, the model page's ledger and pilot table, the proofs page's library and the codes
page's sources. Moving or renaming a linked file on `main` breaks its link, so search `site/src/`
and `build_pages.py` for its path first. Kepler and LatticeLife are public and are linked too.

## The contact form

`contact.html` posts its form to a Google Apps Script web app, `apps-script/Code.gs`, which
emails each message to contact@polylabs-research.net with Reply-To set to the sender. It runs in
the Google Workspace account, not in the Cloud project, and costs nothing. It ignores forms with
the hidden `website` field filled in or sent within 3 seconds of the page opening, and sends at
most 30 emails an hour.

To set it up, or after changing `Code.gs`:

1. Signed in as contact@polylabs-research.net, open https://script.google.com, make a new
   project, and paste in `Code.gs` (replacing what is there).
2. **Deploy**, then **New deployment**, type **Web app**: execute as **Me**, access **Anyone**.
   Authorise it to send email as you.
3. Put the web app's address (`https://script.google.com/macros/s/…/exec`) in the form's
   `data-endpoint` in `src/contact.html`, rebuild the pages and deploy.

After a later change to `Code.gs`, use **Manage deployments** and edit the existing deployment
to a new version, so the address stays the same.

## Deploying on Google Cloud

### In use: Firebase Hosting

Firebase Hosting is Google Cloud's static hosting. It serves from a global CDN, issues the TLS
certificate for a custom domain itself, and is free at this site's size.

The site is hosted in the Google Cloud project `polylabs-512110` (billed to the Poly-Labs
account, which has a GBP 5 budget alert on this project). Its default address is
`https://polylabs-512110.web.app`. `site/.firebaserc` names the project, so no `--project` flag
is needed.

Deploy from `site/`, where `firebase.json` is:

```bash
npm install -g firebase-tools     # once
cd site
firebase hosting:channel:deploy preview --expires 1d   # optional: a private preview URL first
firebase deploy --only hosting
```

The CLI signs in with `firebase login`, or uses gcloud's application-default credentials if
`GOOGLE_CLOUD_QUOTA_PROJECT=polylabs-512110` is set. Earlier versions stay in the console's
release history, and one click rolls back.

The fonts (IBM Plex Mono, STIX Two Text) are served from `public/assets/fonts/`, not Google
Fonts, so a visit makes no third-party requests. The one exception is sending the contact form,
which posts to Google Apps Script.

#### The domain

`polylabs-research.net` and `www.polylabs-research.net` (a redirect to the bare domain) are
registered on the Firebase site. Their DNS is at GoDaddy: **My Products**, then **Domains**,
then **polylabs-research.net**, then **DNS**. The records Firebase needs:

| Type  | Name  | Value                          |
|-------|-------|--------------------------------|
| A     | `@`   | `199.36.158.100`               |
| TXT   | `@`   | `hosting-site=polylabs-512110` |
| CNAME | `www` | `polylabs-512110.web.app`      |

GoDaddy's two parked **A** records for `@` must be deleted, and its default `www` CNAME (to
`@`) replaced. Firebase then issues the certificate by itself, and the console's Hosting page
shows each domain as **Connected**.

### Alternative: a Cloud Storage bucket behind a load balancer

This route uses only core Google Cloud services. It costs more, about USD 18 a month for the
load balancer's forwarding rule, and needs more setup.

```bash
PROJECT=YOUR_PROJECT_ID
BUCKET=polylabs-research-site
gcloud config set project $PROJECT

gcloud storage buckets create gs://$BUCKET --location=US --uniform-bucket-level-access
gcloud storage buckets update gs://$BUCKET --web-main-page-suffix=index.html --web-error-page=404.html
gcloud storage buckets add-iam-policy-binding gs://$BUCKET --member=allUsers --role=roles/storage.objectViewer
gcloud storage rsync site/public gs://$BUCKET --recursive --delete-unmatched-destination-objects

gcloud compute backend-buckets create site-backend --gcs-bucket-name=$BUCKET --enable-cdn
gcloud compute url-maps create site-map --default-backend-bucket=site-backend
gcloud compute ssl-certificates create site-cert --global \
  --domains=polylabs-research.net,www.polylabs-research.net
gcloud compute target-https-proxies create site-proxy --url-map=site-map --ssl-certificates=site-cert
gcloud compute addresses create site-ip --global
gcloud compute forwarding-rules create site-https --global --target-https-proxy=site-proxy \
  --address=site-ip --ports=443
gcloud compute addresses describe site-ip --global --format='value(address)'   # the IP for DNS
```

In GoDaddy's DNS, point an **A** record for `@` and one for `www` at that IP. The certificate
becomes active once DNS resolves, which can take up to an hour or so. Plain `http://` needs a
second forwarding rule on port 80 with a redirect; Firebase does this by itself.

The bucket serves pages at their `.html` names, so build the pages for it with
`python site/build_pages.py --html-links`, which keeps `.html` on the links between pages. Each
page's canonical address, and the sitemap, would still name the short form, so change `url()` in
`build_pages.py` as well if the site ever moves to this route.
