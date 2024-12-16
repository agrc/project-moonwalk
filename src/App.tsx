import { useQuery } from '@tanstack/react-query';
import { Drawer, Footer, Header, SocialMedia, UgrcLogo } from '@ugrc/utah-design-system';
import { collection, getDocs } from 'firebase/firestore';
import PropTypes from 'prop-types';
import { useState } from 'react';
import { useOverlayTrigger } from 'react-aria';
import { useOverlayTriggerState } from 'react-stately';
import { BackupItem } from './components/BackupItem';
import { BackupSchedule } from './components/BackupSchedule';
import { useFirebaseApp } from './components/contexts';
import { MoonwalkBackup } from './components/types';

const version = import.meta.env.PACKAGE_VERSION;

const ErrorFallback = ({ error }: { error: Error }) => {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre style={{ color: 'red' }}>{error.message}</pre>
    </div>
  );
};

ErrorFallback.propTypes = {
  error: PropTypes.object,
};

const links = [
  {
    key: 'UGRC Homepage',
    action: { url: 'https://gis.utah.gov' },
  },
  {
    key: 'AGOL Organization',
    action: { url: 'https://utah.maps.arcgis.com' },
  },
  {
    key: 'GitHub Repository',
    action: { url: 'https://github.com/agrc/project-moonwalk' },
  },
  {
    key: `Version ${version} changelog`,
    action: { url: `https://github.com/agrc/project-moonwalk/releases/v${version}` },
  },
];

export default function App() {
  const sideBarState = useOverlayTriggerState({});
  const sideBarTriggerProps = useOverlayTrigger(
    {
      type: 'dialog',
    },
    sideBarState,
  );
  const trayState = useOverlayTriggerState({ defaultOpen: false });
  const trayTriggerProps = useOverlayTrigger(
    {
      type: 'dialog',
    },
    trayState,
  );
  const [selected, setSelected] = useState<MoonwalkBackup | undefined>();

  const { firestore } = useFirebaseApp();
  const getMoonwalkData = async () => {
    const snapshot = await getDocs(collection(firestore, 'items'));

    return snapshot.docs.map((doc) => {
      return {
        ...doc.data(),
        itemId: doc.id,
      } as MoonwalkBackup;
    });
  };

  const { isPending, error, data } = useQuery({
    queryKey: ['moonwalk'],
    queryFn: getMoonwalkData,
  });

  return (
    <>
      <main className="flex h-screen flex-col md:gap-2">
        <Header links={links}>
          <div className="flex h-full grow items-center gap-3">
            <UgrcLogo />
            <h2 className="font-heading text-3xl font-black text-zinc-600 sm:text-5xl dark:text-zinc-100">
              Project Moonwalk 🕺🏻
            </h2>
          </div>
        </Header>
        <section className="relative flex min-h-0 flex-1 overflow-x-hidden md:mr-2">
          <Drawer main state={sideBarState} {...sideBarTriggerProps}>
            <div className="mx-2 mb-2 grid grid-cols-1 gap-2">
              <h2 className="text-xl font-bold">Available restore points</h2>
              <div className="flex flex-col gap-4 rounded border border-zinc-200 p-3 dark:border-zinc-700">
                {selected && <BackupSchedule item={selected} />}
              </div>
            </div>
          </Drawer>
          <div className="relative flex flex-1 flex-col rounded border border-b-0 border-zinc-200 dark:border-0 dark:border-zinc-700">
            <div className="relative flex-1 space-y-2 overflow-y-scroll px-2 py-1.5 dark:rounded">
              {!isPending &&
                data?.map((item: MoonwalkBackup, i) => (
                  <BackupItem
                    key={i}
                    moonwalk={item}
                    select={(item) => {
                      setSelected(item);
                      sideBarState.open();
                    }}
                  />
                ))}
              {error && <ErrorFallback error={error} />}
              <Drawer
                type="tray"
                className="shadow-inner dark:shadow-white/20"
                allowFullScreen
                state={trayState}
                {...trayTriggerProps}
              >
                <section className="grid gap-2 px-7 pt-2">
                  <h2 className="text-center">What&#39;s here?</h2>
                  Features: 25,001
                </section>
              </Drawer>
            </div>
            <SocialMedia />
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
