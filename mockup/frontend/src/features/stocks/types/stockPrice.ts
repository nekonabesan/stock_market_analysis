export type UpsertStockPriceRequest = {
  code: string;
  market?: string;
  name?: string | null;
  start: string;
  end: string;
};

export type UpsertStockPriceResponse = {
  result: boolean;
};
