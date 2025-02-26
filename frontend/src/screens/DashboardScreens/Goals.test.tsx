import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import StudyHabits from "./Goals"; // Update path based on file structure
import http from "utils/api";
import {act} from "react-dom/test-utils";

// Mock API calls
jest.mock("utils/api", () => ({
  get: jest.fn(),
  patch: jest.fn(),
}));

// Mock local storage
beforeEach(() => {
    jest.clearAllMocks();

  Storage.prototype.getItem = jest.fn((key) => {
    if (key === "flashCardUser") {
      return JSON.stringify({ localId: "testUserId" });
    }
    return null;
  });
});

describe("StudyHabits Component", () => {
  const mockDecks = [
    {
      id: "1",
      userId: "testUserId",
      title: "Test Deck 1",
      description: "A test deck",
      visibility: "public",
      cards_count: 10,
      lastOpened: new Date().toISOString(),
      goal: "Complete 5 flashcards",
      goalCompleted: false,
      goalProgress: 2,
      goalTarget: 5,
    },
  ];

  beforeEach(() => {
    (http.get as jest.Mock).mockImplementation((url) => {
      if (url === "/deck/all") {
        return Promise.resolve({ data: { decks: mockDecks } });
      }
      if (url.startsWith("/deck/goal/")) {
        return Promise.resolve({
          data: {
            goal: "Complete 5 flashcards",
            goalCompleted: false,
            goalProgress: 2,
            goalTarget: 5,
          },
        });
      }
      if (url === "/folders/all") {
        return Promise.resolve({ data: { folders: [] } });
      }
      return Promise.reject(new Error("Unknown API endpoint"));
    });
  });

  it("renders study goals section", async () => {
    await act(async () => {
        render(
          <BrowserRouter>
            <StudyHabits />
          </BrowserRouter>
        );
      });

    expect(screen.getByText("🎯 Today's Study Goals")).toBeInTheDocument();

    // Wait for decks to load
    await waitFor(() => {
      const deckLinks = screen.getAllByText("Test Deck 1");
      expect(deckLinks.length).toBeGreaterThan(0); // Ensure at least one exists
    //   expect(screen.getByText("Complete 5 flashcards")).toBeInTheDocument();
    });

    // Ensure the goal completion status is displayed correctly
    expect(screen.getByText("❌ Not Completed")).toBeInTheDocument();
  });

  it("fetches and displays decks", async () => {
    render(
      <BrowserRouter>
        <StudyHabits />
      </BrowserRouter>
    );

    await waitFor(() => {
        const deckLinks = screen.getAllByText("Test Deck 1");
        expect(deckLinks.length).toBeGreaterThan(0); // Ensure at least one exists
    //   expect(screen.getByText("Complete 5 flashcards")).toBeInTheDocument();
    });
  });

  it("navigates to a deck when clicked", async () => {
    await act(async () => {
        render(
          <BrowserRouter>
            <StudyHabits />
          </BrowserRouter>
        );
      });

    await act(async () => {
        const deckLinks = await screen.findAllByText("Test Deck 1");
        expect(deckLinks.length).toBeGreaterThan(0); // Ensure at least one exists
    
        userEvent.click(deckLinks[0]); // Click only the first one
        expect(http.patch).toHaveBeenCalledWith("/deck/updateLastOpened/1", expect.any(Object));
    });
  });

  it("displays 'No Recent Decks Opened' if no recent decks", async () => {
    (http.get as jest.Mock).mockImplementation((url) => {
      if (url === "/deck/all") {
        return Promise.resolve({ data: { decks: [] } });
      }
      return Promise.resolve({ data: { folders: [] } });
    });

    await act(async () => {
        render(
          <BrowserRouter>
            <StudyHabits />
          </BrowserRouter>
        );
      });

    await waitFor(() => {
      expect(screen.getByText("No Recent Decks Opened")).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully", async () => {
    // Mock API failure
    (http.get as jest.Mock).mockRejectedValue(new Error("API error"));
  
    // Suppress expected console errors
    jest.spyOn(console, "error").mockImplementation(() => {}); 
  
    await act(async () => {
      render(
        <BrowserRouter>
          <StudyHabits />
        </BrowserRouter>
      );
    });
  
    await act(async () => {
      await waitFor(() => {
        expect(screen.getByText("🎯 Today's Study Goals")).toBeInTheDocument();
      });
    });
  
    // Restore console.error after the test
    jest.restoreAllMocks();
  });
});