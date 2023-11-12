function displayKeywords(elementId, keywords) {
  console.log('displayKeywords() called');
  const matchJobs = document.getElementById(elementId);
  const resultTitle = document.getElementById('recommendations_title');

  // Create an h2 element
  const heading = document.createElement('h2');
  heading.textContent = 'Matched Jobs';

  if (resultTitle.childElementCount === 0) {
      resultTitle.appendChild(heading);
  }

  // Create a list and append keywords to it
  const list = document.createElement('ul');
  keywords.forEach(keyword => {
      const listItem = document.createElement('li');
      listItem.textContent = keyword;
      list.appendChild(listItem);
  });

  // Append the list to the 'recommendations' element
  matchJobs.innerHTML = ''; // Clear existing content
  matchJobs.appendChild(list);


}

function displayGPTResults(recommendations_title, api_title) {
  const matchJobsContainer = document.getElementById('recommendations');
    const matchJobs = document.getElementById('recommendations');

    // Check if the element with id 'recommendations' exists
    if (matchJobsContainer) {
        const resultTitle = document.getElementById('recommendations_title');

        // Create an h2 element
        const heading = document.createElement('h2');
        heading.textContent = recommendations_title;

        if (resultTitle.childElementCount === 0) {
          resultTitle.appendChild(heading);
      }

        // Fetch the HTML content directly
        fetch(api_title)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.statusText}`);
                }
                console.log('Response:', response)
                return response.text(); // Change to text() since we're expecting HTML
            })
            .then(htmlContent => {
                // Set the HTML content directly
                matchJobs.innerHTML = htmlContent;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    } else {
        console.error("Element with id 'recommendations' not found.");
    }
}


function compareResumes() {
  console.log('compareResumes() called');

  // Get the values from the form
  // const resumeText = document.getElementById('resume_text').value;
  const jobDescriptionText = document.getElementById('job-description').value;

  // Get the file input element
  const fileInput = document.getElementById('resume');
  
  // select id=image-grid and display it
  // const imageGrid = document.getElementById('image-grid');
  // imageGrid.style.display = 'block';

  // Check if a file is selected
  if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      console.log('Selected file:', file);

      // Use FormData to create a multipart/form-data request
      const formData = new FormData();
      formData.append('resume', file);
      // formData.append('resumeText', resumeText);
      formData.append('jobDescriptionText', jobDescriptionText);

      // Make an AJAX request to the Flask server
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/compare', true);

      // Set up the callback function to handle the response
      xhr.onload = function () {
          if (xhr.status === 200) {
              const response = JSON.parse(xhr.responseText);
              // Display extracted keywords
              // displayKeywords('recommendations', response.resumeKeywords);
              // displayKeywords('job-description-keywords', response.jobDescriptionKeywords);
              // displayKeywords('skill-gap-recommendations', response.skillGapRecommendations);
              // displayKeywords('recommendations', response.recommendations);
          } else {
              console.error('Error:', xhr.statusText);
          }
      };

      // Send the request with the FormData
      xhr.send(formData);
  } else {
      console.error('No file selected.');
  }
}




function displayFileName() {
  const input = document.getElementById('resume');
  const fileName = document.getElementById('file-name');
  fileName.textContent = input.files[0].name;
}

function callProgress() {
  const progress = document.getElementById('progress');
  progress.style.display = 'block';
} 

function callUpgradeSkills() {
  console.log('callUpgradeSkills() called');
  displayGPTResults('Upgrade Skills', '/upgradeSkills');
}

function showPopupWithData(skill) {
  // Fetch data from another API based on the clicked skill
  fetch(`/api/skillData?skill=${encodeURIComponent(skill)}`)
      .then(response => {
          if (!response.ok) {
              throw new Error(`Network response was not ok: ${response.statusText}`);
          }
          return response.json();
      })
      .then(data => {
          // Display the data in a popup (you can use a modal library or create your own popup)
          alert(`Data for ${skill}: ${JSON.stringify(data)}`);
      })
      .catch(error => {
          console.error('Error:', error);
      });
}


function callMatchJobs() {
console.log('callMatchJobs() called');
displayGPTResults('Matched Jobs', '/matchedJobs');
}