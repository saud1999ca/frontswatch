YEMEN FRONT LINES - SITE FOLDER

1. Replace frontswatch.com with your real domain in index.html, robots.txt and sitemap.xml (find and replace, every occurrence).
2. Add a contact email for corrections in the About section (see the comment in index.html).
3. Upload this whole folder to Cloudflare Pages, Netlify or GitHub Pages. Keep all files together.
4. Connect your domain in the host's settings. HTTPS is added automatically.
5. In Google Search Console, add your domain, verify it, submit /sitemap.xml, then use "Request indexing" on the homepage.

UPDATING
- data.js holds all the data. ar.js holds the Arabic translation (add the Arabic title and text for each new event at the same position in AR.rows; if missing, the English text shows). Add a row to ROWS for each new event, add an entry to SNAPS when control of a governorate changes, and change LAST_UPDATED.
- Every row needs a source key from SRC and a status: confirmed, reported, claimed or reference.
- Re-upload data.js. The page itself does not change.
