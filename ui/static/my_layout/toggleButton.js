// --- TOGGLE BUTTON HANDLING ---
export const toggleStates = {};

export function initializeToggleButtons() {
  document.querySelectorAll('.toggle-btn').forEach(button => {
    const option = button.dataset.option;
    toggleStates[option] = false; // default state

    button.addEventListener('click', () => {
      toggleStates[option] = !toggleStates[option];
      button.classList.toggle('active', toggleStates[option]);
      console.log(`Toggled ${option}: ${toggleStates[option]}`);
    });
  });
}
