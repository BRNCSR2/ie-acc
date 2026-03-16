import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";
import EntityCard from "./EntityCard";

describe("EntityCard", () => {
  it("renders entity name and type badge", () => {
    render(
      <MemoryRouter>
        <EntityCard
          entityType="Company"
          entityId="100001"
          name="Greenfield Construction LTD"
        />
      </MemoryRouter>,
    );
    expect(screen.getByText("Company")).toBeInTheDocument();
    expect(screen.getByText("Greenfield Construction LTD")).toBeInTheDocument();
  });

  it("shows score when provided", () => {
    render(
      <MemoryRouter>
        <EntityCard
          entityType="Charity"
          entityId="CHY001"
          name="Test Charity"
          score={4.56}
        />
      </MemoryRouter>,
    );
    expect(screen.getByText("4.56")).toBeInTheDocument();
  });

  it("shows props when provided", () => {
    render(
      <MemoryRouter>
        <EntityCard
          entityType="Company"
          entityId="100001"
          name="Test Co"
          props={{ county: "Dublin", status: "Normal" }}
        />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Dublin/)).toBeInTheDocument();
    expect(screen.getByText(/Normal/)).toBeInTheDocument();
  });
});
