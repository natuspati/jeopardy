import { z } from 'zod';
import {
  BaseUserSchema,
  BasePromptSchema,
  BaseLobbySchema,
  BaseLobbyCategorySchema,
} from '@/shared/interfaces';
import { PromptTypeEnum } from '@/shared/enums';

export const CategoryCreateSchema = z.object({
  name: z.string().min(3).max(64),
});

const promptTypes = Object.values(PromptTypeEnum) as [string, ...string[]];

export const PromptCreateSchema = z.object({
  question: z.string(),
  question_type: z.enum(promptTypes),
  answer: z.string(),
  answer_type: z.enum(promptTypes),
  order: z.number().min(1),
  score: z.number(),
});

export const PromptUpdateSchema = PromptCreateSchema.partial();

export const BaseCategorySchema = z.object({
  id: z.number(),
  owner_id: z.number(),
  name: z.string(),
});

export const PromptSchema = BasePromptSchema;
export type Prompt = z.infer<typeof PromptSchema>;

export const CategorySchema = BaseCategorySchema.extend({
  owner: BaseUserSchema,
  prompts: z.array(PromptSchema),
  lobbies: z.array(BaseLobbySchema),
  lobby_categories: z.array(BaseLobbyCategorySchema),
  is_valid: z.boolean(),
});

export type Category = z.infer<typeof CategorySchema>;
