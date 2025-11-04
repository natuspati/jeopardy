export enum GameStateEnum {
  BEFORE_START = 'BEFORE_START',
  SELECT_PLAYER = 'SELECT_PLAYER',
  SELECT_PROMPT = 'SELECT_PROMPT',
}

export enum PlayerStateEnum {
  SELECTED = 'SELECTED',
  CONNECTED = 'CONNECTED',
  DISCONNECTED = 'DISCONNECTED',
  BANNED = 'BANNED',
}

export enum LeadStateEnum {
  CONNECTED = 'CONNECTED',
  DISCONNECTED = 'DISCONNECTED',
}

export enum PromptStateEnum {
  NOT_SELECTED = 'NOT_SELECTED',
  SELECTED = 'SELECTED',
  ANSWERED = 'ANSWERED',
}

export interface PromptInGameSchema {
  id: number;
  category_id: number;
  question: string;
  question_type: string;
  answer: string;
  answer_type: string;
  order: number;
  score: number;
  state: PromptStateEnum;
}

export interface CategoryInGameSchema {
  id: number;
  name: string;
  owner_id: number;
  prompts: PromptInGameSchema[];
}

export interface PlayerSchema {
  id: number;
  username: string;
  state: PlayerStateEnum;
  score: number;
}

export interface LeadSchema {
  id: number;
  username: string;
  state: LeadStateEnum;
}

export interface GameSchema {
  id: number;
  state: GameStateEnum;
  lead: LeadSchema;
  players: PlayerSchema[];
  categories: CategoryInGameSchema[];
}

export interface GamePayloadSchema {
  game: GameSchema;
}

export interface GameEventSchema {
  name: string;
  payload: GamePayloadSchema | any; // Use any for now, can be more specific later
}
