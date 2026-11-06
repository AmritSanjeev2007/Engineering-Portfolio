# Engineering-Portfolio
My engineering portfolio website showcasing all the projects I have so far undertaken.

A static site (plain HTML, CSS and JavaScript, no build step) designed for GitHub Pages.

## Structure

```
index.html              Home page: about, projects, experience, education, skills, contact
css/style.css           All styling (colours are CSS variables at the top)
js/main.js              Theme toggle, mobile menu, project filters, hero airflow animation
projects/*.html         One page per project
projects/_template.html Blank project page to copy for new projects
assets/img/             Images (favicon, profile photo, project images)
.nojekyll               Tells GitHub Pages to serve files as-is
```

## Preview locally

Open `index.html` in a browser, or run a local server from this folder:

```
python -m http.server 8000
```

then visit http://localhost:8000.

## Publish on GitHub Pages

1. Push this folder to the `main` branch of `AmritSanjeev2007/Engineering-Portfolio`.
2. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch `main`, folder `/ (root)`.
3. The site will be live at https://amritsanjeev2007.github.io/Engineering-Portfolio/

All links are relative, so the site works under the `/Engineering-Portfolio/` sub-path.

## Customising

- **Profile photo:** add `assets/img/profile.jpg` and replace the `.photo-placeholder` div in `index.html` with `<img src="assets/img/profile.jpg" alt="Amrit Sanjeev">`.
- **Project images:** in each card, replace the `.card-media` SVG with an `<img>`. On project pages, replace the `.project-cover` and gallery placeholders.
- **New project:** copy `projects/_template.html`, fill it in, and add a card to the Projects grid in `index.html` with `data-category="engineering"` or `"computing"`.
- **CV download / LinkedIn:** commented-out buttons are in `index.html` (search for `TODO`).
- **Colours:** edit `--accent` and `--accent-2` at the top of `css/style.css`.
