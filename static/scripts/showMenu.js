const showMenu = document.querySelector(".showMenu");
const menu = document.querySelector(".menu");

showMenu.addEventListener("click", () => {
  if (menu.style.display === "block") {
    menu.style.display = "none";
  } else {
    menu.style.display = "block";
  }
});
