import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router";
import SearchBar from "./SearchBar";

describe("SearchBar", () => {
  it("renders input and button", () => {
    render(
      <MemoryRouter>
        <SearchBar onSearch={vi.fn()} />
      </MemoryRouter>,
    );
    expect(screen.getByLabelText("Search")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Search" })).toBeInTheDocument();
  });

  it("calls onSearch on form submit", () => {
    const onSearch = vi.fn();
    render(
      <MemoryRouter>
        <SearchBar onSearch={onSearch} />
      </MemoryRouter>,
    );

    const input = screen.getByLabelText("Search");
    fireEvent.change(input, { target: { value: "Ryanair" } });
    fireEvent.submit(screen.getByRole("button", { name: "Search" }));

    expect(onSearch).toHaveBeenCalledWith("Ryanair");
  });

  it("uses initial value", () => {
    render(
      <MemoryRouter>
        <SearchBar onSearch={vi.fn()} initialValue="test" />
      </MemoryRouter>,
    );
    expect(screen.getByLabelText("Search")).toHaveValue("test");
  });
});
