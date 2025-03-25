"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
function arrayBufferToBase64URL(buffer) {
    const uint8Array = new Uint8Array(buffer);
    return btoa(String.fromCharCode.apply(null, Array.from(uint8Array)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}
function arrayBufferToBase64(buffer) {
    const uint8Array = new Uint8Array(buffer);
    return btoa(String.fromCharCode.apply(null, Array.from(uint8Array)));
}
function base64URLDecode(base64url) {
    const padding = '='.repeat((4 - base64url.length % 4) % 4);
    const base64 = (base64url + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray.buffer;
}
function register() {
    return __awaiter(this, void 0, void 0, function* () {
        const username = prompt("Enter username:");
        if (!username)
            return;
        try {
            const beginResponse = yield fetch('/register/begin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });
            const options = yield beginResponse.json();
            console.log("Received options:", JSON.stringify(options, null, 2));
            console.log("Original challenge:", options.publicKey.public_key.challenge);
            options.publicKey.challenge = base64URLDecode(options.publicKey.public_key.challenge);
            options.publicKey.user.id = base64URLDecode(options.publicKey.user.id);
            if (options.publicKey.excludeCredentials) {
                options.publicKey.excludeCredentials = options.publicKey.excludeCredentials.map((cred) => (Object.assign(Object.assign({}, cred), { id: base64URLDecode(cred.id) })));
            }
            console.log("Processed options:", JSON.stringify(options, null, 2));
            console.log("Decoded challenge:", arrayBufferToBase64(options.publicKey.challenge));
            const credential = yield navigator.credentials.create(options);
            const completeResponse = yield fetch('/register/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: credential.id,
                    rawId: arrayBufferToBase64URL(credential.rawId),
                    response: {
                        attestationObject: arrayBufferToBase64URL(credential.response.attestationObject),
                        clientDataJSON: arrayBufferToBase64URL(credential.response.clientDataJSON),
                    },
                    type: credential.type,
                })
            });
            const result = yield completeResponse.json();
            console.log("Registration result:", result);
            alert(result.status);
        }
        catch (error) {
            console.error("Error in registration process:", error);
            alert("Error: " + error.message);
        }
    });
}
function authenticate() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const beginResponse = yield fetch('/authenticate/begin', {
                method: 'POST'
            });
            const options = yield beginResponse.json();
            options.publicKey.challenge = base64URLDecode(options.publicKey.challenge);
            if (options.publicKey.allowCredentials) {
                options.publicKey.allowCredentials = options.publicKey.allowCredentials.map((cred) => (Object.assign(Object.assign({}, cred), { id: base64URLDecode(cred.id) })));
            }
            const credential = yield navigator.credentials.get(options);
            const completeResponse = yield fetch('/authenticate/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: credential.id,
                    rawId: arrayBufferToBase64URL(credential.rawId),
                    response: {
                        authenticatorData: arrayBufferToBase64URL(credential.response.authenticatorData),
                        clientDataJSON: arrayBufferToBase64URL(credential.response.clientDataJSON),
                        signature: arrayBufferToBase64URL(credential.response.signature),
                        userHandle: credential.response.userHandle ? arrayBufferToBase64URL(credential.response.userHandle) : null,
                    },
                    type: credential.type,
                })
            });
            const result = yield completeResponse.json();
            console.log("Authentication result:", result);
            alert(result.status);
        }
        catch (error) {
            console.error("Error in authentication process:", error);
            alert("Error: " + error.message);
        }
    });
}
document.addEventListener('DOMContentLoaded', () => {
    var _a, _b;
    (_a = document.getElementById('registerButton')) === null || _a === void 0 ? void 0 : _a.addEventListener('click', register);
    (_b = document.getElementById('authenticateButton')) === null || _b === void 0 ? void 0 : _b.addEventListener('click', authenticate);
});
