import { z } from 'zod';
import { BasePromptSchema, NoTZDateTimeSchema } from '@/shared/interfaces.ts';
import { LobbyStateEnum } from '@/shared/enums.ts';

export const lobbyStateTypes = Object.values(LobbyStateEnum) as [string, ...string[]];

export const BaseUserSchema = z.object({
  id: z.number(),
  username: z.string(),
  created_at: NoTZDateTimeSchema,
});

export const BaseCategorySchema = z.object({
  id: z.number(),
  name: z.string(),
  owner_id: z.number(),
});

export const CategoryWithPromptsSchema = BaseCategorySchema.extend({
  prompts: z.array(BasePromptSchema),
});

export const LobbyCreatePublicSchema = z.object({
  category_ids: z.array(z.number()),
});

export const BaseLobbySchema = z.object({
  id: z.number(),
  host_id: z.number(),
  state: z.enum(lobbyStateTypes),
  created_at: NoTZDateTimeSchema,
});

export const LobbyStartedPublicSchema = BaseLobbySchema.extend({
  game_url: z.string().url(),
});

export const LobbySchema = BaseLobbySchema.extend({
  host: BaseUserSchema,
  categories: z.array(CategoryWithPromptsSchema),
});

export type Lobby = z.infer<typeof LobbySchema>;
