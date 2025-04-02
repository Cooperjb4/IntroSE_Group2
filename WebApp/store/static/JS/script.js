// Add a single event listener to handle all navigation buttons
document.querySelectorAll('.nav-button').forEach(button => {
    button.addEventListener('click', function() {
      window.location.href = this.getAttribute('data-url');
    });
  });

// Determine which page we're on and set up the appropriate event listeners
const currentPage = window.location.pathname.split("/").pop();

if (currentPage === "/" || currentPage === "") {
    
}

else if (currentPage === "signup.html") {} 

else if (currentPage === "login.html") {
}

else if (currentPage === "home.html") {
    const searchForm = document.querySelector("form");
    if (searchForm) {
        searchForm.addEventListener("submit", function(event) {
            event.preventDefault();
            window.location.href = "home.html";
        });
    }
} 

else if (currentPage === "cart.html") {} 

else if (currentPage === "checkout.html") {} 

else if (currentPage === "checkoutDetails.html") {} 

else if (currentPage === "account.html") {} 