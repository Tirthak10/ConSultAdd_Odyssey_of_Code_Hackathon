import React, { useState } from "react";
import "./UploadForm.css";
import ResultCard from "./ResultCard";
import LoadingSpinner from "./LoadingSpinner";

const UploadForm = () => {
  const [rfpDocument, setRfpDocument] = useState(null);
  const [companyData, setCompanyData] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [jsonResult, setJsonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('analyze'); // 'analyze' or 'convert'

  const handleFileUpload = async () => {
    if (!rfpDocument) {
      alert("Please select an RFP file");
      return;
    }

    if (mode === 'analyze' && !companyData) {
      alert("Please select both RFP and Company Data files");
      return;
    }

    const formData = new FormData();
    formData.append("rfp", rfpDocument);
    if (mode === 'analyze') {
      formData.append("company_data", companyData);
    }

    try {
      setLoading(true);
      const endpoint = mode === 'analyze' ? '/analyze' : '/convert-to-json';
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        if (mode === 'analyze') {
          setAnalysisResults(data);
          setJsonResult(null);
        } else {
          setJsonResult(data);
          setAnalysisResults(null);
        }
      } else {
        const errorData = await response.json();
        alert(errorData.error || "Failed to process document");
      }
    } catch (error) {
      console.error("Error processing document:", error);
      alert("An error occurred while processing the document");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (event, fileType) => {
    const file = event.target.files[0];
    if (file) {
      const fileExtension = file.name.split('.').pop().toLowerCase();
      
      if (fileType === 'rfp' && !['pdf', 'docx'].includes(fileExtension)) {
        alert('Please upload RFP document in PDF or DOCX format');
        event.target.value = '';
        return;
      }
      
      if (fileType === 'company' && !['pdf', 'docx'].includes(fileExtension)) {
        alert('Please upload company data in PDF or DOCX format');
        event.target.value = '';
        return;
      }

      if (fileType === 'rfp') {
        setRfpDocument(file);
      } else {
        setCompanyData(file);
      }
    }
  };

  return (
    <div className="upload-form">
      <h2>RFP Document Processing</h2>
      
      <div className="mode-selector">
        <button 
          className={`mode-button ${mode === 'analyze' ? 'active' : ''}`}
          onClick={() => setMode('analyze')}
        >
          Analyze RFP
        </button>
        <button 
          className={`mode-button ${mode === 'convert' ? 'active' : ''}`}
          onClick={() => setMode('convert')}
        >
          Convert to JSON
        </button>
      </div>

      <div className="upload-container">
        <div className="upload-box">
          <h3>RFP Document</h3>
          <input
            type="file"
            accept=".pdf,.docx"
            style={{ display: "none" }}
            id="rfpDocumentInput"
            onChange={(e) => handleFileChange(e, 'rfp')}
          />
          <div className="upload-icon">↑</div>
          <p>Upload RFP Document (PDF or DOCX)</p>
          <button
            className="browse-button"
            onClick={() => document.getElementById("rfpDocumentInput").click()}
          >
            Browse Files
          </button>
          {rfpDocument && (
            <p className="uploaded-file">Selected: {rfpDocument.name}</p>
          )}
        </div>

        {mode === 'analyze' && (
          <div className="upload-box">
            <h3>Company Data</h3>
            <input
              type="file"
              accept=".pdf,.docx"
              style={{ display: "none" }}
              id="companyDataInput"
              onChange={(e) => handleFileChange(e, 'company')}
            />
            <div className="upload-icon">↑</div>
            <p>Upload Company Data (PDF or DOCX)</p>
            <button
              className="browse-button"
              onClick={() => document.getElementById("companyDataInput").click()}
            >
              Browse Files
            </button>
            {companyData && (
              <p className="uploaded-file">Selected: {companyData.name}</p>
            )}
          </div>
        )}
      </div>

      <button 
        className="analyze-button"
        onClick={handleFileUpload}
        disabled={!rfpDocument || (mode === 'analyze' && !companyData) || loading}
      >
        {mode === 'analyze' ? 'Analyze Documents' : 'Convert to JSON'}
      </button>

      {loading && <LoadingSpinner />}

      {analysisResults && (
        <div className="analysis-results">
          <ResultCard 
            title="Eligibility Analysis" 
            content={analysisResults.eligibility}
            isEligibilityCard={true}
          />
          <ResultCard 
            title="RFP Summary" 
            content={analysisResults.summary} 
          />
          <ResultCard 
            title="Compliance Analysis" 
            content={analysisResults.compliance} 
          />
        </div>
      )}

      {jsonResult && (
        <div className="json-result">
          <h3>JSON Output</h3>
          <pre>{JSON.stringify(jsonResult, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default UploadForm;
