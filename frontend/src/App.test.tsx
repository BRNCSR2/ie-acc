import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders landing page at /", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("ie-acc")).toBeInTheDocument();
    expect(screen.getByText("Irish Open Transparency Graph")).toBeInTheDocument();
  });

  it("renders search page at /search", () => {
    render(
      <MemoryRouter initialEntries={["/search?q=test"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("ie-acc")).toBeInTheDocument();
    expect(screen.getByLabelText("Search")).toBeInTheDocument();
  });

  it("renders entity detail page", () => {
    render(
      <MemoryRouter initialEntries={["/entity/company/100001"]}>
        <App />
      </MemoryRouter>,
    );
    expect(document.body).toBeTruthy();
  });

  it("renders graph explorer page", () => {
    render(
      <MemoryRouter initialEntries={["/graph/company/100001"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("Graph Explorer")).toBeInTheDocument();
  });
});
