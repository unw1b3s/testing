import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const executablePath = process.env.CHROME_BINARY || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const base = process.env.BASE_URL || 'http://127.0.0.1:8000';
const browser = await puppeteer.launch({executablePath, headless: true, args: ['--no-sandbox']});
fs.mkdirSync('artifacts/puppeteer', {recursive: true});
try {
  const page = await browser.newPage();
  await page.setViewport({width: 1280, height: 900});
  await page.goto(base);
  await page.waitForSelector('#email');
  await page.type('#email', 'student@example.com');
  await page.type('#password', 'Study123!');
  await page.click('#login-button');
  await page.waitForSelector('#tasks-panel', {visible: true});
  const actual = await page.$eval('#tasks-panel h1', el => el.textContent);
  assert.equal(actual, 'Мои задачи');
  await page.type('#title', 'Проверка Puppeteer');
  await page.click('#add-task');
  await page.waitForSelector('.task span');
  assert.equal(await page.$eval('.task span', el => el.textContent), 'Проверка Puppeteer');
  await page.screenshot({path: 'artifacts/puppeteer/result.png'});
  console.log(JSON.stringify({time: new Date().toISOString(), browser: await browser.version(), expected: 'Проверка Puppeteer', actual: await page.$eval('.task span', el => el.textContent), result: 'PASS'}, null, 2));
} finally { await browser.close(); }
