const admin = require('firebase-admin');
const path = require('path');

let serviceAccount;

if (process.env.FIREBASE_SERVICE_ACCOUNT) {
    // Support either raw JSON or base64-encoded JSON in the env var
    try {
        const envVal = process.env.FIREBASE_SERVICE_ACCOUNT;
        try {
            serviceAccount = JSON.parse(envVal);
        } catch (e) {
            // not valid JSON, try base64 decode
            serviceAccount = JSON.parse(Buffer.from(envVal, 'base64').toString('utf8'));
        }
    } catch (err) {
        console.error('Failed to parse FIREBASE_SERVICE_ACCOUNT env var:', err.message);
        throw err;
    }
} else {
    try {
        serviceAccount = require(path.join(__dirname, '../servicekey.json'));
    } catch (err) {
        console.error('Missing Firebase service account file and FIREBASE_SERVICE_ACCOUNT env var is not set.');
        throw err;
    }
}

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
});

const bucket = admin.storage().bucket();

module.exports = { admin, bucket };