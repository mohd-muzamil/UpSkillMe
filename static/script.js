function displayKeywords(elementId, keywords) {
    console.log('displayKeywords() called');
    // Get the element to display the keywords
    const element = document.getElementById(elementId);
    // add keywords to the element
    element.innerHTML = keywords.join(', ');
}

function compareResumes() {
  console.log('compareResumes() called');
    // Get the values from the form
    const resumeText = document.getElementById('resume_text').value;
    const jobDescriptionText = document.getElementById('job-description').value;
  
    // Make an AJAX request to the Flask server
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/compare', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
  
    // Define the data to be sent to the server
    const data = JSON.stringify({ resumeText, jobDescriptionText });
  
    // Set up the callback function to handle the response
    xhr.onload = function () {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
  
        // Display extracted keywords
        displayKeywords('resume-keywords', response.resumeKeywords);
        displayKeywords('job-description-keywords', response.jobDescriptionKeywords);
        displayKeywords('skill-gap-recommendations', response.skillGapRecommendations);
      } else {
        console.error('Error:', xhr.statusText);
      }
    };
  
    // Send the request with the data
    xhr.send(data);
  }
  

  function displayFileName() {
    const input = document.getElementById('resume');
    const fileName = document.getElementById('file-name');
    fileName.textContent = input.files[0].name;
  }
  