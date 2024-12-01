
// Auto Srroll Transition
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    const header = document.querySelector('.header');
    const sticky = header.offsetHeight; // Height at which navbar sticks

    if (window.scrollY > sticky) {
        navbar.classList.add('sticky'); // Add sticky class
    } else {
        navbar.classList.remove('sticky'); // Remove sticky class
    }
});

// Fixed Navbar 
document.querySelectorAll('.navbar a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});
