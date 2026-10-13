# Third-party content and dependencies

Only original code and documentation are distributed by this repository.
The MIT license does not apply to inputs, extracted output, development tools,
SDKs, or middleware obtained separately. No vendor license is replaced by MIT.

| Component | Relationship to this repository | Distribution here |
| --- | --- | --- |
| Cuphead / Studio MDHR | User-supplied game input; recovered code and content remain local | None |
| ILSpy / ilspycmd 9.1.0.7988 | External command used for managed recovery | None |
| .NET SDK 8 | External compiler/runtime used for source checks and tests | None |
| AssetRipper 2.0.0 | Optional external exporter controlled over its local HTTP API | None |
| Unity 6000.6.5f1, UGUI, TextMeshPro | External Editor, packages, references, and build modules | None |
| Rewired | Optional integration references APIs from the user's local dependency | No DLLs or recovered source |
| GOG Galaxy / Steamworks | May occur in user-owned game inputs; local-service adapter does not implement online services | No SDKs, DLLs, or credentials |
| Apple Xcode / SDKs | Required for native signing and device builds | None |
| GitHub Actions checkout/setup-python/setup-dotnet | CI actions fetched by GitHub at pinned revisions | No vendored action code |

Upstream references:

- [ILSpy](https://github.com/icsharpcode/ILSpy)
- [.NET](https://github.com/dotnet/sdk)
- [AssetRipper](https://github.com/AssetRipper/AssetRipper)
- [Unity terms](https://unity.com/legal)
- [Rewired licensing FAQ](https://guavaman.com/projects/rewired/docs/FAQ.html)
- [Unity Asset Store EULA](https://unity.com/legal/as-terms)

Consult the terms attached to the exact tools and dependencies you obtain.
Owning a game copy does not by itself document permission to publish its contents.
Do not add third-party source, packages, logos, or binary dependencies without
reviewing distribution rights and providing the required notices.
