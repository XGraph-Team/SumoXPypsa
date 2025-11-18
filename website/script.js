/**
 * Manhattan Co-Simulation Website
 * Interactive JavaScript
 */

// ============================================
// Navbar Scroll Effect
// ============================================
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ============================================
// Mobile Navigation Toggle
// ============================================
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a link
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// ============================================
// Smooth Scroll for Navigation Links
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');

        // Skip if it's just "#" or external link
        if (href === '#' || href.startsWith('http')) {
            return;
        }

        e.preventDefault();

        const targetId = href.substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            const navbarHeight = document.getElementById('navbar').offsetHeight;
            const targetPosition = targetElement.offsetTop - navbarHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ============================================
// Back to Top Button
// ============================================
const backToTopButton = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    if (window.scrollY > 500) {
        backToTopButton.classList.add('visible');
    } else {
        backToTopButton.classList.remove('visible');
    }
});

backToTopButton.addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// ============================================
// Intersection Observer for Animations
// ============================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for fade-in animation
const animateElements = document.querySelectorAll(`
    .overview-card,
    .feature-card,
    .demo-card,
    .publication-card,
    .arch-layer
`);

animateElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// ============================================
// Active Navigation Link Highlight
// ============================================
const sections = document.querySelectorAll('section[id]');

window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const navbarHeight = document.getElementById('navbar').offsetHeight;

    sections.forEach(section => {
        const sectionTop = section.offsetTop - navbarHeight - 100;
        const sectionBottom = sectionTop + section.offsetHeight;
        const sectionId = section.getAttribute('id');

        if (scrollY >= sectionTop && scrollY < sectionBottom) {
            // Remove active class from all links
            navLinks.forEach(link => {
                link.classList.remove('active');
            });

            // Add active class to current section link
            const activeLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
    });
});

// ============================================
// Video Lazy Loading
// ============================================
const videos = document.querySelectorAll('iframe[src*="youtube"]');

const videoObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const iframe = entry.target;
            // Video will load when it comes into view
            videoObserver.unobserve(iframe);
        }
    });
}, {
    rootMargin: '200px'
});

videos.forEach(video => {
    videoObserver.observe(video);
});

// ============================================
// Dynamic Copyright Year
// ============================================
const updateCopyrightYear = () => {
    const yearElements = document.querySelectorAll('.copyright-year');
    const currentYear = new Date().getFullYear();
    yearElements.forEach(el => {
        el.textContent = currentYear;
    });
};

updateCopyrightYear();

// ============================================
// Stats Counter Animation
// ============================================
const animateCounter = (element, target, duration = 2000) => {
    let current = 0;
    const increment = target / (duration / 16);
    const isNumber = !isNaN(target);

    const updateCounter = () => {
        current += increment;
        if (current < target) {
            if (isNumber) {
                element.textContent = Math.floor(current).toLocaleString();
            }
            requestAnimationFrame(updateCounter);
        } else {
            if (isNumber) {
                element.textContent = target.toLocaleString();
            } else {
                element.textContent = target;
            }
        }
    };

    updateCounter();
};

// Animate stats when they come into view
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statValue = entry.target;
            const targetText = statValue.textContent.trim();

            // Only animate if it's a number
            const targetNumber = parseInt(targetText.replace(/[^0-9]/g, ''));
            if (!isNaN(targetNumber) && targetNumber > 0) {
                statValue.textContent = '0';
                animateCounter(statValue, targetNumber);
            }

            statsObserver.unobserve(statValue);
        }
    });
}, {
    threshold: 0.5
});

const statValues = document.querySelectorAll('.stat-value');
statValues.forEach(stat => {
    statsObserver.observe(stat);
});

// ============================================
// Scroll Progress Indicator (Optional)
// ============================================
const createScrollProgress = () => {
    const progressBar = document.createElement('div');
    progressBar.id = 'scroll-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        width: 0%;
        z-index: 9999;
        transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (window.scrollY / windowHeight) * 100;
        progressBar.style.width = `${scrolled}%`;
    });
};

createScrollProgress();

// ============================================
// Copy Code Button (for code blocks)
// ============================================
const addCopyButtons = () => {
    const codeBlocks = document.querySelectorAll('code');

    codeBlocks.forEach(block => {
        // Skip inline code
        if (block.textContent.length < 50) return;

        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';

        const button = document.createElement('button');
        button.textContent = 'Copy';
        button.className = 'copy-code-btn';
        button.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.25rem 0.75rem;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 0.375rem;
            cursor: pointer;
            font-size: 0.75rem;
            font-weight: 600;
            opacity: 0;
            transition: opacity 0.2s ease;
        `;

        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);
        wrapper.appendChild(button);

        wrapper.addEventListener('mouseenter', () => {
            button.style.opacity = '1';
        });

        wrapper.addEventListener('mouseleave', () => {
            button.style.opacity = '0';
        });

        button.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(block.textContent);
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
};

addCopyButtons();

// ============================================
// External Links - Open in New Tab
// ============================================
const externalLinks = document.querySelectorAll('a[href^="http"]');
externalLinks.forEach(link => {
    if (!link.hasAttribute('target')) {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    }
});

// ============================================
// Keyboard Navigation
// ============================================
document.addEventListener('keydown', (e) => {
    // Press 'h' to go home
    if (e.key === 'h' && !e.ctrlKey && !e.metaKey) {
        const target = document.querySelector('a[href="#home"]');
        if (target && !isInputFocused()) {
            target.click();
        }
    }

    // Press 't' to scroll to top
    if (e.key === 't' && !e.ctrlKey && !e.metaKey) {
        if (!isInputFocused()) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }
});

function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement.tagName === 'INPUT' ||
           activeElement.tagName === 'TEXTAREA' ||
           activeElement.isContentEditable;
}

// ============================================
// Performance Monitoring (Optional)
// ============================================
if ('PerformanceObserver' in window) {
    const perfObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.loadTime > 3000) {
                console.warn(`Slow resource: ${entry.name} took ${entry.loadTime}ms`);
            }
        }
    });

    perfObserver.observe({ entryTypes: ['resource'] });
}

// ============================================
// Accessibility: Skip to Main Content
// ============================================
const createSkipLink = () => {
    const skipLink = document.createElement('a');
    skipLink.href = '#overview';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 0;
        background: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        text-decoration: none;
        z-index: 10000;
        transition: top 0.2s ease;
    `;

    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
    });

    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });

    document.body.insertBefore(skipLink, document.body.firstChild);
};

createSkipLink();

// ============================================
// Console Easter Egg
// ============================================
console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║    Manhattan Power Grid Co-Simulation Platform           ║
║                                                           ║
║    Interested in the code? Check out our GitHub:         ║
║    github.com/YOUR_USERNAME/YOUR_REPO                     ║
║                                                           ║
║    WebConf 2026 Demo Track                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
`);

// ============================================
// Initialize on DOM Ready
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Manhattan Co-Simulation website loaded successfully!');

    // Add any additional initialization here
    // For example, analytics tracking, third-party integrations, etc.
});

// ============================================
// Service Worker Registration (Optional - for PWA)
// ============================================
if ('serviceWorker' in navigator) {
    // Uncomment to enable service worker for offline support
    /*
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
    */
}
