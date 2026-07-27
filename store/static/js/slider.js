// Add this to your custom JS file or script block

// ===== PAUSE ON HOVER =====
document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('medicalSlider');
    if (slider) {
        // Pause on hover
        slider.addEventListener('mouseenter', function() {
            const carousel = bootstrap.Carousel.getInstance(this);
            if (carousel) carousel.pause();
        });
        
        slider.addEventListener('mouseleave', function() {
            const carousel = bootstrap.Carousel.getInstance(this);
            if (carousel) carousel.cycle();
        });
    }

    // ===== PARALLAX EFFECT =====
    const slides = document.querySelectorAll('.medical-slide-bg');
    if (slides.length > 0) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            slides.forEach(function(slide, index) {
                const offset = scrolled * 0.3;
                slide.style.transform = 'translateY(' + offset + 'px)';
            });
        });
    }
});

// ===== COUNTER ANIMATION FOR STATS =====
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    
    const timer = setInterval(function() {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString();
    }, 16);
}

// ===== SMOOTH SCROLL TO SECTIONS =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});