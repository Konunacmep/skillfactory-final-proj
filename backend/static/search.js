let style = document.createElement('style');
style.type = 'text/css';
style.innerHTML = '.hidden-li { display: none; } .search-input { display: block; }';
document.getElementsByTagName('head')[0].appendChild(style);

document.addEventListener('DOMContentLoaded', function() {
    const widget = document.querySelector('.related-widget-wrapper')
    const search = document.createElement("input")
    search.type = "text"
    search.className = "search-input" // set the CSS class
    search.placeholder = "Search"
    widget.insertBefore(search, widget.firstChild) // put it into the DOM

    search.addEventListener('input', function() {
        widget.querySelector('ul').querySelectorAll('li').forEach(element => {
            
            if (!element.querySelector('label').innerText.toLowerCase().includes(search.value.toLowerCase())) {
                element.classList.add('hidden-li')
                // console.log('aaaaa')
            } else {
                element.classList.remove('hidden-li')
            }
        });
    })
})
