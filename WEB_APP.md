# やさしい日本語 前例リファレンス Web App

## What This Builds

This is a Vite + React app that builds into one self-contained HTML file:

```text
dist/yasashii-reference.html
```

The final HTML can be opened directly in modern Microsoft Edge. It does not require a server, network access, external assets, or installation on the viewing machine.

## Development

Install dependencies:

```bash
npm install
```

Run the dev server:

```bash
npm run dev
```

The dev server is only for development. It is not needed for deployment.

## Build

```bash
npm run build
```

The build process:

1. Reads `data/*.json`, `data/sources.csv`, and `data/jlpt/*.csv`
2. Generates `src/generated/app-data.ts`
3. Runs Vite
4. Inlines JavaScript and CSS into one HTML file
5. Writes `dist/yasashii-reference.html`

## Verify

```bash
npm test
npm run typecheck
npm run build
```

Then open `dist/yasashii-reference.html` directly in Edge and test:

- `避難`
- `避難指示`
- `届出`
- `津波`
- `川崎市`

The search box also reads and writes the `q` query parameter, so refreshing or sharing a URL such as this keeps the search term:

```text
dist/yasashii-reference.html?q=避難
```

## Data Maintenance

When adding a new JSON source under `data/`, also add the matching row to `data/sources.csv`.
