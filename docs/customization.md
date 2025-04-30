# 🎨 Customizing Font Size in GitHub Pages

You can increase the font size of your documentation site by adding a custom CSS file when using the **just-the-docs** theme.

---

## 📁 Step 1: Create a Custom CSS File

Add a file named `custom.css` at:

```
docs/assets/css/custom.css
```

Paste in the following styles:

```css
:root {
  --body-font-size: 18px;
}

h1, .text-delta {
  font-size: 2.5rem;
}

h2 {
  font-size: 2rem;
}

h3 {
  font-size: 1.75rem;
}
```

---

## ⚙️ Step 2: Reference It in `_config.yml`

In your `docs/_config.yml`, add:

```yaml
just_the_docs:
  custom_css:
    - "/assets/css/custom.css"
```

---

## ✅ Step 3: Commit & Push

```bash
git add docs/assets/css/custom.css docs/_config.yml
git commit -m "Added custom font size styling"
git push
```

The next time your GitHub Pages site builds, you’ll see larger, cleaner font sizes throughout your site.

---
