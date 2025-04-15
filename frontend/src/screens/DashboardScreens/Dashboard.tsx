import { Card, Popconfirm, Button, Modal } from "antd";
import { useEffect, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import EmptyImg from "assets/images/empty.svg";
import { PropagateLoader } from "react-spinners";
import http from "utils/api";
import Swal from "sweetalert2";
import { LeftOutlined, RightOutlined } from "@ant-design/icons";
import Navbar from "../../components/Navbar";
import activeStreakImg from "../../assets/images/streak-active.png";
import inactiveStreakImg from "../../assets/images/streak-inactive.png";
import { render } from "react-dom";
import {
  CircularProgressbar,
  CircularProgressbarWithChildren,
  buildStyles
} from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

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
  progress?: number; 
}

interface Folder {
  id: string;
  name: string;
  decks: Deck[];
  progress?: number;
}

const Dashboard = () => {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [recentDecks, setRecentDecks] = useState<Deck[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [fetchingDecks, setFetchingDecks] = useState(false);
  const [isFolderPopupVisible, setIsFolderPopupVisible] = useState(false);
  const [selectedFolderDecks, setSelectedFolderDecks] = useState<Deck[]>([]);

  const idToken = window.localStorage.getItem('idToken');

  // for streaks
  const [streak, setStreak] = useState(10);
  const isActive = streak > 0; // Streak is active if it's greater than 0

  // for progress tracking
  const [progress, setProgress] = useState(0);


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
      const res = await http.get("/deck/all", {
        headers: {
          'Authorization': `${idToken}`
        }
      });
      let _decks = res.data?.decks || [];

      // Fetch streaks for all decks
      // _decks = await Promise.all(_decks.map(async (deck: Deck) => {
      //   try {
      //     const streakRes = await http.get(`/deck/streak/${deck.id}`);
      //     return { ...deck, streak: streakRes.data.streak || 0 };
      //   } catch (err) {
      //     console.error(`Error fetching streak for deck ${deck.id}:`, err);
      //     return { ...deck, streak: 0 };
      //   }
        
      // }));

      setDecks(_decks);

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
      const res = await http.get("/folders/all",{
        headers: {
          'Authorization': `${idToken}`
        }
    });
      console.log(res)
      setFolders(res.data?.folders || []);
      await http.post("/folders/all/update", { userId: localId }, {
        headers: {
          'Authorization': `${idToken}`
        }
      })
    } catch (err) {
      console.error("Error fetching folders:", err);
    }
  };

  const updateLastOpened = async (deckId: string) => {
    const timestamp = new Date().toISOString(); // Get the current timestamp
    await http.patch(`/deck/updateLastOpened/${deckId}`, { lastOpened: timestamp }, {
        headers: {
          'Authorization': `${idToken}`
        }
      });
    await http.patch(`/deck/streak/${deckId}`, {}, {
        headers: {
          'Authorization': `${idToken}`
        }
      })
    fetchDecks(); // Refetch the decks to update both 'decks' and 'recentDecks'
  };

  // const updateDeckProgress = async ()



  const handleFolderClick = async (folder: Folder) => {
    try {
      const res = await http.get(`/deck/get-deck/${folder.id}`, {
        headers: {
          'Authorization': `${idToken}`
        }
    });
      console.log(res)
      setSelectedFolderDecks(res.data?.decks || []);
      setIsFolderPopupVisible(true);
    } catch (err) {
      console.error("Error fetching folders:", err);
    }
    setIsFolderPopupVisible(true);
  };

  const navigateToDeck = async (deckId: string, deckTitle: string) => {
    navigate(`/deck/${deckId}/practice?title=${encodeURIComponent(deckTitle)}`);
  };

  const handleDeleteDeck = async (id: string) => {
    try {
      await http.delete(`/deck/delete/${id}`, {
        headers: {
          'Authorization': `${idToken}`
        }
    });
      Swal.fire("Deck Deleted Successfully!", "", "success").then(() => fetchDecks());
    } catch (err) {
      Swal.fire("Deck Deletion Failed!", "", "error");
    }
  };

  const handleDeleteFolder = async (id: string) => {
    try {
      await http.delete(`/folder/delete/${id}`), {
        headers: {
          'Authorization': `${idToken}`
        }
      };
      Swal.fire("Folder Deleted Successfully!", "", "success").then(() => fetchFolders());
    } catch (err) {
      Swal.fire("Folder Deletion Failed!", "", "error");
    }
  };

  const handleAddDeckToFolder = async (deckId: string, folderId: string) => {
    try {
      await http.post("/deck/add-deck", { deckId, folderId }, {
        headers: {
          'Authorization': `${idToken}`
        }
      });
      fetchDecks();
      fetchFolders();
      Swal.fire("Deck added to folder!", "", "success");
    } catch (err) {
      Swal.fire("Failed to add deck to folder!", "", "error");
    }
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

  const scrollLibrary = (direction: "left" | "right") => {
    if (sliderRefLibrary.current) {
      const scrollAmount = direction === "left" ? -300 : 300;
      sliderRefLibrary.current.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  const scrollRecent = (direction: "left" | "right") => {
    if (sliderRefRecent.current) {
      const scrollAmount = direction === "left" ? -300 : 300;
      sliderRefRecent.current.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  return (
    <div className="dashboard-page dashboard-commons">
      <Navbar isDashboard={true} onFolderCreated={fetchFolders} />

      <section>
        <div className="container">
          <div className="row">
            <div className="col-md-12">
              <Card className="welcome-card border-[#E7EAED]">
                <div className="welcome-container">
                  {/* Welcome Message */}
                  <div className="welcome-text">
                    <h3><b>Hey, Welcome Back!</b> 👋</h3>
                    <p>Let's start creating, memorizing, and sharing your flashcards.</p>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Folders Section */}
          <div className="folder-list row mt-4">
            <div className="col-md-12">
              <p className="title">My Folders</p>
            </div>
            {folders.length === 0 ? (
              <div className="col-md-12 text-center">
                <p>No folders created yet.</p>
              </div>
            ) : (
              folders.map((folder) => (
                <div key={folder.id} className="col-md-4">
                  <div className="folder-container" onClick={() => handleFolderClick(folder)}>
                    <h5>{folder.name}</h5>
                    {/* Wrapper to stop propagation from entire popconfirm block */}
                      
                    <p>{folder.decks.length > 0 ? `${folder.decks.length} deck(s)` : null}</p>
                    {
                      folder.decks.length > 0 ?
                      <div className="menu" style={{width: "100px", height: "100px"}}>
                        <CircularProgressbar className="progress-circle" value={folder.progress || 0} text={`${folder.progress || 0}%`} />
                      </div>
                      
                      : null
                    }
                      <p>{folder.decks.length === 0 ? `${folder.decks.length} deck(s)` : null}</p>
                      <div onClick={(e) => e.stopPropagation()}>
                        <Popconfirm
                          title="Are you sure to delete this folder?"
                          onConfirm={() => handleDeleteFolder(folder.id)}
                          okText="Yes"
                          cancelText="No"
                        >
                          <button className="btn text-danger">
                            <i className="lni lni-trash-can"></i> Delete
                          </button>
                        </Popconfirm>
                      </div>
                    </div>
                </div>
              ))
            )}
          </div>

          {/* Decks Section */}
          <div className="row mt-4">
            <div className="col-md-12">
              <p className="title">Your Library</p>
            </div>
            {fetchingDecks ? (
              <div className="col-md-12 text-center" style={{ height: "300px" }}>
                <PropagateLoader color="#221daf" />
              </div>
            ) : decks.length === 0 ? (
              <div className="row justify-content-center empty-pane">
                <div className="text-center">
                  <img className="img-fluid" src={EmptyImg} alt="No Decks" />
                  <p>No Study Deck Created Yet</p>
                </div>
              </div>
            ) : (
              <div className="slider-container">
                {canScrollLeftLib && (
                  <button className="arrow left" onClick={() => scrollLibrary("left")}>
                    <LeftOutlined />
                  </button>
                )}
                <div className="deck-slider" ref={sliderRefLibrary}>
                  {decks.map(({ id, title, description, visibility, cards_count, streak }) => (
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

                      {/* <div className="deck-footer"> */}
                      <div className="menu">
                        <Link to={`/deck/${id}/practice`}><button className="btn text-left"><i className="lni lni-book"></i> Practice</button></Link>
                        <Link to={`/deck/${id}/update`}><button className="btn text-edit"><i className="lni lni-pencil-alt"></i> Update</button></Link>
                        <Popconfirm
                          title="Are you sure to delete this deck?"
                          onConfirm={() => handleDeleteDeck(id)}
                          okText="Yes"
                          cancelText="No"
                        >
                          <button className="btn text-danger"><i className="lni lni-trash-can"></i> Delete</button>
                        </Popconfirm>
                        <select
                          onChange={(e) => handleAddDeckToFolder(id, e.target.value)}
                          defaultValue=""
                          style={{ color: "#007bff", border: "1px solid #007bff", padding: "5px", borderRadius: "4px" }}
                        >
                          <option value="" disabled style={{ color: "#999" }}>Add to Folder</option>
                          {folders.map((folder) => (
                            <option key={folder.id} value={folder.id}>{folder.name}</option>
                          ))}
                        </select>

                        <div className="streak-container">
                          <img
                            src={(streak ?? 0) > 0 ? activeStreakImg : inactiveStreakImg}
                            alt="Streak Icon"
                            className="streak-icon"
                          />
                          <span className="streak-text">{`${streak || 0}`}</span>
                        </div>
                      </div>
                      {/* </div> */}


                    </div>
                  ))}
                </div>
                {canScrollRightLib && (
                  <button className="arrow right" onClick={() => scrollLibrary("right")}>
                    <RightOutlined />
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Recent Decks Section */}
          <div className="row mt-4">
            <div className="col-md-12">
              <p className="title">Recent Decks</p>
            </div>
            {recentDecks.length === 0 ? (
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
            )}
          </div>

          {/* Folder Decks Modal */}
          <Modal
            title="Folder Decks"
            open={isFolderPopupVisible}
            onCancel={() => setIsFolderPopupVisible(false)}
            footer={null}
          >
            {selectedFolderDecks.length === 0 ? (
              <p>No decks in this folder.</p>
            ) : (
              selectedFolderDecks.map(({ id, title }, index) => (
                <div key={index}>
                  <Button className="folder-deck-button" onClick={() => navigateToDeck(id, title)}>
                    {title}
                  </Button>
                </div>
              ))
            )}
          </Modal>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;


