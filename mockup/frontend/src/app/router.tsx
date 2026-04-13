import { createBrowserRouter } from "react-router-dom";

import { App } from "./App";
import { HomePage } from "../pages/HomePage";
import { ShouldersPage } from "../pages/ShouldersPage";
import { StockChartPage } from "../pages/StockChartPage";
import { TrendlinePage } from "../pages/TrendlinePage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "stocks/:code", element: <StockChartPage /> },
      { path: "trendlines/:code", element: <TrendlinePage /> },
      { path: "shoulders/:code", element: <ShouldersPage /> },
    ],
  },
]);