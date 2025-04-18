import "./styles.scss";
import { useState } from "react";
import { Modal, Input, Button } from "antd";
import Swal from "sweetalert2";
import { Link, useParams } from "react-router-dom";
import http from "utils/api";

interface NavbarProps {
  isDashboard?: boolean;
  onFolderCreated?: () => void; // Make onFolderCreated optional
}

const Navbar = ({ isDashboard, onFolderCreated }: NavbarProps) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const flashCardUser = window.localStorage.getItem("flashCardUser");
  const { localId } = (flashCardUser && JSON.parse(flashCardUser)) || {};

  const handleLogout = () => {
    window.localStorage.removeItem("flashCardUser");
    window.location.replace("/");
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      Swal.fire("Folder name cannot be empty!", "", "error");
      return;
    }

    try {
      await http.post("/folder/create", { name: newFolderName, userId: localId});
      Swal.fire("Folder Created Successfully!", "", "success");
      setIsModalVisible(false);
      setNewFolderName("");
      if (onFolderCreated) onFolderCreated(); // Call onFolderCreated only if it's provided
    } catch (err) {
      Swal.fire("Failed to create folder!", "", "error");
    }
  };

  return (
    <nav className="navbar navbar-expand-lg sticky-top">
      <div className="container">
        <Link className="navbar-brand" to="/">
          <img className="img-fluid" src={require("assets/images/logo.png")} alt="Logo" />
        </Link>
        <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
          {isDashboard ? (
            <div className="navbar-nav ml-auto navbar-centers gap-4">
              <li className="nav-item">
                <Link className="nav-link active" aria-current="page" to="/goals">
                  Goals
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link active" aria-current="page" to="/explore">
                  Explore
                </Link>
              </li>
              <Link to="/create-deck">
                <button className="btn btn-main">
                  <i className="lni lni-circle-plus mr-2"></i>
                  <span>Create Deck</span>
                </button>
              </Link>
              <button className="btn btn-main" onClick={() => setIsModalVisible(true)}>
                <i className="lni lni-folder mr-2"></i>
                <span>Create Folder</span>
              </button>
              <li className="nav-item" onClick={handleLogout} style={{ cursor: "pointer", fontWeight: "600" }}>
                <i className="lni lni-cross-circle mr-2" style={{ fontWeight: "600" }}></i> Logout
              </li>
            </div>
          ) : (
            <div className="navbar-nav ml-auto navbar-centers gap-4">
              <li className="nav-item">
                <Link className="nav-link active" aria-current="page" to="/goals">
                  Goals
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link active" aria-current="page" to="/explore">
                  Explore
                </Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link active" aria-current="page" to="/login">
                  Login
                </Link>
              </li>
              <Link to="/register">
                <button className="btn btn-main">Register</button>
              </Link>
            </div>
          )}
        </div>
      </div>
      <Modal
        title="Create New Folder"
        open={isModalVisible}
        onOk={handleCreateFolder}
        onCancel={() => setIsModalVisible(false)}
      >
        <Input
          value={newFolderName}
          onChange={(e) => setNewFolderName(e.target.value)}
          placeholder="Enter folder name"
        />
      </Modal>
    </nav>
  );
};

export default Navbar;
