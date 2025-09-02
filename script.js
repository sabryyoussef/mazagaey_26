// Portfolio Interactive Features
document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scrolling for internal links
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

    // Animate stats on scroll
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -50px 0px'
    };

    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats(entry.target);
            }
        });
    }, observerOptions);

    // Observe all stat cards
    document.querySelectorAll('.stat-card, .github-stat').forEach(card => {
        statsObserver.observe(card);
    });

    // Animate timeline items
    const timelineObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateX(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.timeline-item').forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-50px)';
        item.style.transition = `opacity 0.6s ease ${index * 0.2}s, transform 0.6s ease ${index * 0.2}s`;
        timelineObserver.observe(item);
    });

    // Animate cards on scroll
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.expertise-card, .portfolio-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        cardObserver.observe(card);
    });

    // Add interactive hover effects
    addHoverEffects();
    
    // Add typing effect to hero title
    addTypingEffect();
    
    // Add particle background effect
    createParticleBackground();
    
    // Initialize repository table
    initializeRepositoryTable();
});

function animateStats(element) {
    const statNumber = element.querySelector('.stat-number, .stat-value');
    if (!statNumber || statNumber.dataset.animated) return;
    
    const finalValue = statNumber.textContent;
    const numericValue = parseInt(finalValue.replace(/\D/g, ''));
    
    if (isNaN(numericValue)) return;
    
    statNumber.dataset.animated = 'true';
    let currentValue = 0;
    const increment = numericValue / 50;
    const suffix = finalValue.replace(/\d/g, '');
    
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= numericValue) {
            statNumber.textContent = finalValue;
            clearInterval(timer);
        } else {
            statNumber.textContent = Math.floor(currentValue) + suffix;
        }
    }, 30);
}

function addHoverEffects() {
    // Add ripple effect to buttons
    document.querySelectorAll('.contact-link, .repository-link').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add tech tag hover effects
    document.querySelectorAll('.tech-tag').forEach(tag => {
        tag.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.boxShadow = '0 5px 15px rgba(102, 126, 234, 0.3)';
        });
        
        tag.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        });
    });
}

function addTypingEffect() {
    const heroTitle = document.querySelector('.hero-title');
    if (!heroTitle) return;
    
    const originalText = heroTitle.textContent;
    heroTitle.textContent = '';
    
    let i = 0;
    const typeTimer = setInterval(() => {
        heroTitle.textContent += originalText.charAt(i);
        i++;
        if (i >= originalText.length) {
            clearInterval(typeTimer);
            // Add cursor blink effect
            const cursor = document.createElement('span');
            cursor.textContent = '|';
            cursor.style.animation = 'blink 1s infinite';
            heroTitle.appendChild(cursor);
            
            setTimeout(() => {
                cursor.remove();
            }, 3000);
        }
    }, 100);
}

function createParticleBackground() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.1';
    
    document.body.appendChild(canvas);
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const particles = [];
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 3 + 1
        });
    }
    
    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
            
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = '#667eea';
            ctx.fill();
        });
        
        requestAnimationFrame(animateParticles);
    }
    
    animateParticles();
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .tech-tag {
        transition: all 0.3s ease;
    }
    
    .portfolio-card:hover .project-type {
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);

// Add scroll progress indicator
function addScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.style.position = 'fixed';
    progressBar.style.top = '0';
    progressBar.style.left = '0';
    progressBar.style.width = '0%';
    progressBar.style.height = '3px';
    progressBar.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    progressBar.style.zIndex = '1000';
    progressBar.style.transition = 'width 0.3s ease';
    
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', () => {
        const scrollTop = document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / scrollHeight) * 100;
        
        progressBar.style.width = scrollPercent + '%';
    });
}

addScrollProgress();

// Repository Table Functionality
function initializeRepositoryTable() {
    if (typeof repositoryData === 'undefined') {
        console.log('Repository data not loaded yet');
        return;
    }
    
    populateRepositoryTable();
    setupTableInteractions();
}

