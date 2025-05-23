import { initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { beforeUserCreated, beforeUserSignedIn, HttpsError, type AuthBlockingEvent } from 'firebase-functions/identity';

initializeApp();

const db = getFirestore();

async function checkUser(event: AuthBlockingEvent) {
  const email = event.data?.email;

  if (!email) {
    throw new HttpsError('invalid-argument', 'Email is required');
  }

  const ref = db.collection('authorized-users').doc(email);
  const doc = await ref.get();

  if (!doc.exists) {
    throw new HttpsError('permission-denied', `User (${email}) is not authorized`);
  }
}

export const beforeCreated = beforeUserCreated(checkUser);

/* This may not be necessary since beforeUserCreated fires before beforeUserSignedIn. Leaving it here in case it's needed for existing users.
 This also would be a good place to add additional checks for existing users.
 */
export const beforeSignedIn = beforeUserSignedIn(checkUser);
