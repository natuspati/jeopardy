const settings = {
  maxCategoriesToShow: parseInt(import.meta.env.VITE_MAX_CATEGORIES_TO_SHOW || '5', 10),
  maxLobbiesToShow: parseInt(import.meta.env.VITE_MAX_LOBBIES_TO_SHOW || '20', 10),
  numPromptInCategory: parseInt(import.meta.env.VITE_NUM_PROMPTS_IN_CATEGORY || '3', 10),
  promptQuestionShowLength: parseInt(import.meta.env.VITE_PROMPT_QUESTION_SHOW_LENGTH || '64', 10),
};

export default settings;
