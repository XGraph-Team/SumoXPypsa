# Manhattan Power Grid Co-Simulation - Project Website

This is the official project website for the Manhattan Power Grid Co-Simulation platform, submitted to **WebConf 2026 Demo Track**.

## 🌐 Live Website

**GitHub Pages URL**: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

---

## 📁 File Structure

```
website/
├── index.html          # Main HTML file
├── styles.css          # Professional CSS styling
├── script.js           # Interactive JavaScript
└── README.md           # This file (deployment instructions)
```

---

## 🚀 Deployment to GitHub Pages

### Option 1: Deploy from Main Branch (Recommended)

1. **Upload website files to your repository:**
   ```bash
   git add website/
   git commit -m "Add project website"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under "Source", select **Deploy from a branch**
   - Choose **main** branch and **/website** folder
   - Click **Save**

3. **Wait 1-2 minutes** for deployment

4. **Access your website** at: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

### Option 2: Deploy from gh-pages Branch

1. **Create and push to gh-pages branch:**
   ```bash
   # Create orphan branch
   git checkout --orphan gh-pages

   # Copy website files to root
   cp -r website/* .

   # Commit and push
   git add .
   git commit -m "Deploy website to GitHub Pages"
   git push origin gh-pages

   # Return to main branch
   git checkout main
   ```

2. **Enable GitHub Pages:**
   - Go to **Settings** → **Pages**
   - Select **gh-pages** branch and **/ (root)** folder
   - Click **Save**

---

## ✏️ Customization Guide

### 1. **Replace Placeholders**

Search and replace the following in `index.html`:

| Placeholder | Replace With |
|------------|--------------|
| `YOUR_USERNAME` | Your GitHub username |
| `YOUR_REPO` | Your repository name |
| `YOUR_MAIN_DEMO_VIDEO_ID` | YouTube video ID for main demo |
| `YOUR_POWER_GRID_DEMO_ID` | YouTube video ID for power grid demo |
| `YOUR_TRAFFIC_DEMO_ID` | YouTube video ID for traffic demo |
| `YOUR_V2G_DEMO_ID` | YouTube video ID for V2G demo |
| `YOUR_WEATHER_DEMO_ID` | YouTube video ID for weather demo |
| `YOUR_CASCADE_DEMO_ID` | YouTube video ID for cascading failure demo |
| `YOUR_CHARGING_DEMO_ID` | YouTube video ID for EV charging demo |
| `[Author Names]` | Your names/affiliations |
| `your.email@institution.edu` | Your contact email |
| `Your Institution` | Your university/institution |

### 2. **Add Your Demo Videos**

#### Upload videos to YouTube:
1. Upload your demo videos to YouTube
2. Get the video ID from the URL:
   - URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - Video ID: `dQw4w9WgXcQ`

#### Update iframe sources:
```html
<!-- Replace YOUR_MAIN_DEMO_VIDEO_ID with actual ID -->
<iframe src="https://www.youtube.com/embed/YOUR_MAIN_DEMO_VIDEO_ID" ...>
```

### 3. **Update GitHub Repository Link**

Find all instances of:
```html
<a href="https://github.com/YOUR_USERNAME/YOUR_REPO" target="_blank">
```

Replace with your actual repository URL.

### 4. **Add Paper PDF**

1. Upload your PDF to the repository (e.g., `paper.pdf`)
2. Update the link in `index.html`:
   ```html
   <a href="paper.pdf" class="btn btn-outline" target="_blank">
       <i class="fas fa-file-pdf"></i>
       PDF
   </a>
   ```

### 5. **Update Author Information**

In the **Publication Section**, update:
```html
<p class="paper-authors">
    [Author Names]
</p>
```

To:
```html
<p class="paper-authors">
    John Smith, Jane Doe, Alice Johnson
</p>
```

---

## 🎨 Styling Customization

### Change Primary Color

Edit `styles.css`:
```css
:root {
    --primary-color: #3b82f6;  /* Change this hex code */
    --primary-dark: #2563eb;   /* Darker shade */
    --primary-light: #60a5fa;  /* Lighter shade */
}
```

### Modify Fonts

Replace font imports in `index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=YOUR_FONT&display=swap" rel="stylesheet">
```

Update CSS:
```css
:root {
    --font-primary: 'YOUR_FONT', sans-serif;
}
```

---

## 📹 Video Guidelines

### Recommended Specifications:
- **Resolution**: 1920x1080 (Full HD)
- **Format**: MP4, H.264
- **Duration**:
  - Main demo: 5-10 minutes
  - Feature demos: 2-5 minutes each
- **Audio**: Clear narration or captions

### Upload Checklist:
- [ ] Upload to YouTube
- [ ] Set to "Public" or "Unlisted"
- [ ] Add descriptive title
- [ ] Add timestamps in description
- [ ] Enable embedding
- [ ] Copy video ID
- [ ] Update `index.html`

---

## 🔧 Advanced Features

### Add Google Analytics

1. Get your Google Analytics tracking ID
2. Add before `</head>` in `index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Add Custom Domain

1. Purchase a domain (e.g., `manhattan-cosim.com`)
2. Add `CNAME` file to website root:
   ```
   manhattan-cosim.com
   ```
3. Configure DNS settings at your domain provider
4. Enable HTTPS in GitHub Pages settings

---

## 📱 Testing

### Test Responsiveness:
- Desktop (1920x1080)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667)

### Browser Compatibility:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

### Accessibility:
- Run [WAVE](https://wave.webaim.org/) accessibility checker
- Check keyboard navigation
- Verify screen reader compatibility

---

## 🐛 Troubleshooting

### Videos not loading?
- Check YouTube video IDs are correct
- Ensure videos are set to "Public" or "Unlisted"
- Verify embedding is enabled

### GitHub Pages not updating?
- Clear browser cache (Ctrl+Shift+R)
- Wait 5-10 minutes for propagation
- Check GitHub Actions for build errors

### Mobile menu not working?
- Verify `script.js` is loaded
- Check browser console for errors
- Test on different devices

---

## 📊 Analytics & Metrics

Track your website performance:
- **GitHub Insights**: Repository traffic
- **Google Analytics**: User behavior
- **YouTube Analytics**: Video engagement

---

## 🎓 WebConf 2026 Submission

### Checklist:
- [ ] All placeholder text replaced
- [ ] All demo videos uploaded and embedded
- [ ] GitHub repository link working
- [ ] Paper PDF available
- [ ] Contact information updated
- [ ] Website tested on mobile/desktop
- [ ] Accessibility verified
- [ ] Live URL confirmed
- [ ] Submit URL to WebConf demo track

### Submission Details:
- **Conference**: WWW 2026 (WebConf 2026)
- **Track**: Demo Track
- **Dates**: April 28 - May 2, 2026
- **Location**: Sydney, Australia
- **Submission URL**: https://www2026.thewebconf.org/calls/demos.html

---

## 📧 Support

For questions about the website:
- Open an issue on GitHub
- Contact: your.email@institution.edu

---

## 📄 License

This website template is released under MIT License.

---

## 🙏 Credits

**Built for**: Manhattan Power Grid Co-Simulation Project
**Framework**: Vanilla HTML/CSS/JavaScript
**Icons**: Font Awesome 6.4.0
**Fonts**: Inter, JetBrains Mono (Google Fonts)
**Deployment**: GitHub Pages

---

**Good luck with your WebConf 2026 submission! 🚀**
