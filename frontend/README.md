# Pressurize Frontend

This directory contains the Vue 3 frontend application for Pressurize and the user documentation.

## Project Setup

```sh
npm install
```

If Windows PowerShell blocks `npm.ps1`, use `npm.cmd` in the commands below.

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

## Documentation

The end-user documentation is built with [VitePress](https://vitepress.dev/).

### Running Documentation Locally

To start the documentation development server:

```sh
npm run docs:dev
```

The documentation will be available at `http://localhost:5173/products/pressurize/docs/` (port may vary).

### Building Documentation

The documentation is automatically built when you run `npm run build`. You can also build it independently:

```sh
npm run docs:build
```

### Previewing the Build

To preview the built application and documentation:

```sh
npm run preview
# OR
npm run docs:preview
```
