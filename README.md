# Quick Math

Mental math drills for phone, tablet and desktop: addition, subtraction,
multiplication and division, timed sprints or fixed sets, a "tricky facts" list
that brings back problems you miss, and optional voice answers.

## Files

- `index.html`: the app (also published as a claude.ai artifact, which adds its own page wrapper).
- `build.py`: wraps `index.html` into a full standalone page in `docs/` and draws the home-screen icons.
- `docs/`: the built site served by GitHub Pages. Don't edit it by hand.

## Update the live site

```bash
py build.py
git add -A
git commit -m "Update app"
git push
```
