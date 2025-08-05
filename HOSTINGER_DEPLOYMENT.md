# Hostinger Deployment Guide for Country's News

## Files to Upload to Hostinger

1. **Upload all files from the `dist/` directory to your Hostinger public_html folder:**
   - index.html (main homepage)
   - contact.html (contact page)
   - contact-handler.php (form processing script)
   - articles-data.json (for Load More functionality)
   - All files in articles/ folder
   - All files in categories/ folder
   - sitemap.xml, robots.txt, rss.xml

## Configuration Steps

1. **Update Email Settings in contact-handler.php:**
   ```php
   $admin_email = 'your-email@yourdomain.com'; // Change this to your actual email
   ```

2. **Test Form Functionality:**
   - Newsletter signup form on homepage
   - Contact form on contact page
   - Both forms will send emails to your configured admin email

## Call-to-Action Features Implemented

### 1. Newsletter Subscription
- **Location:** Homepage hero section
- **Features:** Email collection with confirmation emails
- **Storage:** Subscribers saved to newsletter_subscribers.txt
- **Action:** PHP processing with email notifications

### 2. Contact Form
- **Location:** Dedicated contact page (/contact.html)
- **Features:** 
  - Multiple inquiry types (News Tips, Story Ideas, Press Releases, etc.)
  - Optional newsletter subscription
  - Auto-reply confirmation emails
  - Admin notifications
- **Storage:** Contact logs saved to contact_log.txt

### 3. CTA Links Throughout Site
- **Email Links:** Direct mailto: links for quick contact
- **Contact Page:** Easily accessible from main navigation
- **Social Proof:** Professional contact form builds trust

## Monetization Features

### 1. Ad Placements
- **Homepage:** Integrated ad containers throughout article grid
- **Category Pages:** Multiple ad positions with responsive design
- **Contact Page:** Strategic ad placement without disrupting user experience

### 2. Lead Generation
- **Newsletter Collection:** Build email list for direct marketing
- **Contact Forms:** Capture leads for advertising opportunities
- **RSS Feed:** Additional subscriber acquisition channel

## Technical Features for Shared Hosting

### 1. Optimized for Hostinger
- **PHP 7.4+:** Compatible with Hostinger's PHP versions
- **No Database Required:** Uses flat files for simplicity
- **Email Function:** Uses PHP's built-in mail() function
- **Static Files:** Fast loading with minimal server requirements

### 2. SEO & Performance
- **Sitemap:** Auto-generated for search engine indexing
- **Robots.txt:** Proper crawler directives
- **RSS Feed:** Content syndication
- **Responsive Design:** Mobile-friendly layout
- **Fast Loading:** Minimal JavaScript and optimized images

## File Structure on Hostinger

```
public_html/
├── index.html (homepage)
├── contact.html (contact page)
├── contact-handler.php (form processor)
├── articles-data.json (AJAX data)
├── sitemap.xml
├── robots.txt
├── rss.xml
├── articles/
│   └── [all article HTML files]
├── categories/
│   └── [all category HTML files]
├── newsletter_subscribers.txt (auto-created)
└── contact_log.txt (auto-created)
```

## Testing Checklist

- [ ] Homepage loads correctly
- [ ] Newsletter signup form works
- [ ] Contact page loads
- [ ] Contact form submits successfully
- [ ] Email notifications are received
- [ ] Load More functionality works
- [ ] Category pages load
- [ ] Article pages load
- [ ] All links work correctly

## Troubleshooting

1. **Forms not working:** Check PHP error logs in Hostinger cPanel
2. **Emails not sending:** Verify email settings and SMTP configuration
3. **Load More not working:** Check JavaScript console for errors
4. **Images not showing:** Verify image paths and file uploads

## Support

For technical issues with the website functionality, check:
1. Hostinger's error logs
2. Browser developer console
3. PHP error reporting in contact-handler.php
