export type Stock = {
  id: number;
  code: string;
  market: string | null;
  name: string | null;
  sector: string | null;
  memo: string | null;
  created_at: string;
  updated_at: string;
};

export type StocksResponse = {
  results: Stock[];
};