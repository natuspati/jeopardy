const settings = {
  maxCategoriesToShow: parseInt(import.meta.env.VITE_MAX_CATEGORIES_TO_SHOW || '5', 10),
  maxLobbiesToShow: parseInt(import.meta.env.VITE_MAX_LOBBIES_TO_SHOW || '20', 10),
  numPromptInCategory: parseInt(import.meta.env.VITE_NUM_PROMPTS_IN_CATEGORY || '3', 10),
  promptQuestionShowLength: parseInt(import.meta.env.VITE_PROMPT_QUESTION_SHOW_LENGTH || '64', 10),
  minCategoriesInLobby: parseInt(import.meta.env.VITE_MIN_CATEGORIES_IN_LOBBY || '3', 10),
  maxCategoriesInLobby: parseInt(import.meta.env.VITE_MAX_CATEGORIES_IN_LOBBY || '5', 10),
  lobbyCreatedAtFilterDays: parseInt(import.meta.env.VITE_LOBBY_CREATED_AT_FILTER_DAYS || '1', 10),
};

export default settings;
