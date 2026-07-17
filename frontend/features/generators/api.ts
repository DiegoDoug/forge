import { api } from "@/lib/api-client";

export const generatorsApi = {
  password: (input: {
    length: number;
    use_upper: boolean;
    use_lower: boolean;
    use_digits: boolean;
    use_symbols: boolean;
    exclude_ambiguous: boolean;
  }) => api.post<{ value: string }>("/api/generators/password", input),
  uuid4: () => api.post<{ value: string }>("/api/generators/uuid4"),
  uuid7: () => api.post<{ value: string }>("/api/generators/uuid7"),
  nanoid: (input: { size: number; alphabet?: string }) => api.post<{ value: string }>("/api/generators/nanoid", input),
  randomBytes: (input: { length: number; encoding: "hex" | "base64" | "base64url" }) =>
    api.post<{ value: string }>("/api/generators/random-bytes", input),
  apiKey: (input: { prefix: string }) => api.post<{ value: string }>("/api/generators/api-key", input),
  jwtSecret: (input: { length: number }) => api.post<{ value: string }>("/api/generators/jwt-secret", input),
  entropy: (input: { value: string }) =>
    api.post<{ bits: number; strength: string; pool_size: number }>("/api/generators/entropy", input),
};
