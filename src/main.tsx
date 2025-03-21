import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  FirebaseAnalyticsProvider,
  FirebaseAppProvider,
  FirebaseAuthProvider,
  FirebaseFunctionsProvider,
  FirestoreProvider,
} from '@ugrc/utah-design-system';
import { OAuthProvider } from 'firebase/auth';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ErrorBoundary } from 'react-error-boundary';
import App from './App';
import './index.css';

const provider = new OAuthProvider('oidc.utahid');
provider.addScope('app:UGRCMoonwalk'); // request submitted to create this app in AP Admin

let firebaseConfig: Record<string, string>;
if (import.meta.env.VITE_FIREBASE_CONFIGS) {
  firebaseConfig = JSON.parse(import.meta.env.VITE_FIREBASE_CONFIGS);
} else {
  throw new Error('VITE_FIREBASE_CONFIGS is not defined');
}

const MainErrorFallback = ({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => {
  return (
    <div className="static flex h-screen w-screen items-center justify-center">
      <div className="flex-col items-center">
        <h1>Something went wrong</h1>
        <pre className="text-red-500">{error.message}</pre>
        <button className="w-full rounded-full border p-1" onClick={resetErrorBoundary}>
          Try again
        </button>
      </div>
    </div>
  );
};

const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary FallbackComponent={MainErrorFallback} onReset={() => window.location.reload()}>
      <FirebaseAppProvider config={firebaseConfig}>
        <FirebaseAuthProvider provider={provider}>
          <FirebaseAnalyticsProvider>
            <FirestoreProvider>
              <FirebaseFunctionsProvider>
                <QueryClientProvider client={queryClient}>
                  <App />
                </QueryClientProvider>
              </FirebaseFunctionsProvider>
            </FirestoreProvider>
          </FirebaseAnalyticsProvider>
        </FirebaseAuthProvider>
      </FirebaseAppProvider>
    </ErrorBoundary>
  </StrictMode>,
);
