import React from "react";
import "./ResultCard.css";

const ResultCard = ({ title, content, isEligibilityCard = false }) => {
  // Extract eligibility status if this is the eligibility card
  const getEligibilityStatus = (content) => {
    if (!isEligibilityCard) return null;
    
    const lowerContent = content.toLowerCase();
    // Look for more specific eligibility indicators
    if (lowerContent.includes("go decision") || lowerContent.includes("eligible") || lowerContent.includes("qualified")) {
      return "ELIGIBLE";
    } else if (lowerContent.includes("no-go") || lowerContent.includes("not eligible") || lowerContent.includes("disqualified")) {
      return "NOT ELIGIBLE";
    }
    return "UNDETERMINED";
  };

  const eligibilityStatus = isEligibilityCard ? getEligibilityStatus(content) : null;

  const getStatusMessage = (status) => {
    switch(status) {
      case "ELIGIBLE":
        return "✔️ ELIGIBLE TO PROCEED";
      case "NOT ELIGIBLE":
        return "❌ NOT ELIGIBLE";
      default:
        return "⚠️ ELIGIBILITY UNDETERMINED";
    }
  };

  return (
    <div className={`result-card ${isEligibilityCard ? 'eligibility-card' : ''}`}>
      <h3>{title}</h3>
      {isEligibilityCard && eligibilityStatus && (
        <div className={`eligibility-status ${eligibilityStatus.toLowerCase().replace(' ', '-')}`}>
          {getStatusMessage(eligibilityStatus)}
        </div>
      )}
      <p>{content}</p>
    </div>
  );
};

export default ResultCard;
