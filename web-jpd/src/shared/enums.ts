export const PromptTypeEnum = {
  TEXT: 'text',
  IMAGE: 'image',
  VIDEO: 'video',
  AUDIO: 'audio',
} as const;

export type PromptType = (typeof PromptTypeEnum)[keyof typeof PromptTypeEnum];
