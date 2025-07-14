const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Set a realistic user agent
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)');

  try {
    const targetUrl = 'https://www.ycombinator.com/companies?batch=Summer%202025&batch=Spring%202025&batch=Winter%202025&batch=Fall%202024&batch=Summer%202024&batch=Winter%202024&industry=Healthcare&industry=Engineering%2C%20Product%20and%20Design&regions=United%20States%20of%20America&regions=United%20Kingdom&regions=France';

    console.log('Navigating to filtered Y Combinator Companies Directory...');
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 60000 });

    // Scroll through the entire list to load all companies
    console.log('Scrolling through the filtered companies directory...');
    await autoScroll(page);

    // Extract all unique company links
    const companyLinks = await page.evaluate(() => {
      const linkElements = Array.from(document.querySelectorAll('a[href^="/companies/"]'));
      const links = linkElements
        .map(el => el.href)
        .filter((href, index, self) =>
          self.indexOf(href) === index && !href.includes('/companies/founders')
        ); // Exclude non-company links
      return links;
    });

    console.log(`Found ${companyLinks.length} filtered companies.`);

    // Save the company URLs to a JSON file
    fs.writeFileSync('filtered_company_urls.json', JSON.stringify(companyLinks, null, 2));
    console.log('Filtered company URLs have been saved to "filtered_company_urls.json".');

  } catch (error) {
    console.error('Error during Puppeteer execution:', error);
  } finally {
    await browser.close();
  }
})();

// Function to auto-scroll the page to the bottom
async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 100;
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;

        if (totalHeight >= scrollHeight - window.innerHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 100);
    });
  });
}
