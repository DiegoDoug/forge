import { api } from "@/lib/api-client";

export const cryptoApi = {
  base64Encode: (text: string, urlSafe: boolean) => api.post<{ text: string }>("/api/crypto/base64/encode", { text, url_safe: urlSafe }),
  base64Decode: (text: string, urlSafe: boolean) => api.post<{ text: string }>("/api/crypto/base64/decode", { text, url_safe: urlSafe }),

  hash: (text: string, algorithm: string) => api.post<{ digest: string }>("/api/crypto/hash", { text, algorithm }),
  verifyHash: (text: string, algorithm: string, expected: string) =>
    api.post<{ valid: boolean }>("/api/crypto/hash/verify", { text, algorithm, expected }),

  aesEncrypt: (plaintext: string, passphrase: string) =>
    api.post<{ ciphertext: string; nonce: string; salt: string }>("/api/crypto/aes/encrypt", { plaintext, passphrase }),
  aesDecrypt: (ciphertext: string, nonce: string, salt: string, passphrase: string) =>
    api.post<{ text: string }>("/api/crypto/aes/decrypt", { ciphertext, nonce, salt, passphrase }),

  jwtDecode: (token: string) =>
    api.post<{ header: Record<string, unknown>; payload: Record<string, unknown> }>("/api/crypto/jwt/decode", { token }),
  jwtVerify: (token: string, secret: string, algorithm: string) =>
    api.post<{ valid: boolean; payload: Record<string, unknown> | null; error: string | null }>(
      "/api/crypto/jwt/verify",
      { token, secret, algorithm },
    ),
  jwtBuild: (payload: Record<string, unknown>, secret: string, algorithm: string, expiresInSeconds?: number) =>
    api.post<{ text: string }>("/api/crypto/jwt/build", {
      payload,
      secret,
      algorithm,
      expires_in_seconds: expiresInSeconds,
    }),

  rsaKeypair: (keySize: number) => api.post<{ private_key: string; public_key: string }>("/api/crypto/rsa/keypair", { key_size: keySize }),
  rsaEncrypt: (publicKey: string, plaintext: string) =>
    api.post<{ text: string }>("/api/crypto/rsa/encrypt", { public_key: publicKey, plaintext }),
  rsaDecrypt: (privateKey: string, ciphertext: string) =>
    api.post<{ text: string }>("/api/crypto/rsa/decrypt", { private_key: privateKey, ciphertext }),

  eccKeypair: () => api.post<{ private_key: string; public_key: string }>("/api/crypto/ecc/keypair"),
  eccSign: (privateKey: string, message: string) =>
    api.post<{ text: string }>("/api/crypto/ecc/sign", { private_key: privateKey, message }),
  eccVerify: (publicKey: string, message: string, signature: string) =>
    api.post<{ valid: boolean }>("/api/crypto/ecc/verify", { public_key: publicKey, message, signature }),
};
