import { Button } from '@ugrc/utah-design-system';
import { MoonlightBackup } from './data/moonlight.ts';

export const BackupItem = ({
  moonlight,
  select,
}: {
  moonlight: MoonlightBackup;
  select: (moonlight: MoonlightBackup) => void;
}) => {
  return (
    <div className="grid grid-flow-col grid-cols-[repeat(2,_minmax(0,_1fr)),min-content] gap-x-4 rounded border px-2 py-1">
      <span className="self-center">{moonlight.name}</span>
      <span className="self-center">{new Date(moonlight.lastBackup).toLocaleString()}</span>
      <Button variant="secondary" onPress={() => select(moonlight)}>
        Restore
      </Button>
    </div>
  );
};
