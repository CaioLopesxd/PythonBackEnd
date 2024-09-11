document.querySelectorAll(".delete").forEach((button) => {
  button.addEventListener("click", function () {
    const postId = this.getAttribute("data-id");
    fetch("/delete_post", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        id: postId,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload();
        } else {
          alert("Erro ao deletar o post.");
        }
      });
  });
});
