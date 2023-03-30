function typeWriter(elem) {
    const textoArray = elem.innerHTML.split('');
    elem.innerHTML = '';
    textoArray.forEach((letra, i) => {
        setTimeout(() => elem.innerHTML += letra, 75 * i);
    })
}

function atualizarIdade(elem){
    const dataAtual = new Date();
    const dataNascimento = new Date("2002/03/04");
    let idade =  dataAtual.getFullYear() - dataNascimento.getFullYear();
    const mes = dataAtual.getMonth() - dataNascimento.getMonth();

    if(mes<0||(mes===0 && dataAtual.getDate() < dataNascimento.getDate())){
        idade--;
    }
    console.log(idade);

    elem.forEach((elemento)=>{
        elemento.innerHTML = idade;
    })
}

typeWriter(document.querySelector('.textoAnimacao'));
atualizarIdade(document.querySelectorAll('.idade'));
