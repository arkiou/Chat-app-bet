const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
const highlightCards = document.querySelectorAll('.highlight-card');
const fadeInElements = document.querySelectorAll('.fade-in');

if (navToggle && navLinks) {
  navToggle.setAttribute('aria-expanded', 'false');
  navToggle.addEventListener('click', () => {
    const isActive = navToggle.classList.toggle('active');
    navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isActive.toString());
  });

  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if (navLinks.classList.contains('open')) {
        navLinks.classList.remove('open');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  });
}

const observer = new IntersectionObserver(
  entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible', 'active');
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.2 }
);

highlightCards.forEach(card => observer.observe(card));
fadeInElements.forEach(el => observer.observe(el));

document.querySelectorAll('a[href^="tel"]').forEach(link => {
  link.addEventListener('click', () => {
    if (window.gtag) {
      window.gtag('event', 'click', {
        event_category: 'engagement',
        event_label: 'call_cta',
      });
    }
  });
});

document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', event => {
    const button = form.querySelector('button[type="submit"]');
    if (button) {
      button.textContent = 'Αποστολή...';
      setTimeout(() => {
        button.textContent = 'Η Αίτηση Εστάλη!';
        button.disabled = true;
      }, 400);
    }
    event.preventDefault();
  });
});

const yearEl = document.querySelector('[data-year]');
if (yearEl) {
  yearEl.textContent = new Date().getFullYear();
}
