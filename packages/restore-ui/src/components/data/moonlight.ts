export type MoonlightCollection = {
  items: MoonlightBackup[];
};
export type MoonlightBackup = {
  name: string;
  lastBackup: string;
  shortSchedule: boolean[];
  longSchedule: boolean[];
};

const generateRandomDate = () => {
  const start = new Date(2000, 0, 1);
  const end = new Date();
  const date = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return date.toISOString();
};

const generateRandomBooleanArray = (length: number) => {
  return Array.from({ length }, () => Math.random() >= 0.5);
};

const words = [
  'apple',
  'banana',
  'cherry',
  'date',
  'elderberry',
  'fig',
  'grape',
  'honeydew',
  'kiwi',
  'lemon',
  'mango',
  'nectarine',
  'orange',
  'papaya',
  'quince',
  'raspberry',
  'strawberry',
  'tangerine',
  'ugli',
  'vanilla',
  'watermelon',
  'yam',
  'zucchini',
];

const generateRandomWords = (count: number): string => {
  let result = '';
  for (let i = 0; i < count; i++) {
    result += words[Math.floor(Math.random() * words.length)] + ' ';
  }
  return result.trim();
};

const generateRandomService = () => {
  return {
    name: generateRandomWords(3),
    lastBackup: generateRandomDate(),
    shortSchedule: generateRandomBooleanArray(14),
    longSchedule: generateRandomBooleanArray(11),
  };
};

const generateItems = (count: number) => Array.from({ length: count }, () => generateRandomService());

export const moonlight: MoonlightCollection = {
  items: generateItems(20),
};
