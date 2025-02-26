import { Card } from "antd";
import { useEffect, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import http from "utils/api";
import Swal from "sweetalert2";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";
import Navbar from "../../components/Navbar";

interface Deck {
  id: string;
  userId: string;
  title: string;
  description: string;
  visibility: string;
  cards_count: number;
  lastOpened?: string; // Optional for recent decks
  folderId?: string;    // Optional to track folder assignment
  streak?: number;
  goal?: string;
  goalCompleted?: boolean;
  goalProgress?: number;
  goalTarget?: number;
}

interface Folder {
  id: string;
  name: string;
  decks: Deck[];
}

const StudyHabits = () => {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [recentDecks, setRecentDecks] = useState<Deck[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [fetchingDecks, setFetchingDecks] = useState(false);
  const [isFolderPopupVisible, setIsFolderPopupVisible] = useState(false);
  const [selectedFolderDecks, setSelectedFolderDecks] = useState<Deck[]>([]);

  // for goals
  const [deckGoals, setDeckGoals] = useState<Record<string, {
    goal: string;
    completed: boolean;
    progress: number;
    target: number;
  }>>({});

  // Refs for sliders
  const sliderRefLibrary = useRef<HTMLDivElement>(null);
  const sliderRefRecent = useRef<HTMLDivElement>(null);
  const [canScrollLeftLib, setCanScrollLeftLib] = useState(false);
  const [canScrollRightLib, setCanScrollRightLib] = useState(false);
  const [canScrollLeftRec, setCanScrollLeftRec] = useState(false);
  const [canScrollRightRec, setCanScrollRightRec] = useState(false);

  const flashCardUser = window.localStorage.getItem("flashCardUser");
  const { localId } = (flashCardUser && JSON.parse(flashCardUser)) || {};

  const navigate = useNavigate();

  useEffect(() => {
    fetchDecks();
    fetchFolders();
  }, []);

  useEffect(() => {
    updateArrowsVisibilityLibrary();
    updateArrowsVisibilityRecent();
    const sliderLib = sliderRefLibrary.current;
    const sliderRec = sliderRefRecent.current;

    if (sliderLib) {
      sliderLib.addEventListener("scroll", updateArrowsVisibilityLibrary);
      return () => sliderLib.removeEventListener("scroll", updateArrowsVisibilityLibrary);
    }
    if (sliderRec) {
      sliderRec.addEventListener("scroll", updateArrowsVisibilityRecent);
      return () => sliderRec.removeEventListener("scroll", updateArrowsVisibilityRecent);
    }
  }, [decks]);

  const fetchDecks = async () => {
    setFetchingDecks(true);
    try {
      const res = await http.get("/deck/all", { params: { localId } });
      const _decks = res.data?.decks || [];
      setDecks(_decks);

      // Fetch goals for each deck
      const updatedGoals: Record<string, { goal: string; completed: boolean; progress: number; target: number; }> = {};
      await Promise.all(_decks.map(async (deck: Deck) => {
        try {
          const goalRes = await http.get(`/deck/goal/${deck.id}`);
          updatedGoals[deck.id] = {
            goal: goalRes.data.goal,
            completed: goalRes.data.goalCompleted,
            progress: goalRes.data.goalProgress,
            target: goalRes.data.goalTarget,
          };
        } catch (err) {
          console.error(`Error fetching goal for deck ${deck.id}:`, err);
        }
      }));

      setDeckGoals(updatedGoals);

      // Filter recent decks opened in the last 5 days
      const fiveDaysAgo = new Date();
      fiveDaysAgo.setDate(fiveDaysAgo.getDate() - 5);
      const recent = _decks
        .filter((deck: { lastOpened: string | number | Date; }) => deck.lastOpened && new Date(deck.lastOpened) >= fiveDaysAgo)
        .sort((a: { lastOpened: string | number | Date; }, b: { lastOpened: string | number | Date; }) => new Date(b.lastOpened!).getTime() - new Date(a.lastOpened!).getTime());

      setRecentDecks(recent);
    } catch (err) {
      console.error("Error fetching decks:", err);
      setDecks([]);
      setRecentDecks([]);
    } finally {
      setFetchingDecks(false);
    }
  };

  const fetchFolders = async () => {
    try {
      const res = await http.get("/folders/all", { params: { userId: localId } });
      setFolders(res.data?.folders || []);
    } catch (err) {
      console.error("Error fetching folders:", err);
    }
  };
  const updateLastOpened = async (deckId: string) => {
    const timestamp = new Date().toISOString(); // Get the current timestamp
    await http.patch(`/deck/updateLastOpened/${deckId}`, { lastOpened: timestamp });
    fetchDecks(); // Refetch the decks to update both 'decks' and 'recentDecks'
  };

  // Update arrows visibility based on scroll position
  const updateArrowsVisibilityLibrary = () => {
    if (sliderRefLibrary.current) {
      const { scrollLeft, scrollWidth, clientWidth } = sliderRefLibrary.current;
      setCanScrollLeftLib(scrollLeft > 0);
      setCanScrollRightLib(scrollLeft + clientWidth < scrollWidth);
    }
  };

  const updateArrowsVisibilityRecent = () => {
    if (sliderRefRecent.current) {
      const { scrollLeft, scrollWidth, clientWidth } = sliderRefRecent.current;
      setCanScrollLeftRec(scrollLeft > 0);
      setCanScrollRightRec(scrollLeft + clientWidth < scrollWidth);
    }
  };

  const scrollRecent = (direction: "left" | "right") => {
    if (sliderRefRecent.current) {
      const scrollAmount = direction === "left" ? -300 : 300;
      sliderRefRecent.current.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  const [completed, setCompleted] = useState<boolean>(false);

  useEffect(() => {
    const savedCompletion = localStorage.getItem("goalCompleted");
    if (savedCompletion == "true") {
      setCompleted(true);
    }
  }, []);

  return (
    <div className="dashboard-page dashboard-commons">
      <Navbar isDashboard={true} onFolderCreated={fetchFolders} />

      <section>
        <div className="container">
          <div className="row">
            <div className="col-md-12">
              <Card className="welcome-card border-[#E7EAED]">
                <div className="welcome-container">
                  {/* Study Habit Message */}
                  <div className="welcome-text">
                    <h3><b>🎯 Today's Study Goals</b></h3>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Goals Section */}
          <div className="goal-section">
            <div className="deck-container">
              {decks.map(({ id, title, description, visibility, cards_count, streak }) => (
                <div className="deck-goal" key={id}>
                  <div className="align-items-center">
                    <Link to={`/deck/${id}/practice`} onClick={() => updateLastOpened(id)}>
                      <h5>{title}</h5>
                    </Link>
                    <p className="goal-text">{deckGoals[id]?.goal || "No goal assigned"}</p>
                    {deckGoals[id]?.completed ? "✅ Completed" : "❌ Not Completed"}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="deck-slider" ref={sliderRefLibrary}>

          </div>
          {/* Recent Decks Section */}
          < div className="row mt-4" >
            <div className="col-md-12">
              <p className="title">Recent Decks</p>
            </div>
            {
              recentDecks.length === 0 ? (
                <div className="row justify-content-center">
                  <p>No Recent Decks Opened</p>
                </div>
              ) : (
                <div className="slider-container">
                  {canScrollLeftRec && (
                    <button className="arrow left" onClick={() => scrollRecent("left")}>
                      <LeftOutlined />
                    </button>
                  )}
                  <div className="deck-slider" ref={sliderRefRecent}>
                    {recentDecks.map(({ id, title, description, visibility, cards_count }) => (
                      <div className="deck-card" key={id}>
                        <div className="d-flex justify-content-between align-items-center">
                          <Link to={`/deck/${id}/practice`} onClick={() => updateLastOpened(id)}>
                            <h5>{title}</h5>
                          </Link>
                          <div className="d-flex gap-2 visibility-status align-items-center">
                            {visibility === "public" ? <i className="lni lni-world"></i> : <i className="lni lni-lock-alt"></i>}
                            {visibility}
                          </div>
                        </div>
                        <p className="description">{description}</p>
                        <p className="items-count">{cards_count} item(s)</p>
                      </div>
                    ))}
                  </div>
                  {canScrollRightRec && (
                    <button className="arrow right" onClick={() => scrollRecent("right")}>
                      <RightOutlined />
                    </button>
                  )}
                </div>
              )
            }
          </div>

        </div>
      </section >
    </div >
  );
};

export default StudyHabits;


