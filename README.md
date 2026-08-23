# Jaxie's Art

A gallery of Jaxie's drawings, organized by year / month / week, published
as a password-protected static site.

**Live site:** https://jaxie-art.pages.dev/ (password required — ask Andreas)

## How it works

- Drawings live in `images/YYYY/MM/DD/`, one dated folder per day.
- `scripts/build_manifest.py` scans that folder and generates `manifest.json`,
  which the site reads to render the gallery (grouped by week, filterable
  by year/month/week).
- Every push to `master` triggers a GitHub Action that rebuilds the
  manifest and deploys to Cloudflare Pages.
- The whole site is gated behind HTTP Basic Auth via a Cloudflare Pages
  Function (`functions/_middleware.js`), configured with multiple
  username/password pairs stored in the `SITE_USERS` secret.

## Adding new drawings

**Automatically (the normal way):** drawings placed in the `Pictures/Jaxie-drawings`
folder on OneDrive are picked up automatically. A scheduled GitHub Action
(`sync-onedrive.yml`) checks that folder periodically, copies new files into
the right `images/YYYY/MM/DD/` folder (using the original file date), and
pushes — which triggers the deploy above. Each file is only ever imported
once, tracked in `.onedrive-sync-ledger.txt`, so removing it from the
gallery later doesn't bring it back.

**Manually:** navigate to
`github.com/andlo/jaxie-art/upload/master/images/YYYY/MM/DD` in a browser
and drop files in — GitHub creates the folder as part of the commit if it
doesn't exist yet. No local clone needed. The displayed date comes from
the folder path, not the file's own timestamp, so this works fine even
though browser uploads don't preserve original file dates.

## Removing a drawing

Click "Request removal" on any drawing in the gallery. This opens a
pre-filled GitHub issue with the file path.

- If **you** (a trusted account, see the workflow files) open it, the image
  is deleted automatically and the issue is closed.
- If anyone else opens it, the issue is flagged for manual review instead —
  add the `approved` label to it to trigger the actual removal. Only
  repository collaborators can add labels, so this can't be triggered by a
  stranger.

## Repository structure

```
images/YYYY/MM/DD/*.png        published drawings, one dated folder per day
archive-original-import/       backup of the original bulk import — NOT
                                published (excluded from every deploy)
manifest.json                  generated — do not edit by hand
scripts/build_manifest.py      builds manifest.json from images/
scripts/sync_onedrive.py       imports new files from OneDrive
functions/_middleware.js       password gate (Cloudflare Pages Function)
.github/workflows/
  deploy.yml                   build manifest + deploy to Cloudflare Pages
  sync-onedrive.yml            scheduled OneDrive import (every 15 min)
  handle-removal.yml           auto-removal for trusted requesters
  execute-approved-removal.yml runs once a removal request is labeled "approved"
```

## License

Drawings are published under **CC BY-NC-ND 4.0** (see `LICENSE`) — you're
welcome to view and share them with credit, but not modify them or use
them commercially. The gallery's own code is available under a permissive
license (see `LICENSE-CODE`).
