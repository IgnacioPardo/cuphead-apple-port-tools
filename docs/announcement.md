# Announcement copy

## Short post

I've published the original tooling from my Cuphead Apple Silicon / Apple TV port
experiment: recovery scripts, save adapters, and Unity build/audit helpers. MIT
licensed. Bring your own game files; the complete rebuild pipeline is still in progress.

https://github.com/IgnacioPardo/cuphead-apple-port-tools

## Longer post

I've published Cuphead Apple Port Tools, the original tooling developed while
rebuilding my local Cuphead installation for Apple Silicon macOS and Apple TV.

The private experiment has working native ARM64 players using Unity IL2CPP and
Metal. This repository shares the recovery scripts, original save adapters,
build/audit helpers, tests, and a plan for completing the local migration workflow.

It's an experimental tooling release, not a downloadable game or a one-command
port. You'll need your own game files and development tools. Game source, assets,
DLLs, and compiled players aren't included. The original tooling is MIT licensed.

REA helped inspect the managed assemblies during recovery. I've also linked
Apple's Game Porting Toolkit as a resource for porting guidance and Metal tools.

- Repository: https://github.com/IgnacioPardo/cuphead-apple-port-tools
- Release: https://github.com/IgnacioPardo/cuphead-apple-port-tools/releases/tag/v0.1.0
- REA: https://github.com/morluto/rea
- Apple Game Porting Toolkit: https://developer.apple.com/games/game-porting-toolkit/
