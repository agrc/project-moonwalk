import { browser } from '@ugrc/eslint-config';

browser[0].ignores = [
  '.firebase',
  '.github/*',
  '.vscode/*',
  'data/*',
  'dist/*',
  'forklift/*',
  'maps/*',
  'mockups/*',
  'node_modules/*',
  'package-lock.json',
  'public/*',
  'functions/*',
  'jobs/*',
  'firebase-export-*',
].concat(browser[0].ignores);

export default browser;
