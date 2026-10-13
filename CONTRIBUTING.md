# Contributing

Use Conventional Commits, for example:

- `feat(recovery): support an additional local installation layout`
- `fix(saves): preserve the previous valid snapshot on failure`
- `test(publication): reject staged binary payloads`
- `docs: clarify Unity migration prerequisites`

Keep changes focused. Run the checks in the README before submitting a change.
Add newly reviewed files to `public-files.json`, explaining their origin there
and in `docs/provenance.md`. The manifest is an explicit review boundary, not an
automatically generated list to accept without inspection.

Use synthetic fixtures. Do not attach game DLLs, recovered source, media,
serialized assets, credentials, signing profiles, device identifiers, or raw
Unity/device logs to commits, issues, PRs, or Actions artifacts. Summarize local
results and strip personal paths from diagnostic excerpts.

The publication check also scans historical commits. Fixing the current file
does not remove an earlier committed payload. If sensitive content was committed,
stop before pushing and follow `SECURITY.md`; do not merely add another cleanup
commit. Do not force-push or rewrite shared history without maintainer coordination.
