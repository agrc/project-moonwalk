# Changelog

## [1.0.7](https://github.com/agrc/project-moonwalk/compare/v1.0.6...v1.0.7) (2024-12-17)


### Features

* integrate UtahID sign in ([61cb637](https://github.com/agrc/project-moonwalk/commit/61cb637604dcbcb46343bfff0593b60f712300b5)), closes [#9](https://github.com/agrc/project-moonwalk/issues/9)


### Dependencies

* bump app dependencies ([d8ed074](https://github.com/agrc/project-moonwalk/commit/d8ed074a522a154f85d922e7ae954f1f375e0acf))
* bump pytest-cov ([94d645c](https://github.com/agrc/project-moonwalk/commit/94d645c3bfa1a5eeb230a29e1728f37ae2522b5d))
* react 18 -&gt; 19 ([55453f8](https://github.com/agrc/project-moonwalk/commit/55453f8fcf3954c20790913731f0dbc86542e777))


### Documentation

* add step for running backup process ([8d5ae61](https://github.com/agrc/project-moonwalk/commit/8d5ae6197437c242027004a85106d9f587fc2e6f))
* improve setup instructions ([ff9869a](https://github.com/agrc/project-moonwalk/commit/ff9869a31c6dc4ded2754cca45ded17cd8c9a6a0))

## [1.0.6](https://github.com/agrc/project-moonwalk/compare/v1.0.5...v1.0.6) (2024-10-14)


### Bug Fixes

* correct firebase rules syntax ([3fa2916](https://github.com/agrc/project-moonwalk/commit/3fa29161b90ccadcb337c178ccb2fb5416bb8a6d))


### Dependencies

* bump the npm_and_yarn group with 2 updates ([cd549dd](https://github.com/agrc/project-moonwalk/commit/cd549dd760b8f321182c0015bbb390c2a6721995))

## [1.0.5](https://github.com/agrc/project-moonwalk/compare/v1.0.4...v1.0.5) (2024-10-14)


### Bug Fixes

* turn off firebase access for now ([2f3c536](https://github.com/agrc/project-moonwalk/commit/2f3c536821721ebf21833f7fc23f5ec1bcd5be45))

## [1.0.4](https://github.com/agrc/project-moonwalk/compare/v1.0.3...v1.0.4) (2024-10-02)


### Bug Fixes

* **backup:** handle non-feature-layer items ([6449352](https://github.com/agrc/project-moonwalk/commit/6449352a734467ec78dcd554995dd9aab2e1585e))

## [1.0.3](https://github.com/agrc/project-moonwalk/compare/v1.0.2...v1.0.3) (2024-10-01)


### Bug Fixes

* **backup:** add cloudrun configs for retries and timeout ([eff624e](https://github.com/agrc/project-moonwalk/commit/eff624e0d3f44d7f415cf3709f5e06eaf82e5f47))

## [1.0.2](https://github.com/agrc/project-moonwalk/compare/v1.0.1...v1.0.2) (2024-10-01)


### Bug Fixes

* make release (prod) deploys match push (dev) deploys ([8f09e22](https://github.com/agrc/project-moonwalk/commit/8f09e225ca27b86816356613302b3be8d4c6c962))

## [1.0.1](https://github.com/agrc/project-moonwalk/compare/v1.0.0...v1.0.1) (2024-10-01)


### Bug Fixes

* clean up deploy conditions ([b527735](https://github.com/agrc/project-moonwalk/commit/b527735585e62f340c0e398d1abb3598572c3288))

## 1.0.0 (2024-10-01)


### Features

* **backup:** clean up any orphaned exports ([7b40569](https://github.com/agrc/project-moonwalk/commit/7b40569fb55acf2812995b3ca280b39b49f46f56))
* **backup:** very basic backup implementation ([66510e9](https://github.com/agrc/project-moonwalk/commit/66510e9e0e49b823ab4321306574cdbb747f4885))
* **backup:** write simple docs to firestore ([1a35770](https://github.com/agrc/project-moonwalk/commit/1a35770fb1d89cbdef416d8e30c53ea9775aec7e))
* **backup:** write to storage emulator ([dc14727](https://github.com/agrc/project-moonwalk/commit/dc14727e5bf09a401cf2361904e8eb5e22ac9c5a))
* crude restores (truncate and load as well as recreate) ([19f36c9](https://github.com/agrc/project-moonwalk/commit/19f36c92474ea718d812e25bb6517fa7c74b71a3))
* more refinements to backup and wiring website to restore function ([bae34e6](https://github.com/agrc/project-moonwalk/commit/bae34e63e6c1ab900aea0f57407766b8127200ce))


### Bug Fixes

* **backup:** fix module name and allow import within container ([d71197b](https://github.com/agrc/project-moonwalk/commit/d71197b0124c00f33ab17b5f25873a43ecbaf907))
* **backup:** fix test import ([81833b7](https://github.com/agrc/project-moonwalk/commit/81833b7b5e760b4bb9e1d9664a4b53cd141e88e4))
* **backup:** pass gis to utility functions ([cd1c53a](https://github.com/agrc/project-moonwalk/commit/cd1c53aea2d1107aad0f4384775b4c5c45024ad0))
* **backup:** put data.zip in the correct temp folder ([3f4094d](https://github.com/agrc/project-moonwalk/commit/3f4094d091b3f340234b8e4ce81f2e82c6f4dd5e))
* **functions:** fix secret accessing ([22db46e](https://github.com/agrc/project-moonwalk/commit/22db46ea2bb09d38c38fe379d2554f642cf763fa))
* **functions:** mount secrets ([d9a7d29](https://github.com/agrc/project-moonwalk/commit/d9a7d29fb8711c9861ddbf16bacdbc380aa01781))
* **functions:** use UPPER CASE name for secrets ([68a02dd](https://github.com/agrc/project-moonwalk/commit/68a02ddff4a9fce5f1f319f501bdd9298ac93e4d))
* keep [@jacobdadams](https://github.com/jacobdadams)'s eye from twitching ([99bf74b](https://github.com/agrc/project-moonwalk/commit/99bf74b0a8d0d2ed33fcba1b2d79410d44cbc06a))
* new bucket paths to match lifecycle rules ([37e0558](https://github.com/agrc/project-moonwalk/commit/37e0558775cee7afd0ed7248f63fd54065b82e0b))
* **restore:** increase memory ([16cccf8](https://github.com/agrc/project-moonwalk/commit/16cccf85f8f1c32ce432c3a0c41a783a727965ac))


### Dependencies

* bump rollup in the npm_and_yarn group across 1 directory ([5e4602e](https://github.com/agrc/project-moonwalk/commit/5e4602e408278df70e4eb3664ee4a73242917667))
* bump the safe-dependencies group with 20 updates ([11a6ed2](https://github.com/agrc/project-moonwalk/commit/11a6ed2caa090625662faf59f68be4ec93d24966))
* **dev:** bump basic-auth-connect in the npm_and_yarn group ([c31bef1](https://github.com/agrc/project-moonwalk/commit/c31bef1e26482c37ef59c2ecba73d7b5ea76a4c8))
* **dev:** bump eslint-plugin-react-hooks ([8dd791c](https://github.com/agrc/project-moonwalk/commit/8dd791cf2c00a6218f0d829d89c8cfe852093972))
* **ui:** fix build with design system update ([8ea678c](https://github.com/agrc/project-moonwalk/commit/8ea678c3a9f35f0993104fdbe2f4844d9a3df38e))
* update firebase-functions requirement ([f5304fa](https://github.com/agrc/project-moonwalk/commit/f5304fa50d7be197635660c09fc072207167dc84))


### Styles

* **ui:** fix borders in dark mode ([de83e9d](https://github.com/agrc/project-moonwalk/commit/de83e9d3d26fc58ff8d62a86a39183dedfdb0311))
