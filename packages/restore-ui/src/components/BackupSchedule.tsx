import { Button } from '@ugrc/utah-design-system';

// today - 1 day
new Date(new Date().setDate(new Date().getDate() - 1)).toLocaleString();
// ignore time

export const BackupSchedule = ({
  shortSchedule,
  longSchedule,
}: {
  shortSchedule: boolean[];
  longSchedule: boolean[];
}) => {
  return (
    <>
      <h4>Daily</h4>
      <div className="grid grid-flow-row grid-cols-2">
        {shortSchedule.map((day, i) =>
          day ? (
            <Button variant="icon" key={i}>
              {new Date(new Date().setDate(new Date().getDate() - i)).toLocaleDateString()}
            </Button>
          ) : null,
        )}
      </div>
      <h4>Weekly</h4>
      <div className="grid grid-flow-row grid-cols-2">
        {longSchedule.map((day, i) =>
          day ? (
            <Button variant="icon" key={i}>
              {new Date(new Date().setDate(new Date().getDate() - i * 7)).toLocaleDateString()}
            </Button>
          ) : null,
        )}
      </div>
    </>
  );
};
