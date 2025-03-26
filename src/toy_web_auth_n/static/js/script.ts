interface AuthenticatorResponse {
    readonly clientDataJSON: ArrayBuffer;
    readonly attestationObject?: ArrayBuffer;
    readonly authenticatorData?: ArrayBuffer;
    readonly signature?: ArrayBuffer;
    readonly userHandle?: ArrayBuffer | null;
}

interface PublicKeyCredential extends Credential {
    readonly rawId: ArrayBuffer;
    readonly response: AuthenticatorResponse;
    getClientExtensionResults(): AuthenticationExtensionsClientOutputs;
}

function arrayBufferToBase64URL(buffer: ArrayBuffer): string {
    const uint8Array = new Uint8Array(buffer);
    return btoa(String.fromCharCode.apply(null, Array.from(uint8Array)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

function arrayBufferToBase64(buffer: ArrayBuffer): string {
    const uint8Array = new Uint8Array(buffer);
    return btoa(String.fromCharCode.apply(null, Array.from(uint8Array)));
}
function base64URLDecode(base64url: string): ArrayBuffer {
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

async function register(): Promise<void> {
    const username = prompt("Enter username:");
    if (!username) return;

    try {
        const beginResponse = await fetch('/register/begin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const options = await beginResponse.json();
        const user = {
            id: options.publicKey.user.id,
            name: options.publicKey.user.name,
            displayName: options.publicKey.user.displayName,
        };

        console.log("Received options:", JSON.stringify(options, null, 2));
        console.log("Original challenge:", options.publicKey.public_key.challenge);

        options.publicKey.challenge = base64URLDecode(options.publicKey.public_key.challenge);
        options.publicKey.user.id = base64URLDecode(options.publicKey.user.id);
        if (options.publicKey.excludeCredentials) {
            options.publicKey.excludeCredentials = options.publicKey.excludeCredentials.map((cred: any) => ({
                ...cred,
                id: base64URLDecode(cred.id)
            }));
        }

        console.log("Processed options:", JSON.stringify(options, null, 2));
        console.log("Decoded challenge:", arrayBufferToBase64(options.publicKey.challenge));

        const credential = await navigator.credentials.create(options) as PublicKeyCredential;

        const completeResponse = await fetch('/register/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: credential.id,
                rawId: arrayBufferToBase64URL(credential.rawId),
                response: {
                    attestationObject: arrayBufferToBase64URL(credential.response.attestationObject!),
                    clientDataJSON: arrayBufferToBase64URL(credential.response.clientDataJSON),
                },
                type: credential.type,
                user: user,
            })
        });

        const result = await completeResponse.json();
        console.log("Registration result:", result);
        localStorage.setItem('webauthn_user_id', result.user_id);
        localStorage.setItem('webauthn_username', result.username);
        alert(result.status);
    } catch (error) {
        console.error("Error in registration process:", error);
        alert("Error: " + (error as Error).message);
    }
}

async function authenticate(): Promise<void> {
    const username = prompt("Enter username:");
    if (!username) return;

    try {
        const beginResponse = await fetch('/authenticate/begin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const options = await beginResponse.json();
        console.log("Received auth options:", JSON.stringify(options, null, 2));

        options.publicKey.challenge = base64URLDecode(options.publicKey.challenge);

        if (options.publicKey.allowCredentials) {
            options.publicKey.allowCredentials = options.publicKey.allowCredentials.map((cred: any) => ({
                ...cred,
                id: base64URLDecode(cred.id)
            }));
        }

        const credential = await navigator.credentials.get(options) as PublicKeyCredential;
        console.log("Auth credential:", credential);

        const completeResponse = await fetch('/authenticate/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: credential.id,
                rawId: arrayBufferToBase64URL(credential.rawId),
                response: {
                    authenticatorData: arrayBufferToBase64URL(credential.response.authenticatorData!),
                    clientDataJSON: arrayBufferToBase64URL(credential.response.clientDataJSON),
                    signature: arrayBufferToBase64URL(credential.response.signature!),
                    userHandle: credential.response.userHandle ? arrayBufferToBase64URL(credential.response.userHandle) : null,
                },
                type: credential.type,
            })
        });

        const result = await completeResponse.json();
        console.log("Authentication result:", result);
        alert(result.status);
    } catch (error) {
        console.error("Error in authentication process:", error);
        alert("Error: " + (error as Error).message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('registerButton')?.addEventListener('click', register);
    document.getElementById('authenticateButton')?.addEventListener('click', authenticate);
});
