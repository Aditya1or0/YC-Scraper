const puppeteer = require('puppeteer-extra');
const fs = require('fs');
require('dotenv').config();
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

// Use Stealth Plugin to avoid detection
puppeteer.use(StealthPlugin());

(async () => {
  // Launch the browser
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Set user agent from .env or use a default one
  const userAgent = process.env.USER_AGENT || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';
  await page.setUserAgent(userAgent);

  // Navigate to the OpenAI Crunchbase page
  const url = 'https://www.crunchbase.com/organization/openai';
  console.log(`Navigating to ${url}`);
  await page.goto(url, { waitUntil: 'networkidle2' });

  // Wait for the main heading to load
  try {
    await page.waitForSelector('h1[class*="heading"]', { timeout: 15000 });
  } catch (error) {
    console.error('Main heading not found. The page structure might have changed.');
    await browser.close();
    process.exit(1);
  }

  // Extract data
  const data = await page.evaluate(() => {
    // Helper function to get text content
    const getText = (selector) => {
      const element = document.querySelector(selector);
      return element ? element.innerText.trim() : null;
    };

    // Helper function to get multiple elements' text
    const getMultipleTexts = (selector) => {
      const elements = document.querySelectorAll(selector);
      return Array.from(elements).map(el => el.innerText.trim());
    };

    // Organization Name
    const name = getText('h1[class*="heading"]');

    // Stage
    const stage = getText('span[class*="stage"]');

    // Industries
    const industries = getMultipleTexts('a[class*="category"]').join(', ');

    // Headquarters Location
    const location = getText('span[class*="location"]');

    // Description
    const description = getText('div[class*="description"]');

    // CB Rank (Company)
    const cbRank = getText('span[class*="cb-rank"]');

    // Investment Stage
    const investmentStage = getText('span[class*="investment-stage"]');

    // Number of Portfolio Organizations
    const portfolioCount = getText('span[class*="portfolio-count"]');

    // Number of Investments
    const investmentsCount = getText('span[class*="investments-count"]');

    // Number of Lead Investments
    const leadInvestmentsCount = getText('span[class*="lead-investments-count"]');

    // Accelerator Program Type
    const acceleratorType = getText('span[class*="accelerator-type"]');

    // Accelerator Application Deadline
    const acceleratorDeadline = getText('span[class*="application-deadline"]');

    // Investor Type
    const investorType = getText('span[class*="investor-type"]');

    // Number of Founders (Alumni)
    const foundersCount = getText('span[class*="founders-count"]');

    // Number of Alumni
    const alumniCount = getText('span[class*="alumni-count"]');

    // Founders
    const foundersElements = document.querySelectorAll('div[class*="founder-card"] h2');
    const founders = Array.from(foundersElements).map(el => el.innerText.trim()).join(', ');

    // Number of Employees
    const employeesCount = getText('span[class*="employees-count"]');

    // Last Funding Date
    const lastFundingDate = getText('span[class*="last-funding-date"]');

    // Last Funding Amount
    const lastFundingAmount = getText('span[class*="last-funding-amount"]');

    // Last Funding Type
    const lastFundingType = getText('span[class*="last-funding-type"]');

    // Last Equity Funding Type
    const lastEquityFundingType = getText('span[class*="last-equity-funding-type"]');

    // Last Equity Funding Amount
    const lastEquityFundingAmount = getText('span[class*="last-equity-funding-amount"]');

    // Total Funding Amount
    const totalFundingAmount = getText('span[class*="total-funding-amount"]');

    // Top 5 Investors
    const topInvestorsElements = document.querySelectorAll('div[class*="top-investors"] a');
    const topInvestors = Array.from(topInvestorsElements).slice(0, 5).map(el => el.innerText.trim()).join(', ');

    // Estimated Revenue Range
    const revenueRange = getText('span[class*="revenue-range"]');

    // Operating Status
    const operatingStatus = getText('span[class*="operating-status"]');

    // Founded Date
    const foundedDate = getText('span[class*="founded-date"]');

    // Company Type
    const companyType = getText('span[class*="company-type"]');

    // Website
    const websiteElement = document.querySelector('a[class*="website-link"]');
    const website = websiteElement ? websiteElement.href : null;

    // LinkedIn
    const linkedinElement = document.querySelector('a[href*="linkedin.com"]');
    const linkedin = linkedinElement ? linkedinElement.href : null;

    // Contact Email
    const emailElement = document.querySelector('a[href^="mailto:"]');
    const contactEmail = emailElement ? emailElement.getAttribute('href').replace('mailto:', '') : null;

    // Phone Number
    const phoneNumber = getText('span[class*="phone-number"]');

    // Full Description
    const fullDescription = getText('div[class*="full-description"]');

    return {
      name,
      stage,
      industries,
      location,
      description,
      cbRank,
      investmentStage,
      portfolioCount,
      investmentsCount,
      leadInvestmentsCount,
      acceleratorType,
      acceleratorDeadline,
      investorType,
      foundersCount,
      alumniCount,
      founders,
      employeesCount,
      lastFundingDate,
      lastFundingAmount,
      lastFundingType,
      lastEquityFundingType,
      lastEquityFundingAmount,
      totalFundingAmount,
      topInvestors,
      revenueRange,
      operatingStatus,
      foundedDate,
      companyType,
      website,
      linkedin,
      contactEmail,
      phoneNumber,
      fullDescription
    };
  });

  // Check if essential data is present
  if (!data.name) {
    console.error('Failed to extract the company name. The page structure might have changed.');
  } else {
    console.log('Extracted Data:', data);

    // Save the data to a JSON file
    fs.writeFileSync('openai_crunchbase_data.json', JSON.stringify(data, null, 2));
    console.log('Data saved to openai_crunchbase_data.json');
  }

  // Close the browser
  await browser.close();
})();

// Helper function to auto-scroll the page (if needed)
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
