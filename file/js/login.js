function logout() {
    var logoutForm = document.createElement("form");
    logoutForm.setAttribute("method", "post");
    logoutForm.setAttribute("action", '/logout/');
    document.body.appendChild(logoutForm);
    logoutForm.submit();
}