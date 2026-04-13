import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { AppHeader } from "../components/layout/AppHeader";

describe("AppHeader", () => {
  it("renders title and nav links", () => {
    render(
      <MemoryRouter>
        <AppHeader />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Stock Analysis Dashboard Prototype" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Home" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Chart" })).toBeInTheDocument();
  });
});
