import React from "react";
import "./UploadForm.css";

const UploadForm = () => {
  return (
    <div className="upload-form">
      <h2>Upload Documents for Analysis</h2>
      <div className="upload-container">
        <div className="upload-box">
          <h3>Company Profile</h3>
          <div className="upload-icon">↑</div>
          <p>Drag & Drop Files</p>
          <p>or</p>
          <button className="browse-button">Browse Files</button>
        </div>
        <div className="upload-box">
          <h3>RFP Document</h3>
          <div className="upload-icon">↑</div>
          <p>Drag & Drop Files</p>
          <p>or</p>
          <button className="browse-button">Browse Files</button>
        </div>
      </div>
    </div>
  );
};

export default UploadForm;
