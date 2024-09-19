import { useMutation } from '@tanstack/react-query';
import { Button } from '@ugrc/utah-design-system';
import { httpsCallable } from 'firebase/functions';
import { useFirebaseApp } from './contexts';
import { MoonwalkBackup, Version } from './types';

export const BackupSchedule = ({ item }: { item: MoonwalkBackup }) => {
  const { functions } = useFirebaseApp();
  const restore = httpsCallable(functions, 'restore');
  const restoreMutation = async (version: Version): Promise<string> => {
    const result = await restore({ item_id: item.itemId, category: version.category, generation: version.generation });

    return result.data as string;
  };

  const { data, isPending, error, mutate } = useMutation({ mutationFn: restoreMutation });

  return (
    <>
      <h4>Versions</h4>
      <div className="grid grid-flow-row grid-cols-1 gap-1">
        {item.versions.map((version) =>
          version ? (
            <Button variant="primary" key={version.generation} isDisabled={isPending} onPress={() => mutate(version)}>
              {new Date(version.updated.toDate()).toLocaleString()}
            </Button>
          ) : null,
        )}
        {data ? <div>Restore successful: {data}</div> : null}
        {error ? <div>Restore failed: {error.message}</div> : null}
      </div>
    </>
  );
};
