import { api } from "@/lib/api-client";

export interface SetupStatus {
  setup_completed: boolean;
}

export interface SessionStatus {
  authenticated: boolean;
}

export const authApi = {
  setupStatus: () => api.get<SetupStatus>("/api/setup/status"),
  setup: (masterPassword: string) => api.post<SessionStatus>("/api/setup", { master_password: masterPassword }),
  unlock: (masterPassword: string) => api.post<SessionStatus>("/api/auth/unlock", { master_password: masterPassword }),
  lock: () => api.post<SessionStatus>("/api/auth/lock"),
  session: () => api.get<SessionStatus>("/api/auth/session"),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.put<SessionStatus>("/api/auth/password", { current_password: currentPassword, new_password: newPassword }),
};
