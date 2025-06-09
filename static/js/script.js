// Global variables
const cart = JSON.parse(localStorage.getItem("cart")) || []

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  updateCartUI()
  setupEventListeners()
})

// Event listeners
function setupEventListeners() {
  // Search functionality
  const searchInput = document.getElementById("searchInput")
  if (searchInput) {
    searchInput.addEventListener("input", debounce(searchProducts, 300))
  }

  // Close modals on escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeModals()
    }
  })
}

// Utility functions
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

function formatPrice(price) {
  return new Intl.NumberFormat("ru-RU").format(price) + " ₽"
}

// Search functionality
function toggleSearch() {
  const searchBar = document.getElementById("searchBar")
  if (searchBar) {
    searchBar.classList.toggle("active")
    if (searchBar.classList.contains("active")) {
      const searchInput = document.getElementById("searchInput")
      if (searchInput) searchInput.focus()
    }
  }
}

function searchProducts() {
  const query = document.getElementById("searchInput").value.toLowerCase()
  if (query.trim() === "") {
    return
  }
  // Redirect to catalog with search query
  window.location.href = `/catalog?search=${encodeURIComponent(query)}`
}

// Cart functionality
function addToCart(productId, quantity = 1) {
  // Send AJAX request to add item to cart
  fetch("/add-to-cart", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: quantity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showMessage("Товар добавлен в корзину", "success")
        updateCartCount(data.cart_count)
      } else {
        showMessage(data.message || "Ошибка при добавлении товара", "error")
      }
    })
    .catch((error) => {
      showMessage("Произошла ошибка", "error")
    })
}

function updateCartQuantity(productId, newQuantity) {
  if (newQuantity < 1) {
    removeFromCart(productId)
    return
  }

  fetch("/update-cart", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: newQuantity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        location.reload()
      } else {
        showMessage(data.message || "Ошибка при обновлении корзины", "error")
      }
    })
    .catch((error) => {
      showMessage("Произошла ошибка", "error")
    })
}

function removeFromCart(productId) {
  if (confirm("Удалить товар из корзины?")) {
    fetch("/remove-from-cart", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({
        product_id: productId,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload()
        } else {
          showMessage(data.message || "Ошибка при удалении товара", "error")
        }
      })
      .catch((error) => {
        showMessage("Произошла ошибка", "error")
      })
  }
}

function updateCartUI() {
  // This function updates the cart count in the header
  // The actual cart items are rendered server-side
}

function updateCartCount(count) {
  const cartCount = document.querySelector(".cart-count")
  if (cartCount) {
    cartCount.textContent = count
  }
}

function toggleCart() {
  const cartSidebar = document.getElementById("cartSidebar")
  const overlay = document.getElementById("overlay")

  if (cartSidebar && overlay) {
    cartSidebar.classList.toggle("active")
    overlay.classList.toggle("active")

    if (cartSidebar.classList.contains("active")) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = "auto"
    }
  }
}

// Modal management
function closeModals() {
  const modals = document.querySelectorAll(".modal")
  const overlay = document.getElementById("overlay")
  const cartSidebar = document.getElementById("cartSidebar")

  modals.forEach((modal) => {
    modal.classList.remove("active")
  })

  if (overlay) overlay.classList.remove("active")
  if (cartSidebar) cartSidebar.classList.remove("active")

  document.body.style.overflow = "auto"
}

// Mobile menu
function toggleMobileMenu() {
  const nav = document.querySelector(".nav");
  if (nav) {
    nav.classList.toggle("mobile-active");
  }
}


// Utility functions
function showMessage(text, type = "info") {
  const message = document.createElement("div")
  message.className = `message ${type}`
  message.innerHTML = `
        ${text}
        <button onclick="this.parentElement.remove()">×</button>
    `

  let flashContainer = document.querySelector(".flash-messages")
  if (!flashContainer) {
    flashContainer = document.createElement("div")
    flashContainer.className = "flash-messages"
    document.body.appendChild(flashContainer)
  }

  flashContainer.appendChild(message)

  setTimeout(() => {
    message.remove()
  }, 5000)
}

function getCSRFToken() {
  const token = document.querySelector("[name=csrf_token]")
  return token ? token.value : ""
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute("href"))
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  })
})

// Auto-hide flash messages
document.addEventListener("DOMContentLoaded", () => {
  const messages = document.querySelectorAll(".message")
  messages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"
      setTimeout(() => {
        message.remove()
      }, 300)
    }, 5000)
  })
})
