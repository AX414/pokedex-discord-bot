function typeWriter(elem) {
    const textoArray = elem.innerHTML.split('');
    elem.innerHTML = '';
    textoArray.forEach((letra, i) => {
        setTimeout(() => elem.innerHTML += letra, 75 * i);
    })
}

typeWriter(document.querySelector('.textoAnimacao'));