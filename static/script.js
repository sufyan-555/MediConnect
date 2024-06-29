// Mobile navbar
const btn=document.getElementById('menu-btn')
const nav=document.getElementById('menu')

btn.addEventListener('click',()=>
{
    btn.classList.toggle('open')
    nav.classList.toggle('flex')
    nav.classList.toggle('hidden')
})


// Javascript for FAQ section

const dtElements=document.querySelectorAll('dt')
dtElements.forEach(element=>{
    element.addEventListener('click',()=>
    {
        const ddId=element.getAttribute('aria-controls');
        const ddElement=document.getElementById(ddId);
        const ddArrowIcon=element.querySelectorAll('i')[0];


        ddElement.classList.toggle('hidden');
        ddArrowIcon.classList.toggle('-rotate-180');
    })
})

