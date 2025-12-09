const connectWalletBtn = document.getElementById('connectWalletBtn');
const walletPopup = document.getElementById('walletPopup');
const closePopupBtn = document.getElementById('closePopupBtn');

connectWalletBtn.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent default anchor behavior
    walletPopup.style.display = 'flex';
});

closePopupBtn.addEventListener('click', () => {
    walletPopup.style.display = 'none';
});

// Close popup when clicking on the overlay
walletPopup.addEventListener('click', (e) => {
    if (e.target === walletPopup) {
        walletPopup.style.display = 'none';
    }
});