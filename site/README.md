# The website: polylabs-research.net

A static site, with no server code and no build step needed to deploy it: `public/` is the whole
site. The interactive figures compute in the browser from `public/assets/data.js`.

```
site/
  build_data.py     writes public/assets/data.js from lattice-lab's records and code
  build_pages.py    wraps each body in src/ in the shared head, header and footer
  src/*.html        the page bodies
  public/           what gets deployed
    index.html, model.html, parity.html, atlas.html, settling.html, proofs.html, 404.html
    assets/site.css, assets/lib.js (shared maths, SHA-256, charts), assets/js/<page>.js
  firebase.json     Firebase Hosting configuration
```

## Rebuilding

```bash
uv run --no-sync python site/build_data.py     # after new records, pilots or proofs
uv run --no-sync python site/build_pages.py    # after editing site/src/ or the header/footer
```

Then commit `site/public/` and deploy. `build_data.py` reads only this repository. The fourth
pilot's status on the site is the `PILOT37` dictionary in `build_data.py`, edited by hand.

Before deploying, check the pages locally:

```bash
cd site/public && python3 -m http.server 8000     # then open http://localhost:8000
```

Nothing on the site may link into lattice-lab on GitHub while that repository is private; those
links would 404 for visitors. Kepler and LatticeLife are public and are linked.

## Deploying on Google Cloud

### Recommended: Firebase Hosting

Firebase Hosting is Google Cloud's static hosting. It serves from a global CDN, issues the TLS
certificate for a custom domain itself, and is free at this site's size. It works with an existing
Google Cloud project.

1. Install the CLI and sign in:
   ```bash
   npm install -g firebase-tools
   firebase login
   ```
2. Add Firebase to the Google Cloud project you already use: in the
   [Firebase console](https://console.firebase.google.com/), choose **Add project** and pick
   the existing Google Cloud project from the list.
3. Deploy from `site/`, where `firebase.json` is:
   ```bash
   cd site
   firebase deploy --only hosting --project YOUR_PROJECT_ID
   ```
   The site is now live at `https://YOUR_PROJECT_ID.web.app`.
4. Connect the domain: in the Firebase console, open **Hosting**, then **Add custom domain**,
   and enter `polylabs-research.net`. Add `www.polylabs-research.net` too, set to redirect to
   the bare domain. Firebase shows the DNS records to create.
5. In GoDaddy, open **My Products**, then **Domains**, then **polylabs-research.net**, then
   **DNS**, and:
   - add the **TXT** record Firebase gives, for verification;
   - delete GoDaddy's default **A** record for `@` (the "Parked" one), and add the **A**
     records Firebase gives for `@`;
   - for `www`, replace the default CNAME with the record Firebase gives.

   DNS usually takes minutes but can take a few hours. Firebase then issues the certificate by
   itself, and the console shows the domain as **Connected**.

To redeploy after a change, run `firebase deploy --only hosting --project YOUR_PROJECT_ID`
again. Earlier versions stay in the console's release history, and one click rolls back.

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

The bucket serves pages at their `.html` names; the site's links use those names, so both
routes work unchanged.
