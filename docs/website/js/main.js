// Main JavaScript for PlainSpeak Contest Website

document.addEventListener('DOMContentLoaded', function() {
    // Form handling
    const registerForm = document.querySelector('.register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const submitButton = registerForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.textContent = 'Submitting...';

            try {
                const formData = new FormData(registerForm);
                const data = Object.fromEntries(formData.entries());

                const response = await fetch('/api/contest/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error('Registration failed');
                }

                const result = await response.json();
                
                // Show success message
                const successMessage = document.createElement('div');
                successMessage.className = 'alert success';
                successMessage.textContent = 'Registration successful! Check your email for confirmation.';
                registerForm.insertBefore(successMessage, registerForm.firstChild);
                
                // Reset form
                registerForm.reset();

            } catch (error) {
                // Show error message
                const errorMessage = document.createElement('div');
                errorMessage.className = 'alert error';
                errorMessage.textContent = 'Registration failed. Please try again.';
                registerForm.insertBefore(errorMessage, registerForm.firstChild);
                
                console.error('Registration error:', error);
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Register Now';
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // Intersection Observer for animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements that should animate on scroll
    document.querySelectorAll('.category-card, .prize-card, .resource-card').forEach(
        el => observer.observe(el)
    );

    // Countdown timer for registration deadline
    function updateCountdown() {
        const deadline = new Date('2025-05-31T23:59:59').getTime();
        const now = new Date().getTime();
        const distance = deadline - now;

        if (distance > 0) {
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));

            const countdownEl = document.querySelector('.countdown');
            if (countdownEl) {
                countdownEl.textContent = `Registration closes in: ${days}d ${hours}h ${minutes}m`;
            }
        }
    }

    // Update countdown every minute
    updateCountdown();
    setInterval(updateCountdown, 60000);

    // Form validation
    function validateForm() {
        const inputs = registerForm.querySelectorAll('input, textarea, select');
        let isValid = true;

        inputs.forEach(input => {
            if (input.hasAttribute('required') && !input.value.trim()) {
                isValid = false;
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }

            if (input.type === 'email' && input.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value)) {
                    isValid = false;
                    input.classList.add('error');
                }
            }
        });

        return isValid;
    }

    // Add real-time validation
    if (registerForm) {
        registerForm.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.classList.add('error');
                } else {
                    this.classList.remove('error');
                }
            });
        });
    }

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav ul');
    
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', () => {
            nav.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
});

// Add CSS class when scrolled
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});
