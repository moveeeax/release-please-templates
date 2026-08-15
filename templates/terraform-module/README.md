# Terraform module template

`release-type: terraform-module` bumps the version referenced in the module's
`README.md` usage block and `versions.tf` metadata, and tags `vX.Y.Z` so
consumers can pin `?ref=vX.Y.Z` or use the Terraform Registry.

Keep breaking input/output changes behind a `feat!:` or a `BREAKING CHANGE:`
footer — that is what turns into a major bump once you are past `v1.0.0`.
