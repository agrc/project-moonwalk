import { useMutation } from '@tanstack/react-query';
import { Button, useFirebaseFunctions } from '@ugrc/utah-design-system';
import { httpsCallable } from 'firebase/functions';
import type { MoonwalkBackup, Version } from './types';

export const ItemDetails = ({ item }: { item: MoonwalkBackup }) => {
  const { functions } = useFirebaseFunctions();
  const restore = httpsCallable(functions, 'restore');
  const restoreMutation = async (version: Version): Promise<string> => {
    const result = await restore({ item_id: item.itemId, category: version.category, generation: version.generation });

    return result.data as string;
  };

  const { data, isPending, error, mutate } = useMutation({ mutationFn: restoreMutation });

  return (
    <>
      <h3 className="font-medium">{item.name}</h3>
      <span className="text-xs dark:divide-slate-700">{item.itemId}</span>
      <h4>Restore Points</h4>
      <div className="grid grid-cols-1 gap-3">
        {item.versions.map((version) => {
          if (!version) return null;

          const entries = Object.entries(version.rowCounts ?? {});
          const hasCounts = entries.length > 0;

          return (
            <div
              key={version.generation}
              className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="font-medium">{new Date(version.updated.toDate()).toLocaleString()}</div>

              <div className="mb-3">
                {hasCounts ? (
                  <ul className="mt-1 divide-y divide-slate-100 text-sm dark:divide-slate-700">
                    {entries.map(([layer, count]) => (
                      <li key={layer} className="flex items-center justify-between py-1">
                        <span className="truncate pr-2 text-slate-600 dark:text-slate-300">{layer}</span>
                        <span className="font-mono tabular-nums">{count.toLocaleString()}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="mt-1 text-sm italic text-slate-500">No row counts available</div>
                )}
              </div>

              <div className="flex justify-end">
                <Button variant="primary" isDisabled={isPending} onPress={() => mutate(version)}>
                  {isPending ? 'Restoring…' : 'Restore'}
                </Button>
              </div>
            </div>
          );
        })}

        {/* status messages */}
        {data ? (
          <div className="col-span-full rounded-md border border-green-200 bg-green-50 p-2 text-green-800">
            Restore successful: {data}
          </div>
        ) : null}
        {error ? (
          <div className="col-span-full rounded-md border border-red-200 bg-red-50 p-2 text-red-800">
            Restore failed: {error.message}
          </div>
        ) : null}
      </div>
    </>
  );
};
