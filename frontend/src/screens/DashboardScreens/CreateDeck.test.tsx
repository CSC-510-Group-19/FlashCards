import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import CreateDeck from "./CreateDeck";
import http from "utils/api";
import { act } from "react-dom/test-utils";
import Swal from "sweetalert2";

jest.mock("utils/api", () => ({
  post: jest.fn(),
}));

jest.mock("sweetalert2", () => ({ fire: jest.fn() }));

beforeEach(() => {
  jest.clearAllMocks();
  Storage.prototype.getItem = jest.fn((key) => {
    if (key === "flashCardUser") {
      return JSON.stringify({ localId: "testUserId" });
    }
    return null;
  });
});

describe("CreateDeck Component", () => {
  it("renders the CreateDeck form correctly", async () => {
    await act(async () => {
      render(
        <BrowserRouter>
          <CreateDeck />
        </BrowserRouter>
      );
    });

    expect(screen.getByText("Create a new study deck")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Title")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Description")).toBeInTheDocument();
    expect(screen.getByText("Create Deck")).toBeInTheDocument();
  });

  it("updates input fields correctly", async () => {
    await act(async () => {
      render(
        <BrowserRouter>
          <CreateDeck />
        </BrowserRouter>
      );
    });

    const titleInput = screen.getByPlaceholderText("Title");
    const descriptionInput = screen.getByPlaceholderText("Description");

    userEvent.type(titleInput, "New Deck Title");
    userEvent.type(descriptionInput, "This is a test description.");

    expect(titleInput).toHaveValue("New Deck Title");
    expect(descriptionInput).toHaveValue("This is a test description.");
  });

  it("submits the form successfully", async () => {
    (http.post as jest.Mock).mockResolvedValue({ data: { id: "deck123" } });
    await act(async () => {
      render(
        <BrowserRouter>
          <CreateDeck />
        </BrowserRouter>
      );
    });

    userEvent.type(screen.getByPlaceholderText("Title"), "Test Deck");
    userEvent.type(screen.getByPlaceholderText("Description"), "Test Description");

    await act(async () => {
      userEvent.click(screen.getByRole("button", { name: /create deck/i }));
    });

    await waitFor(() => expect(http.post).toHaveBeenCalledTimes(1));
    expect(http.post).toHaveBeenCalledWith("/deck/create", expect.objectContaining({
      title: "Test Deck",
      description: "Test Description",
      visibility: "public",
      localId: "testUserId",
    }));
    expect(Swal.fire).toHaveBeenCalledWith(expect.objectContaining({ icon: "success" }));
  });

  it("handles form submission error", async () => {
    (http.post as jest.Mock).mockRejectedValue(new Error("Failed to create deck"));
    await act(async () => {
      render(
        <BrowserRouter>
          <CreateDeck />
        </BrowserRouter>
      );
    });

    userEvent.type(screen.getByPlaceholderText("Title"), "Test Deck");
    userEvent.type(screen.getByPlaceholderText("Description"), "Test Description");

    await act(async () => {
      userEvent.click(screen.getByRole("button", { name: /create deck/i }));
    });

    await waitFor(() => expect(http.post).toHaveBeenCalledTimes(1));
    expect(Swal.fire).toHaveBeenCalledWith(expect.objectContaining({ icon: "error" }));
  });

  it("updates visibility when selecting Public or Private", async () => {
    await act(async () => {
      render(
        <BrowserRouter>
          <CreateDeck />
        </BrowserRouter>
      );
    });
  
    // Public should be selected by default
    const publicRadio = screen.getByLabelText(/Public/i);
    const privateRadio = screen.getByLabelText(/Private/i);
  
    expect(publicRadio).toBeChecked();
    expect(privateRadio).not.toBeChecked();
  
    // Change to Private
    userEvent.click(privateRadio);
  
    // Ensure Private is now selected
    await waitFor(() => {
      expect(privateRadio).toBeChecked();
      expect(publicRadio).not.toBeChecked();
    });
  });

});
