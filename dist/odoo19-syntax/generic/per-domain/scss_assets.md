# SCSS & Assets

# Odoo 19 — SCSS & Assets Reference

This reference covers SCSS/Sass migration for the dart-sass compiler (Odoo 17 introduced it, Odoo 18 enforces it, Odoo 19 stays on it).

## Table of contents
1. Division operator — `/` no longer divides
2. `@import` is dead — use `@use` / `@forward`
3. Module-namespaced variables and mixins
4. Asset registration (recap)
5. CSS custom properties

---

## 1. Division operator

In dart-sass, `/` is treated as the CSS slash separator (e.g., `font: 16px/1.5 Arial`), NOT division. For arithmetic, use `math.div()` or `calc()`.

```scss
// ❌ OLD (libsass — Odoo 16) — division worked
.element {
    width: 100px / 2;        // = 50px in libsass, literal "100px / 2" in dart-sass
    font-size: 24px / 1.5;
}

// ✅ Odoo 19 — explicit math.div
@use "sass:math";

.element {
    width: math.div(100px, 2);
    font-size: math.div(24px, 1.5);
}

// ✅ Or use CSS calc() — works in any version
.element {
    width: calc(100px / 2);
    font-size: calc(24px / 1.5);
}
```

## 2. `@import` is dead — use `@use` / `@forward`

Sass `@import` is deprecated in dart-sass and will be removed. Odoo 18+ refuses or warns aggressively. Replace with `@use` and `@forward`.

```scss
// ❌ OLD
@import "variables";
@import "mixins";

.element {
    color: $primary-color;
    @include my-mixin();
}

// ✅ Odoo 19 — namespaced
@use "variables" as vars;
@use "mixins" as mix;

.element {
    color: vars.$primary-color;
    @include mix.my-mixin();
}

// ✅ Odoo 19 — wildcard namespace (closest to old behavior)
@use "variables" as *;
@use "mixins" as *;

.element {
    color: $primary-color;
    @include my-mixin();
}
```

`@forward` is for re-exporting from index/barrel files:

```scss
// _index.scss
@forward "variables";
@forward "mixins";
@forward "components";

// In a consuming file
@use "index" as *;
```

## 3. Module-namespaced variables and mixins

Differences when using `@use` (vs `@import`):
- Variables, mixins, and functions are namespaced by default — refer to them as `namespace.$var`, `namespace.mix($args)`.
- Use `as *` to import unprefixed (less safe, but matches old `@import` behavior).
- Use `as alias` for a custom prefix.
- Each `@use` is loaded once per file; `@import` could be repeated.
- Private members (prefixed with `_` or `-`) are not accessible across modules.

```scss
// _utils.scss
$primary: #875A7B;
$_secret: #000;        // private, not accessible from other files

@function double($x) { @return $x * 2; }

// _component.scss
@use "utils";

.box {
    color: utils.$primary;        // ✅
    width: utils.double(10px);    // ✅
    // background: utils.$_secret; // ❌ ERROR — private
}
```

## 4. Asset registration (recap)

SCSS files are added to bundles in `__manifest__.py` like any other asset:

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/scss/_variables.scss',
        'my_module/static/src/scss/main.scss',
    ],
},
```

Order matters when files use `@use` of relative paths. List shared/dependency files before files that consume them.

## 5. CSS custom properties

Native CSS variables (`--name: value;`) are unchanged and work fine. They're the recommended way for runtime-themable values.

```scss
:root {
    --my-primary: #875A7B;
}

.element {
    color: var(--my-primary);
}
```

These don't go through Sass compilation, so they're not affected by the libsass → dart-sass migration.
