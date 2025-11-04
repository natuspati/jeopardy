import { z } from 'zod';
import { PromptTypeEnum } from '@/shared/enums';

export const BaseUserSchema = z.object({
  id: z.number(),
  username: z.string(),
});

const promptTypes = Object.values(PromptTypeEnum) as [string, ...string[]];

export const BasePromptSchema = z.object({
  id: z.number(),
  category_id: z.number(),
  question: z.string(),
  question_type: z.enum(promptTypes),
  answer: z.string(),
  answer_type: z.enum(promptTypes),
  order: z.number(),
  score: z.number(),
});

export const BaseLobbySchema = z.object({
  id: z.number(),
  host_id: z.number(),
  state: z.string(),
});

export const BaseLobbyCategorySchema = z.object({
  lobby_id: z.number(),
  category_id: z.number(),
});

export type User = z.infer<typeof BaseUserSchema>;
