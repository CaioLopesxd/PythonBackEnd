const showMenu = document.querySelector(".showMenu");
const menu = document.querySelector(".menu");

showMenu.addEventListener("click", () => {
  if (menu.style.display === "block") {
    menu.style.display = "none";
  } else {
    menu.style.display = "block";
  }
});

const loginLogout = document.querySelector(".loginLogout");

document.addEventListener("DOMContentLoaded", function () {
  fetch("/check_login_status")
    .then((response) => response.json())
    .then((data) => {
      if (!data.logged_in) {
        loginLogout.innerHTML = "Login";
        loginLogout.style.color = "#00796b";
        return;
      }
      loginLogout.innerHTML = "Logout";
      loginLogout.style.color = "#d32f2f";
    })
    .catch((error) =>
      console.error("Erro ao verificar o status de login:", error)
    );
});

loginLogout.addEventListener("click", function () {
  fetch("/check_login_status")
    .then((response) => response.json())
    .then((data) => {
      if (!data.logged_in) {
        window.location.href = "/login";
        return;
      }
      window.location.href = "/logout";
    });
});

