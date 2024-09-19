import { Timestamp } from 'firebase/firestore';

export type MoonwalkCollection = {
  items: MoonwalkBackup[];
};
export type Version = {
  generation: number;
  updated: Timestamp;
  category: 'long' | 'short';
};
export type MoonwalkBackup = {
  name: string;
  lastBackup: string;
  itemId: string;
  versions: Version[];
};
