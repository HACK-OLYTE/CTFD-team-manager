/**
 * ctfd-team-manager — disband_redirect.js
 * Intercepts clicks on .disband-team (the theme's "Disband Team" button)
 * and redirects to /teams/leave instead of opening the modal popup.
 * Uses capture:true to execute before Alpine.js.
 */
document.addEventListener('click', function (e) {
    var btn = e.target.closest('.disband-team');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    window.location.href = '/teams/leave';
}, true);
