function price_filter() {
    let selectedRadio = document.querySelector('input[name="priceRange"]:checked');
    let selectedValue = selectedRadio ? selectedRadio.value : null;
    let url = new URL(window.location.href);
    url.searchParams.set('price_range', selectedValue);
    url.searchParams.delete('page');
    window.location.href = url.href;
}

function updateOrder(){
    let selectedValue = document.getElementById('SortBy').value;
    let url = new URL(window.location.href);
    url.searchParams.set('order', selectedValue);
    url.searchParams.delete('page');
    window.location.href = url.href;
}


