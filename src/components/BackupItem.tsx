import { Button } from '@ugrc/utah-design-system';
import type { MoonwalkBackup } from './types.ts';

export const BackupItem = ({
  moonwalk,
  select,
}: {
  moonwalk: MoonwalkBackup;
  select: (moonwalk: MoonwalkBackup) => void;
}) => {
  return (
    <div className="grid grid-flow-col grid-cols-[repeat(2,_minmax(0,_1fr)),min-content] gap-x-4 rounded border border-zinc-200 p-3 px-2 py-1 dark:border-zinc-700">
      <span className="self-center">{moonwalk.name}</span>
      <span className="self-center italic">{moonwalk.itemType}</span>
      <Button variant="secondary" onPress={() => select(moonwalk)}>
        Versions
      </Button>
    </div>
  );
};
