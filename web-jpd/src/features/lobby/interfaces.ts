import { z } from 'zod';
import {
  BaseUserSchema,
  BaseLobbySchema,
  BasePromptSchema,
  BaseLobbyCategorySchema,
} from '@/shared/interfaces';

// Category specific schemas (should be moved to category feature)
export const BaseCategorySchema = z.object({
  id: z.number(),
  owner_id: z.number(),
  name: z.string(),
  created_at: z.string(),
});

export const CategoryWithPromptsSchema = BaseCategorySchema.extend({
  prompts: z.array(BasePromptSchema),
});

export const LobbySchema = BaseLobbySchema.extend({
  host: BaseUserSchema,
  categories: z.array(CategoryWithPromptsSchema),
  lobby_categories: z.array(BaseLobbyCategorySchema),
});

export type Lobby = z.infer<typeof LobbySchema>;
