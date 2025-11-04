import { z } from 'zod';

export const UserRegisterSchema = z.object({
  username: z.string().min(3).max(16),
  password: z.string().min(6).max(16),
});

export const UserSchema = z.object({
  id: z.number(),
  username: z.string(),
});

export type User = z.infer<typeof UserSchema>;

export const TokenSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
});

export interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (token: string) => void;
  logout: () => void;
}
