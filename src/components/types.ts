import { Timestamp } from 'firebase/firestore';

export type MoonwalkCollection = {
  items: MoonwalkBackup[];
};
export type Version = {
  generation: number;
  updated: Timestamp;
  category: 'long' | 'short';
  rowCounts: Record<string, number> | undefined;
};
export type MoonwalkBackup = {
  name: string;
  lastBackup: string;
  itemId: string;
  versions: Version[];
  itemType: string;
};
