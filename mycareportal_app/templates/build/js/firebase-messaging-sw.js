// [START initialize_firebase_in_sw]
// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.14.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.14.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in the
// messagingSenderId.
firebase.initializeApp({
  "apiKey": "AIzaSyBoHn7o797Puv80voB4uwPC1GztrspUJHg",
  'authDomain': "we-care-29905.firebaseapp.com",
  "databaseURL": "https://we-care-29905.firebaseio.com",
  "projectId": "we-care-29905",
  "storageBucket": "we-care-29905.appspot.com",
  'messagingSenderId': "356911246271",
  'appId': "1:356911246271:web:c1f3af11e123337c674f0a",
  'measurementId': "G-GPNQPQXS5L"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.usePublicVapidKey("BLqX-1Rb6U5RDfXHlpVFW8THXFkmgfH0e152EZezLuuIZgvV3asbNZZ3cm46zIez_sPB_f5i4iu0TRqbqa-PEDE");
console.log("messaging :",messaging )
// [END initialize_firebase_in_sw]

// If you would like to customize notifications that are received in the
// background (Web app is closed or not in browser focus) then you should
// implement this optional method.
// [START background_handler]
messaging.setBackgroundMessageHandler(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  // Customize notification here
  const notificationTitle = 'Background Message Title';
  const notificationOptions = {
    body: 'Background Message body.',
    icon: '/firebase-logo.png'
  };

  return self.registration.showNotification(notificationTitle,
      notificationOptions);
});
// [END background_handler]