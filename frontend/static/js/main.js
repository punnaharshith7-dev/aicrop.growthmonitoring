/**
 * AI Crop Growth Monitoring — SaaS Client Script
 */

document.addEventListener('DOMContentLoaded', () => {
  // ── Sidebar Toggle for Mobile ──────────────────────────────
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const toggleBtn = document.getElementById('sidebarToggle');

  if (toggleBtn && sidebar && overlay) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
      overlay.classList.toggle('show');
    });

    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  // ── Notification Dropdown Toggle ───────────────────────────
  const notifBtn = document.getElementById('notifToggleBtn');
  const notifDropdown = document.getElementById('notifDropdown');

  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Close user menu if open
      const userMenu = document.getElementById('userMenuDropdown');
      if (userMenu) userMenu.classList.remove('show');

      notifDropdown.classList.toggle('show');
    });
  }

  // ── User Profile Dropdown Toggle ────────────────────────────
  const userBtn = document.getElementById('userMenuBtn');
  const userMenu = document.getElementById('userMenuDropdown');

  if (userBtn && userMenu) {
    userBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Close notification menu if open
      if (notifDropdown) notifDropdown.classList.remove('show');

      userMenu.classList.toggle('show');
    });
  }

  // Close dropdowns on outside click
  document.addEventListener('click', (e) => {
    if (notifDropdown && !notifDropdown.contains(e.target) && e.target !== notifBtn) {
      notifDropdown.classList.remove('show');
    }
    if (userMenu && !userMenu.contains(e.target) && e.target !== userBtn) {
      userMenu.classList.remove('show');
    }
  });

  // ── AJAX Mark Recommendation as Read ────────────────────────
  document.querySelectorAll('.btn-mark-read').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const recId = btn.getAttribute('data-rec-id');
      if (!recId) return;

      try {
        const res = await fetch(`/recommendations/mark-read/${recId}`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (res.ok) {
          // Remove notification item or mark item in place
          const item = btn.closest('.dropdown-item-notification') || btn.closest('.rec-card');
          if (item) {
            item.style.transition = 'all 0.3s ease';
            item.style.opacity = '0';
            item.style.transform = 'translateX(20px)';
            setTimeout(() => {
              item.remove();
              // Update badge count
              const badge = document.querySelector('.btn-badge');
              if (badge) {
                let count = parseInt(badge.textContent.trim()) || 0;
                if (count > 1) {
                  badge.textContent = count - 1;
                } else {
                  badge.remove();
                }
              }
            }, 300);
          }
        }
      } catch (err) {
        console.error('Failed to mark recommendation as read:', err);
      }
    });
  });

  // ── Chart.js Global Theme Defaults ──────────────────────────
  if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
    Chart.defaults.color = '#64748b';
    Chart.defaults.scale.grid.color = 'rgba(226, 232, 240, 0.6)';
    Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';
    Chart.defaults.plugins.tooltip.titleFont = { family: "'Plus Jakarta Sans', sans-serif", weight: 'bold' };
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
  }
});

