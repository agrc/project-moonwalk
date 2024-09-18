export type MoonlightCollection = {
  items: MoonlightBackup[];
};
export type MoonlightBackup = {
  name: string;
  lastBackup: string;
  itemId: string;
};
