function getProducts() {
    const data = localStorage.getItem('products');
    return data ? JSON.parse(data) : [];
}

function addProduct(product) {
    const products = getProducts();
    products.push(product);
    localStorage.setItem('products', JSON.stringify(products));
}

function updateProduct(id, updatedProduct) {
    const products = getProducts();
    const index = products.findIndex(p => p.product_id === id);
    if (index !== -1) {
        products[index] = updatedProduct;
        localStorage.setItem('products', JSON.stringify(products));
    }
}

function getLocations() {
    const data = localStorage.getItem('locations');
    return data ? JSON.parse(data) : [];
}

function addLocation(location) {
    const locations = getLocations();
    locations.push(location);
    localStorage.setItem('locations', JSON.stringify(locations));
}

function updateLocation(id, updatedLocation) {
    const locations = getLocations();
    const index = locations.findIndex(l => l.location_id === id);
    if (index !== -1) {
        locations[index] = updatedLocation;
        localStorage.setItem('locations', JSON.stringify(locations));
    }
}

function getMovements() {
    const data = localStorage.getItem('movements');
    return data ? JSON.parse(data) : [];
}

function addMovement(movement) {
    const movements = getMovements();
    movements.push(movement);
    localStorage.setItem('movements', JSON.stringify(movements));
}
