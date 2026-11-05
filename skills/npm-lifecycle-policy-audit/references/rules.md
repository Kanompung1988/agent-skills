# npm lifecycle policy reference

Sources: [npm CLI v11 scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts/), [npm package.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/).

- **NPM001**: install/ci lifecycle hooks: `preinstall`, `install`, `postinstall`, `preprepare`, `prepare`, `postprepare`. Git dependencies can also run prepare during packaging. Listing a hook is not proof of malicious behavior.
- **NPM002**: pack/publish hooks: `prepack`, `postpack`, `prepublishOnly`, `publish`, `postpublish`. `prepare` is also covered by NPM001, and may run during pack/publish.
- **NPM003**: `dependencies` hook runs after `node_modules` changes.
- **NPM004**: implicit `node-gyp rebuild` can be selected when root `binding.gyp` exists but no explicit `install` or `preinstall` script is defined. Only file existence is checked.
- **NPM005**: non-string scripts value (structural contract issue). The tool never prints the supplied command.
- **NPM006**: deprecated `prepublish` runs during npm install/ci, not only npm publish (important semantic trap).

Exit 0 = no findings in this limited rule set, 1 = review findings, 2 = invalid input. `--allow NAME` suppresses only that exact known event from results; it does **not** make npm skip the hook. No command bodies, credentials, environment values or variable expansions are printed. No `npm` invocation happens. Does not resolve dependencies, evaluate script intent, recursively inspect workspaces or transitive packages, reason about `ignore-scripts`, or compare npm versions beyond documented npm 11 behavior. The project is an educational developer review aid, not a security certification.
