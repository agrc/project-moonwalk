import { FirebaseApp, FirebaseOptions, initializeApp, registerVersion } from 'firebase/app';
import { connectFirestoreEmulator, Firestore, getFirestore } from 'firebase/firestore';
import { connectFunctionsEmulator, Functions, getFunctions } from 'firebase/functions';
import { createContext, ReactNode, useContext, useMemo, version } from 'react';

const DEFAULT_APP_NAME = '[DEFAULT]';
const FirebaseAppContext = createContext<{
  app: FirebaseApp;
  firestore: Firestore;
  functions: Functions;
} | null>(null);

const appVersion = import.meta.env.PACKAGE_VERSION;

type FirebaseProviderProps = {
  firebaseConfig: FirebaseOptions;
  children: ReactNode;
};

export function FirebaseAppProvider(props: FirebaseProviderProps) {
  const { firebaseConfig } = props;
  const value = useMemo(() => {
    registerVersion('react', version || 'unknown');
    registerVersion('app', appVersion || 'unknown');

    const app = initializeApp(firebaseConfig, DEFAULT_APP_NAME);
    const firestore = getFirestore(app);
    const functions = getFunctions(app);

    console.log('import.meta.env.DEV', import.meta.env.DEV);
    if (import.meta.env.DEV) {
      connectFirestoreEmulator(firestore, 'localhost', 8080);
      connectFunctionsEmulator(functions, 'localhost', 5001);
    }

    return { app, firestore, functions };
  }, [firebaseConfig]);

  return <FirebaseAppContext.Provider value={value} {...props} />;
}

export function useFirebaseApp() {
  const firebaseApp = useContext(FirebaseAppContext);
  if (!firebaseApp) {
    throw new Error('Cannot call useFirebaseApp unless your component is within a FirebaseAppProvider');
  }

  return firebaseApp;
}
