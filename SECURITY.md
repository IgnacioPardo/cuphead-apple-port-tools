# Security and publication incidents

Use GitHub private vulnerability reporting if the repository has it enabled.
Otherwise contact the maintainer through an established private channel before
sharing sensitive details. Do not open a public issue containing a credential,
game payload, local path, or device record.

If you discover a credential, avoid testing it. Report the affected path and
revision without the value; its owner decides whether revocation or rotation is
necessary. Do not attempt to rotate credentials belonging to the game's publisher.

For accidental publication, coordinate history and hosting cleanup with the
maintainer. Removing a file from the latest commit does not remove past copies,
forks, cached views, release assets, LFS objects, or Actions logs.

Recovery commands process local files and invoke explicitly supplied external
tools. They do not launch the game. Use inputs and tools you trust, and keep the
private workspace outside this repository. The publication scanner covers
working/index content and local Git refs; it does not inspect un-fetched remote
refs, remote artifacts, or prove that arbitrary text is free of third-party content.
