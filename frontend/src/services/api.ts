const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export const searchApi = {
  /**
   * Запускает асинхронный поиск на бэкенде.
   */
  startSearch: async (query: string, queryType: string) => {
    const response = await fetch(`${API_BASE_URL}/search/async`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query,
        query_type: queryType,
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Проверяет статус запущенной задачи.
   */
  checkStatus: async (taskId: string) => {
    const response = await fetch(`${API_BASE_URL}/search/status/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Получает последние отчеты из базы
   */
  getReports: async (query?: string) => {
    const url = query ? `${API_BASE_URL}/reports/?q=${encodeURIComponent(query)}` : `${API_BASE_URL}/reports/`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Получает связи из Neo4j
   */
  getGraph: async () => {
    const response = await fetch(`${API_BASE_URL}/graph/`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }
};
