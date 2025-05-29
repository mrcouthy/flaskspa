document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const initialToggleButtonLeft = '260px'; // As per CSS
    const collapsedToggleButtonLeft = '10px'; // Desired position when collapsed

    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('sidebar-collapsed');

            // Adjust button position
            if (sidebar.classList.contains('collapsed')) {
                sidebarToggle.style.left = collapsedToggleButtonLeft;
            } else {
                sidebarToggle.style.left = initialToggleButtonLeft;
            }
        });
    }
});