function populateRepositoryTable() {
    const tbody = document.getElementById('repositories-tbody');
    if (!tbody) return;
    
    const repositories = Object.values(repositoryData);
    
    tbody.innerHTML = repositories.map(repo => {
        const totalModules = Object.values(repo.branches).reduce((sum, branch) => sum + branch.modules, 0);
        const totalFiles = Object.values(repo.branches).reduce((sum, branch) => sum + branch.files, 0);
        const totalLines = Object.values(repo.branches).reduce((sum, branch) => sum + branch.lines, 0);
        
        // Determine repository type
        let repoType = 'public';
        let repoTypeClass = 'public';
        
        if (repo.name.includes('private') || repo.name.includes('mazagawy') || repo.name.includes('ian2')) {
            repoType = 'Private';
            repoTypeClass = 'private';
        } else if (totalModules > 30 || totalLines > 1000000) {
            repoType = 'Enterprise';
            repoTypeClass = 'enterprise';
        } else {
            repoType = 'Public';
            repoTypeClass = 'public';
        }
        
        const displayName = repo.name.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
        const formattedLines = totalLines > 1000000 ? 
            (totalLines / 1000000).toFixed(1) + 'M' : 
            totalLines > 1000 ? 
            (totalLines / 1000).toFixed(0) + 'K' : 
            totalLines.toString();
        
        return `
            <tr data-repo="${repo.name}" data-type="${repoTypeClass}">
                <td>
                    <div class="repo-name">
                        ${displayName}
                        <span class="repo-type-badge ${repoTypeClass}">${repoType}</span>
                    </div>
                </td>
                <td>
                    <span class="branch-count">${repo.total_branches}</span>
                </td>
                <td>
                    <span class="metric-value ${totalModules > 30 ? 'metric-large' : ''}">${totalModules}</span>
                </td>
                <td>
                    <span class="metric-value">${totalFiles.toLocaleString()}</span>
                </td>
                <td>
                    <span class="metric-value ${totalLines > 1000000 ? 'metric-large' : ''}">${formattedLines}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="action-btn view" onclick="showRepositoryDetails('${repo.name}')">
                            <i class="fas fa-eye"></i>
                            Details
                        </button>
                        ${repo.url ? `
                        <a href="${repo.url}" target="_blank" class="action-btn github">
                            <i class="fab fa-github"></i>
                            GitHub
                        </a>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function setupTableInteractions() {
    // Search functionality
    const searchInput = document.getElementById('repo-search');
    if (searchInput) {
        searchInput.addEventListener('input', filterRepositories);
    }
    
    // Filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterRepositories();
        });
    });
    
    // Sortable columns
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortBy = this.dataset.sort;
            sortTable(sortBy);
        });
    });
    
    // Modal functionality
    setupModal();
}

function filterRepositories() {
    const searchTerm = document.getElementById('repo-search').value.toLowerCase();
    const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
    const rows = document.querySelectorAll('#repositories-tbody tr');
    
    rows.forEach(row => {
        const repoName = row.querySelector('.repo-name').textContent.toLowerCase();
        const repoType = row.dataset.type;
        
        const matchesSearch = repoName.includes(searchTerm);
        const matchesFilter = activeFilter === 'all' || repoType === activeFilter;
        
        row.style.display = matchesSearch && matchesFilter ? '' : 'none';
    });
}

function sortTable(sortBy) {
    const tbody = document.getElementById('repositories-tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
            case 'name':
                aValue = a.querySelector('.repo-name').textContent.toLowerCase();
                bValue = b.querySelector('.repo-name').textContent.toLowerCase();
                return aValue.localeCompare(bValue);
            
            case 'branches':
                aValue = parseInt(a.querySelector('.branch-count').textContent);
                bValue = parseInt(b.querySelector('.branch-count').textContent);
                return bValue - aValue;
            
            case 'modules':
            case 'files':
            case 'lines':
                const colIndex = ['name', 'branches', 'modules', 'files', 'lines'].indexOf(sortBy);
                aValue = a.cells[colIndex].textContent.replace(/[^\d.]/g, '');
                bValue = b.cells[colIndex].textContent.replace(/[^\d.]/g, '');
                
                // Handle M and K suffixes
                if (a.cells[colIndex].textContent.includes('M')) aValue *= 1000000;
                if (a.cells[colIndex].textContent.includes('K')) aValue *= 1000;
                if (b.cells[colIndex].textContent.includes('M')) bValue *= 1000000;
                if (b.cells[colIndex].textContent.includes('K')) bValue *= 1000;
                
                return parseFloat(bValue) - parseFloat(aValue);
        }
    });
    
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

function showRepositoryDetails(repoName) {
    const repo = repositoryData[repoName];
    if (!repo) return;
    
    const modal = document.getElementById('repo-modal');
    const modalTitle = document.getElementById('modal-repo-name');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.textContent = repoName.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
    
    const branchesHtml = Object.entries(repo.branches).map(([branchName, branchData]) => `
        <div class="branch-card">
            <div class="branch-header">
                <div class="branch-name">${branchName}</div>
                <div class="branch-stats">
                    <span>📦 ${branchData.modules} modules</span>
                    <span>📄 ${branchData.files.toLocaleString()} files</span>
                    <span>📝 ${branchData.lines.toLocaleString()} lines</span>
                </div>
            </div>
            ${branchData.top_modules.length > 0 ? `
            <div class="branch-modules">
                <h4>Key Modules:</h4>
                <div class="module-tags">
                    ${branchData.top_modules.map(module => `
                        <span class="module-tag">${module}</span>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `).join('');
    
    modalBody.innerHTML = `
        <div class="branch-details">
            ${branchesHtml}
        </div>
    `;
    
    modal.style.display = 'block';
}

function setupModal() {
    const modal = document.getElementById('repo-modal');
    const closeBtn = modal.querySelector('.close');
    
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}
