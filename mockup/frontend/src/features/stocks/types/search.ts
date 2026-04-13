export type SearchRequest = {
  market: string;
  name?: string;
  code?: string;
};

export type SearchResponse = {
  found: boolean;
  market: string;
  name: string | null;
  code: string;
};
