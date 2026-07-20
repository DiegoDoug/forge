import type { SecretType } from "./api";

export const SECRET_TYPE_LABELS: Record<SecretType, string> = {
  password: "Password",
  api_key: "API Key",
  ssh_key: "SSH Key",
  jwt_secret: "JWT Secret",
  oauth_secret: "OAuth Secret",
  env_var: "Environment Variable",
  note: "Secure Note",
  other: "Other",
};

export const SECRET_TYPES: SecretType[] = [
  "password",
  "api_key",
  "ssh_key",
  "jwt_secret",
  "oauth_secret",
  "env_var",
  "note",
  "other",
];
