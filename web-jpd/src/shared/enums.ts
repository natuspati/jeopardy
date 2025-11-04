export const PromptTypeEnum = {
  TEXT: 'text',
  IMAGE: 'image',
  VIDEO: 'video',
  AUDIO: 'audio',
} as const;

export type PromptType = (typeof PromptTypeEnum)[keyof typeof PromptTypeEnum];

export const LobbyStateEnum = {
  CREATED: 'created',
  STARTED: 'started',
  FINISHED: 'finished',
} as const;

export type LobbyStateType = (typeof LobbyStateEnum)[keyof typeof LobbyStateEnum];
