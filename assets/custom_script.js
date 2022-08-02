
document.addEventListener('keydown', (e) => {
    e = e || window.event;
    if ((e.keyCode == 116)){
        e.preventDefault();
        alert("Nút F5 đã bị vô hiệu hoá!")
    }
});